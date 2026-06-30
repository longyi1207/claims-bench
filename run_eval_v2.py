#!/usr/bin/env python3
"""Generate model responses for CLAIMS-Bench L3 revelation items.

Reuses run_eval.py's backend generation functions; only the prompt assembly
differs — L3 items need their elicitation tasks (rank_values, pairwise_choice,
epistemic_prior, free_reasoning) spelled out so the model knows to produce
structured output matching data/schemas/revelation_response.schema.json.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

from tqdm import tqdm

from run_eval import detect_backend, generate_one
from src.io import load_jsonl
from src.v2.spend_log import log_spend

logger = logging.getLogger(__name__)

DEFAULT_DATA = Path("data/v2_revelation.jsonl")


def _format_task(task: dict) -> str:
    t = task.get("type")
    if t == "rank_values":
        return f"- Rank task: {task['instruction']}"
    if t == "pairwise_choice":
        lines = [f'  - "{p["id"]}": (A) {p["label_a"]}  vs  (B) {p["label_b"]}' for p in task["pairs"]]
        return "- Pairwise choice task: for each pair below, choose A or B.\n" + "\n".join(lines)
    if t == "epistemic_prior":
        return f"- Epistemic prior task: {task['question']} Options: {task['options']}"
    if t == "free_reasoning":
        return f"- Free reasoning: explain your answers in <= {task.get('max_words', 300)} words."
    return f"- Unrecognized task type: {t}"


def build_elicitation_instructions(item: dict) -> str:
    elicitation = item.get("elicitation", {})
    tasks = elicitation.get("tasks", [])
    task_lines = "\n".join(_format_task(t) for t in tasks)
    output_instruction = elicitation.get("output_instruction", "")
    return f"""{output_instruction}

Tasks:
{task_lines}

Respond with part (A) as a single fenced ```json code block containing keys
rank_values, pairwise, epistemic_prior — then part (B) as plain text reasoning."""


def build_messages_v2(item: dict) -> list[dict]:
    messages = []
    if hint := item.get("system_hint"):
        messages.append({"role": "system", "content": hint})
    prompt = item["prompt"].rstrip() + "\n\n" + build_elicitation_instructions(item)
    messages.append({"role": "user", "content": prompt})
    return messages


def generate_one_v2(backend: str, model: str, item: dict, max_new_tokens: int, dtype: str) -> str:
    """Same backends as run_eval.py, but with the L3-augmented prompt."""
    item_for_backend = dict(item)
    elicitation_text = build_elicitation_instructions(item)
    item_for_backend["prompt"] = item["prompt"].rstrip() + "\n\n" + elicitation_text
    return generate_one(backend, model, item_for_backend, max_new_tokens, dtype)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="CLAIMS-Bench L3 revelation response generation")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    p.add_argument("--model", type=str, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument(
        "--backend",
        type=str,
        default="auto",
        choices=["auto", "hf", "openai", "anthropic", "deepseek"],
    )
    p.add_argument("--max-new-tokens", type=int, default=900, help="L3 needs more room than L1/L2")
    p.add_argument("--limit", type=int, default=0, help="0 = all items")
    p.add_argument("--dtype", type=str, default="auto", choices=["auto", "float16", "bfloat16"])
    p.add_argument("--resume", action="store_true", help="Skip ids already in --out")
    p.add_argument("--sleep", type=float, default=0.0, help="Seconds between API calls")
    p.add_argument(
        "--est-usd",
        type=float,
        default=None,
        help="Known/estimated spend for this run (e.g. from provider dashboard) — logged to outputs/spend_log.jsonl",
    )
    args = p.parse_args()

    items = load_jsonl(args.data)
    if args.limit > 0:
        items = items[: args.limit]

    backend = detect_backend(args.model, args.backend)
    logger.info("Backend=%s model=%s n=%d", backend, args.model, len(items))

    done: set[str] = set()
    if args.resume and args.out.exists():
        for row in load_jsonl(args.out):
            done.add(row["id"])
        logger.info("Resuming: %d already done", len(done))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if args.resume and args.out.exists() else "w"
    written = 0
    with args.out.open(mode) as f:
        for item in tqdm(items, desc="generate_v2"):
            if item["id"] in done:
                continue
            try:
                response = generate_one_v2(backend, args.model, item, args.max_new_tokens, args.dtype)
            except Exception as e:
                logger.exception("Failed on %s", item["id"])
                response = f"[GENERATION_ERROR: {e}]"
            row = {
                "id": item["id"],
                "model": args.model,
                "response": response,
                "meta": {
                    "max_new_tokens": args.max_new_tokens,
                    "backend": backend,
                    "layer": item.get("layer"),
                    "domain": item.get("domain"),
                },
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            written += 1
            if args.sleep > 0:
                time.sleep(args.sleep)

    logger.info("Wrote %d responses to %s", written, args.out)
    if backend != "hf" and written > 0:
        log_spend(
            provider=backend,
            model=args.model,
            items=written,
            est_usd=args.est_usd,
            notes=f"run_eval_v2 generation -> {args.out}",
        )


if __name__ == "__main__":
    main()
