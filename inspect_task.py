"""CLAIMS-Bench L3 as an Inspect (`inspect_ai`) task.

Replaces the hand-rolled provider layer in `run_eval.py` / `run_eval_v2.py`
(serial loop, no retries, no rate-limit backoff, manual `--est-usd` accounting)
with Inspect's model layer: concurrency (`--max-connections`), retries, token
accounting in the eval log, `inspect view`, and `--epochs N` for replicates.

**Deliberately NOT moved into Inspect:** cross-sample aggregation. Bradley-Terry
fitting, Borda profile means, bootstrap CIs / permutation tests
(`src/v2/significance.py`), consistency reports, and human-panel distance all
pool information *across* samples and models; Inspect's metric protocol is
`list[SampleScore] -> float`, so those stay in the existing scripts. This task
produces per-sample scores in exactly the legacy shape, and
`scripts/eval_log_to_jsonl.py` exports an `.eval` log back to the
`responses.jsonl` / `scored.jsonl` files every downstream script already reads.

Prompt assembly is imported from `run_eval_v2.build_messages_v2`, not
reimplemented, so the prompt a model sees here is byte-identical to the legacy
pipeline. `tests/test_inspect_prompt_parity.py` asserts that for all 80 items.

Usage
-----
    # generate + score, 10 replicates, 12-way concurrency
    inspect eval inspect_task.py --model openai/gpt-4o \
        --epochs 10 --max-connections 12 \
        -T subset=structured

    # with the failure-mode / implicit LLM judge
    inspect eval inspect_task.py --model anthropic/claude-sonnet-4-6 \
        -T judge_model=gpt-4o -T subset=implicit

    # export back to the legacy jsonl shape
    python scripts/eval_log_to_jsonl.py --log logs/<run>.eval --out-dir outputs/my_run
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Literal

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import ChatMessageSystem, ChatMessageUser, GenerateConfig
from inspect_ai.scorer import Score, Scorer, Target, mean, scorer, stderr
from inspect_ai.solver import TaskState, generate

from run_eval_v2 import build_messages_v2
from src.io import load_jsonl
from src.providers import (
    PROVIDER_FILTERED_PREFIX,
    content_filter_categories,
    is_content_filter_error,
    looks_like_filter_response,
)
from src.v2.failure_modes import merge_failure_mode_score, run_failure_mode_judge
from src.v2.implicit_judge import merge_implicit_score, run_implicit_judge
from src.v2.item_utils import is_implicit_item, is_structured_item
from src.v2.revelation_parse import extract_reasoning, load_schema, parse_response
from src.v2.schwartz_profile import (
    SCHWARTZ_VALUES,
    extract_pairwise_comparisons,
    infer_full_profile,
    pairwise_summary,
)

logger = logging.getLogger(__name__)

DEFAULT_DATA = Path("data/v2_revelation.jsonl")
Subset = Literal["all", "structured", "implicit"]


# --------------------------------------------------------------------------- #
# dataset
# --------------------------------------------------------------------------- #


def record_to_sample(item: dict) -> Sample:
    """One benchmark item -> one Inspect sample.

    The chat messages come from `build_messages_v2()` so the wire prompt matches
    the legacy pipeline exactly; the raw item rides along in metadata because the
    scorer needs its `pole_a`/`pole_b` annotations and rubric notes.
    """
    messages: list[Any] = []
    for m in build_messages_v2(item):
        if m["role"] == "system":
            messages.append(ChatMessageSystem(content=m["content"]))
        else:
            messages.append(ChatMessageUser(content=m["content"]))

    return Sample(
        input=messages,
        id=item["id"],
        metadata={
            "item": item,
            "layer": item.get("layer"),
            "domain": item.get("domain"),
            "elicitation_type": item.get("elicitation_type"),
            "implicit": is_implicit_item(item),
        },
    )


def load_items(data: Path | str, subset: Subset) -> list[dict]:
    items = load_jsonl(data)
    if subset == "structured":
        items = [i for i in items if is_structured_item(i)]
    elif subset == "implicit":
        items = [i for i in items if is_implicit_item(i)]
    elif subset != "all":
        raise ValueError(f"unknown subset {subset!r} (all|structured|implicit)")
    return items


# --------------------------------------------------------------------------- #
# scorer
# --------------------------------------------------------------------------- #


def _empty_profile() -> dict[str, float]:
    return {v: 0.0 for v in SCHWARTZ_VALUES}


def _as_score_value(profile: dict[str, float]) -> dict[str, float]:
    """Inspect Score values must cover the same keys on every sample, or the
    per-dimension metrics go ragged. Always emit all 10."""
    full = _empty_profile()
    full.update({k: float(v) for k, v in (profile or {}).items() if k in full})
    return full


@scorer(metrics={v: [mean(), stderr()] for v in SCHWARTZ_VALUES})
def revelation_scorer(
    judge_model: str | None = None,
    judge_backend: str = "auto",
) -> Scorer:
    """Per-sample scoring, delegating to the existing v2 scoring modules.

    Structured items: parse the fenced JSON -> Borda profile + BT comparisons,
    then (optionally) the failure-mode judge on the free reasoning.
    Implicit items: the whole profile comes from the implicit salience judge, so
    without `judge_model` they score as an empty profile — same as the legacy
    scorer.

    `Score.metadata` carries the full legacy scored row so
    `scripts/eval_log_to_jsonl.py` can round-trip it without recomputation.
    """
    schema = load_schema()

    resolved_backend = judge_backend
    if resolved_backend == "auto" and judge_model:
        resolved_backend = "anthropic" if judge_model.startswith("claude") else "openai"

    async def score(state: TaskState, target: Target) -> Score:
        item = state.metadata["item"]
        response = state.output.completion or ""

        if response.strip().startswith(PROVIDER_FILTERED_PREFIX) or looks_like_filter_response(response):
            return Score(
                value=_as_score_value({}),
                answer="provider_filtered",
                metadata={"scored": {"parse_status": "provider_filtered",
                                     "schwartz_profile": {}, "pairwise": {},
                                     "bt_comparisons": [], "epistemic_prior": None,
                                     "reasoning_text": response, "structured_raw": {}}},
            )

        if is_implicit_item(item):
            row: dict[str, Any] = {
                "parse_status": "implicit",
                "schwartz_profile": {},
                "schwartz_salience_raw": {},
                "pairwise": {},
                "bt_comparisons": [],
                "epistemic_prior": None,
                "reasoning_text": response.strip(),
                "structured_raw": {},
            }
            if judge_model:
                try:
                    # Judge clients are sync; keep them off the event loop so
                    # Inspect's concurrency still applies to the judge calls.
                    judge_out = await asyncio.to_thread(
                        run_implicit_judge, resolved_backend, judge_model, item, response
                    )
                    row.update(merge_implicit_score(item, judge_out))
                except Exception as e:  # judge failure must not kill the sample
                    logger.warning("implicit judge failed on %s: %s", item["id"], e)
                    row["judge_error"] = str(e)
                    if is_content_filter_error(e):
                        row["judge_error_kind"] = "provider_content_filter"
                        row["judge_filter_categories"] = content_filter_categories(e)
        else:
            structured = parse_response(response, schema)
            parse_status = structured.get("_parse_status", "ok")
            ok = parse_status == "ok"
            row = {
                "parse_status": parse_status,
                "schwartz_profile": infer_full_profile(structured) if ok else {},
                "pairwise": pairwise_summary(structured) if ok else {},
                "bt_comparisons": extract_pairwise_comparisons(item, structured) if ok else [],
                "epistemic_prior": structured.get("epistemic_prior") if ok else None,
                "reasoning_text": extract_reasoning(response),
                "structured_raw": {
                    k: v for k, v in structured.items() if not k.startswith("_")
                },
            }
            if judge_model and parse_status != "non_compliant_format":
                try:
                    judge_out = await asyncio.to_thread(
                        run_failure_mode_judge,
                        resolved_backend,
                        judge_model,
                        item,
                        row["reasoning_text"],
                        row["structured_raw"],
                    )
                    row.update(
                        merge_failure_mode_score(
                            item, judge_out, row["structured_raw"], row["reasoning_text"]
                        )
                    )
                except Exception as e:
                    logger.warning("failure-mode judge failed on %s: %s", item["id"], e)
                    row["judge_error"] = str(e)
                    if is_content_filter_error(e):
                        row["judge_error_kind"] = "provider_content_filter"
                        row["judge_filter_categories"] = content_filter_categories(e)

        return Score(
            value=_as_score_value(row.get("schwartz_profile", {})),
            answer=row["parse_status"],
            metadata={"scored": row},
        )

    return score


# --------------------------------------------------------------------------- #
# task
# --------------------------------------------------------------------------- #


@task
def claims_bench_l3(
    data: str = str(DEFAULT_DATA),
    subset: Subset = "all",
    judge_model: str | None = None,
    judge_backend: str = "auto",
    max_tokens: int = 900,
    temperature: float = 0.0,
) -> Task:
    """CLAIMS-Bench L3 value-revelation eval.

    Args:
        data: items jsonl (default: the full 80-item set).
        subset: `all` | `structured` (Borda/BT from JSON) | `implicit` (free text).
        judge_model: LLM judge for failure modes + implicit profiles. Omit to
            skip all judge calls (structured items still get Borda/BT profiles).
        judge_backend: `auto` | `openai` | `anthropic`.
        max_tokens: L3 structured responses need room; legacy default is 900.
        temperature: 0 for baselines; >0 with `--epochs N` for consistency runs.
    """
    items = load_items(data, subset)
    return Task(
        dataset=MemoryDataset([record_to_sample(i) for i in items], name=f"claims_bench_l3_{subset}"),
        solver=generate(),
        scorer=revelation_scorer(judge_model=judge_model, judge_backend=judge_backend),
        config=GenerateConfig(max_tokens=max_tokens, temperature=temperature),
    )
