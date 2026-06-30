#!/usr/bin/env python3
"""Compare norm profiles across models on CLAIMS-Bench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.aggregate import aggregate
from src.io import index_by_id, load_jsonl

DEFAULT_DATA = Path("data/v0.2_core120.jsonl")

METRICS = [
    "acceptable_rate",
    "primary_accuracy",
    "blanket_refusal_rate",
    "welfare_aggregate_bias_rate",
    "control_help_refusal_rate",
]


def main() -> None:
    p = argparse.ArgumentParser(description="Compare CLAIMS-Bench model reports")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA)
    p.add_argument(
        "--reports",
        nargs="+",
        type=Path,
        required=True,
        help="Report JSON files from score_responses.py",
    )
    p.add_argument("--out", type=Path, default=Path("outputs/leaderboard.json"))
    p.add_argument("--markdown", type=Path, default=None, help="Optional markdown table")
    args = p.parse_args()

    rows = []
    for path in args.reports:
        report = json.loads(path.read_text())
        model = report.get("model") or path.stem
        summary = report.get("summary", report)
        row = {"model": model, "report": str(path), **{m: summary.get(m) for m in METRICS}}
        row["n"] = summary.get("n")
        row["by_conflict_type"] = summary.get("by_conflict_type", {})
        row["failure_mode_counts"] = summary.get("failure_mode_counts", {})
        vp = summary.get("value_profile", {})
        if vp.get("n_scored"):
            row["western_index"] = vp.get("western_index")
            row["eastern_relational_index"] = vp.get("eastern_relational_index")
            row["utilitarian_minus_deontological"] = vp.get("utilitarian_minus_deontological")
        rows.append(row)

    rows.sort(key=lambda r: (-(r.get("acceptable_rate") or 0), r["model"]))

    out = {"metrics": METRICS, "models": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

    if args.markdown:
        lines = [
            "| Model | acceptable | primary | blanket_refusal | welfare_bias | control_help_refusal |",
            "|-------|------------|---------|-----------------|--------------|----------------------|",
        ]
        for r in rows:
            def fmt(v):
                return f"{v:.3f}" if isinstance(v, float) else ("—" if v is None else str(v))

            lines.append(
                f"| {r['model']} | {fmt(r.get('acceptable_rate'))} | "
                f"{fmt(r.get('primary_accuracy'))} | {fmt(r.get('blanket_refusal_rate'))} | "
                f"{fmt(r.get('welfare_aggregate_bias_rate'))} | "
                f"{fmt(r.get('control_help_refusal_rate'))} |"
            )
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text("\n".join(lines) + "\n")
        print(f"Wrote {args.markdown}")

    print(json.dumps({"leaderboard": rows}, indent=2))
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
