#!/usr/bin/env python3
"""Compare fundamental value profiles across model reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VALUE_METRICS = [
    "western_index",
    "eastern_relational_index",
    "deontological_index",
    "utilitarian_index",
    "western_minus_eastern",
    "utilitarian_minus_deontological",
]


def main() -> None:
    p = argparse.ArgumentParser(description="Compare value profiles across CLAIMS-Bench reports")
    p.add_argument("--reports", nargs="+", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("outputs/value_leaderboard.json"))
    p.add_argument("--markdown", type=Path, default=None)
    args = p.parse_args()

    rows = []
    for path in args.reports:
        report = json.loads(path.read_text())
        model = report.get("model") or path.parent.name
        vp = report.get("summary", report).get("value_profile", {})
        if not vp or vp.get("n_scored", 0) == 0:
            continue
        row = {
            "model": model,
            "report": str(path),
            "n_scored": vp.get("n_scored"),
            **{m: vp.get(m) for m in VALUE_METRICS},
            "top_values": vp.get("top_values", [])[:3],
        }
        rows.append(row)

    rows.sort(key=lambda r: -(r.get("western_index") or 0))
    out = {"metrics": VALUE_METRICS, "models": rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

    if args.markdown:
        lines = [
            "| Model | western | eastern | deontological | utilitarian | W−E | util−deont | top value |",
            "|-------|---------|---------|---------------|-------------|-----|------------|-----------|",
        ]
        for r in rows:
            top = r["top_values"][0]["value"] if r["top_values"] else "—"
            lines.append(
                f"| {r['model']} | {r['western_index']:.3f} | {r['eastern_relational_index']:.3f} | "
                f"{r['deontological_index']:.3f} | {r['utilitarian_index']:.3f} | "
                f"{r['western_minus_eastern']:.3f} | {r['utilitarian_minus_deontological']:.3f} | {top} |"
            )
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text("\n".join(lines) + "\n")
        print(f"Wrote {args.markdown}")

    print(json.dumps(out, indent=2))
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
