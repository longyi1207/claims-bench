#!/usr/bin/env python3
"""Export an Inspect `.eval` log to the legacy CLAIMS-Bench jsonl shape.

Everything downstream of generation — `score_revelation.py`'s aggregate report,
`scripts/consistency_report.py`, `src/v2/significance.py`,
`compare_profiles_v2.py`, `paper/generate_figures.py` — reads
`responses.jsonl` / `scored.jsonl`. This script is the seam: Inspect owns
generation and per-sample scoring, the existing analysis stack keeps owning
cross-sample aggregation, and neither has to know about the other.

Emits, for a log at `--log`:
  <out-dir>/<model>_responses.jsonl   # id, item_id, model, response, meta
  <out-dir>/<model>_scored.jsonl      # legacy scored row (only if the log was scored)
  <out-dir>/<model>_usage.json        # token usage from the log (see --log-spend)

Replicates: Inspect `--epochs N` becomes the legacy `_run{epoch}` id suffix, so
a multi-epoch log drops straight into `consistency_report.py` / `significance.py`.

Usage:
    python scripts/eval_log_to_jsonl.py --log logs/2026-08-24T…_claims-bench-l3.eval \
        --out-dir outputs/full80_run --log-spend
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Any

from inspect_ai.log import read_eval_log

from src.providers import PROVIDER_FILTERED_PREFIX, looks_like_filter_response

logger = logging.getLogger(__name__)

_FILTER_HINTS = ("content_filter", "content management policy", "responsibleaipolicyviolation")


def _error_marker(message: str) -> str:
    """Azure refuses some items at the deployment level; that is not the model
    declining, and must not be scored as if it were."""
    if any(h in (message or "").lower() for h in _FILTER_HINTS):
        return f"{PROVIDER_FILTERED_PREFIX} {message}]"
    return f"[GENERATION_ERROR: {message}]"


def _model_slug(model: str) -> str:
    """`openai/gpt-4o` and `openai-api/azure/gpt-4o` -> `gpt-4o`.

    Keeps output filenames matching the legacy runs regardless of how many
    provider segments the Inspect model string carries.
    """
    return model.rsplit("/", 1)[-1]


def _provider(model: str) -> str:
    """Everything before the model name: `openai-api/azure`, `anthropic`, ..."""
    return model.rsplit("/", 1)[0] if "/" in model else model


def _sample_id(sample: Any, multi_epoch: bool) -> tuple[str, str]:
    item_id = str(sample.id)
    if multi_epoch:
        return f"{item_id}_run{sample.epoch}", item_id
    return item_id, item_id


def _scored_row(sample: Any) -> dict[str, Any] | None:
    """Pull the legacy scored row the Inspect scorer stashed in Score.metadata."""
    scores = sample.scores or {}
    for score in scores.values():
        meta = score.metadata or {}
        if "scored" in meta:
            return dict(meta["scored"])
    return None


def export(log_path: Path, out_dir: Path, log_spend: bool = False) -> dict[str, Any]:
    log = read_eval_log(str(log_path))
    if log.status != "success":
        logger.warning("log status is %r — exporting what completed", log.status)
    if not log.samples:
        raise SystemExit(f"{log_path}: no samples in log (headers only?)")

    model = log.eval.model
    slug = _model_slug(model)
    epochs = getattr(log.eval.config, "epochs", None) or 1
    multi_epoch = epochs > 1

    gen_cfg = log.eval.model_generate_config
    meta_common = {
        "max_new_tokens": getattr(gen_cfg, "max_tokens", None),
        "backend": "inspect:" + _provider(model),
        "temperature": getattr(gen_cfg, "temperature", None),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    resp_path = out_dir / f"{slug}_responses.jsonl"
    scored_path = out_dir / f"{slug}_scored.jsonl"

    n_resp = n_scored = n_error = n_filtered = 0
    scored_rows: list[dict[str, Any]] = []

    with resp_path.open("w") as f:
        for sample in log.samples:
            row_id, item_id = _sample_id(sample, multi_epoch)
            item = (sample.metadata or {}).get("item", {})
            if sample.error is not None:
                response = _error_marker(sample.error.message)
                n_error += 1
                if response.startswith(PROVIDER_FILTERED_PREFIX):
                    n_filtered += 1
            else:
                response = sample.output.completion or ""
                if looks_like_filter_response(response):
                    # HTTP 200 whose body is the filter notice — not an answer.
                    response = f"{PROVIDER_FILTERED_PREFIX} {response.strip()}]"
                    n_filtered += 1
            f.write(
                json.dumps(
                    {
                        "id": row_id,
                        "item_id": item_id,
                        "model": slug,
                        "response": response,
                        "meta": {
                            **meta_common,
                            "layer": item.get("layer"),
                            "domain": item.get("domain"),
                            "elicitation_type": item.get("elicitation_type"),
                            "replicate": sample.epoch if multi_epoch else None,
                        },
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            n_resp += 1

            scored = _scored_row(sample)
            if scored is not None:
                if response.startswith(PROVIDER_FILTERED_PREFIX):
                    # The log may hold a score computed before the filter notice
                    # was recognised (or a judge's read of the notice itself).
                    # Neither is model behaviour — overwrite, don't inherit.
                    scored = {
                        "parse_status": "provider_filtered",
                        "schwartz_profile": {},
                        "pairwise": {},
                        "bt_comparisons": [],
                        "epistemic_prior": None,
                        "reasoning_text": response,
                        "structured_raw": {},
                    }
                scored_rows.append({"id": row_id, "item_id": item_id, "model": slug, **scored})

    if scored_rows:
        with scored_path.open("w") as f:
            for row in scored_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        n_scored = len(scored_rows)

    # Token usage — the thing the legacy pipeline could only get by hand-copying
    # a number off a provider dashboard into `--est-usd`.
    usage = {
        name: u.model_dump() if hasattr(u, "model_dump") else dict(u)
        for name, u in (log.stats.model_usage or {}).items()
    }
    usage_path = out_dir / f"{slug}_usage.json"
    usage_path.write_text(json.dumps(usage, indent=2) + "\n")

    if log_spend:
        from src.v2.spend_log import log_spend as append_spend

        append_spend(
            provider="inspect:" + _provider(model),
            model=slug,
            items=n_resp,
            est_usd=None,
            notes=(
                f"inspect eval -> {log_path.name}; tokens={json.dumps(usage)}"
            ),
        )

    summary = {
        "log": str(log_path),
        "model": model,
        "epochs": epochs,
        "responses": n_resp,
        "scored": n_scored,
        "generation_errors": n_error,
        "provider_filtered": n_filtered,
        "responses_path": str(resp_path),
        "scored_path": str(scored_path) if scored_rows else None,
        "usage": usage,
    }
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log", type=Path, required=True, nargs="+", help="one or more .eval logs")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument(
        "--log-spend",
        action="store_true",
        help="append a row to outputs/spend_log.jsonl with the log's token usage",
    )
    args = p.parse_args()

    for log_path in args.log:
        summary = export(log_path, args.out_dir, log_spend=args.log_spend)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
