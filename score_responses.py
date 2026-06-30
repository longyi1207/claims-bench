#!/usr/bin/env python3
"""Score CLAIMS-Bench responses (heuristic and/or LLM judge)."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from tqdm import tqdm

from src.aggregate import aggregate
from src.heuristic import (
    behavior_tag,
    detect_failures,
    dispute_acknowledged,
    predict_norm_class,
)
from src.values import score_values
from src.io import index_by_id, load_jsonl
from src.judge import merge_score, run_judge

logger = logging.getLogger(__name__)

DEFAULT_DATA = Path("data/v0.2_core120.jsonl")


def score_heuristic(item: dict, response: str) -> dict:
    tag = behavior_tag(response)
    predicted = predict_norm_class(item, response, tag)
    nc = item["norm_classes"]
    primary = nc.get("primary")
    failures = detect_failures(item, response, predicted, tag)
    ack = dispute_acknowledged(response)
    out = {
        "behavior_tag": tag,
        "predicted_norm_class": predicted,
        "primary_match": predicted == primary if primary is not None else None,
        "acceptable_match": predicted in nc["acceptable"]
        or (predicted == "ambiguous" and "ambiguous" in nc["acceptable"]),
        "failure_modes_triggered": failures,
        "dispute_acknowledged": ack,
        "judge_rationale": "heuristic_v0",
        "scorer": "heuristic",
    }
    out.update(score_values(item, response))
    return out


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Score CLAIMS-Bench responses")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    p.add_argument("--responses", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--scored-out", type=Path, default=None, help="Per-item scores JSONL")
    p.add_argument("--scorer", choices=["heuristic", "judge", "both"], default="heuristic")
    p.add_argument("--judge-model", type=str, default=None)
    p.add_argument(
        "--judge-backend",
        type=str,
        default="auto",
        choices=["auto", "openai", "anthropic"],
    )
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    if args.scorer in ("judge", "both") and not args.judge_model:
        p.error("--judge-model required when --scorer is judge or both")

    items_list = load_jsonl(args.data)
    items = index_by_id(items_list)
    responses = load_jsonl(args.responses)
    if args.limit > 0:
        responses = responses[: args.limit]

    judge_backend = args.judge_backend
    if judge_backend == "auto" and args.judge_model:
        if args.judge_model.startswith("claude"):
            judge_backend = "anthropic"
        else:
            judge_backend = "openai"

    scored = []
    for row in tqdm(responses, desc="score"):
        item = items[row["id"]]
        resp = row.get("response", "")

        if args.scorer == "heuristic":
            s = score_heuristic(item, resp)
        elif args.scorer == "judge":
            judge_out = run_judge(judge_backend, args.judge_model, item, resp)
            s = merge_score(item, judge_out)
        else:
            h = score_heuristic(item, resp)
            try:
                judge_out = run_judge(judge_backend, args.judge_model, item, resp)
                s = merge_score(item, judge_out)
                s["heuristic"] = h
            except Exception as e:
                logger.warning("Judge failed on %s: %s — falling back to heuristic", item["id"], e)
                s = h

        # Value layer always computed from response text
        if "value_scores" not in s:
            s.update(score_values(item, resp))

        scored.append({"id": row["id"], "model": row.get("model"), **s})

    scorer_label = args.scorer
    if args.scorer in ("judge", "both"):
        scorer_label = f"{args.scorer}:{args.judge_model}"

    report = {
        "summary": aggregate(scored, items),
        "model": responses[0].get("model") if responses else None,
        "data": str(args.data),
        "responses": str(args.responses),
        "scorer": scorer_label,
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

    if args.scored_out:
        args.scored_out.parent.mkdir(parents=True, exist_ok=True)
        with args.scored_out.open("w") as f:
            for s in scored:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
