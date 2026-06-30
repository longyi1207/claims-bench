#!/usr/bin/env python3
"""Compare L3 Schwartz profiles across models — Table 1 generator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.v2.schwartz_profile import SCHWARTZ_VALUES


def load_report(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    p = argparse.ArgumentParser(description="Compare L3 revelation reports across models")
    p.add_argument(
        "--reports",
        nargs="+",
        type=Path,
        required=True,
        help="report.json paths from score_revelation.py",
    )
    p.add_argument("--markdown", type=Path, default=None)
    args = p.parse_args()

    rows = []
    for rp in args.reports:
        data = load_report(rp)
        summary = data.get("summary", {})
        model = data.get("model") or rp.parent.name
        prof = summary.get("mean_schwartz_profile", {})
        bt = summary.get("bradley_terry_profile", {})
        rows.append(
            {
                "model": model,
                "n": summary.get("n", 0),
                "n_structured": summary.get("n_structured_profile", summary.get("n_with_valid_profile")),
                "n_implicit": summary.get("n_implicit_profile", 0),
                "compliance": summary.get("structured_compliance_rate", summary.get("format_compliance_rate")),
                "profile": prof,
                "bt_profile": bt,
                "failure_rates": summary.get("failure_mode_rates", {}),
            }
        )

    lines = [
        "# L3 Schwartz Profile Comparison",
        "",
        "| Model | n | structured ok | implicit | compliance | top-3 values (Borda mean) |",
        "|-------|---|---------------|----------|------------|---------------------------|",
    ]
    for r in rows:
        top3 = sorted(r["profile"].items(), key=lambda x: -x[1])[:3]
        top3s = ", ".join(f"{k}={v:.2f}" for k, v in top3 if k in SCHWARTZ_VALUES)
        lines.append(
            f"| {r['model']} | {r['n']} | {r['n_structured']} | {r['n_implicit']} | "
            f"{r['compliance']:.2f} | {top3s} |"
        )

    lines.extend(["", "## Full mean_schwartz_profile (Borda)", ""])
    header = "| Model | " + " | ".join(SCHWARTZ_VALUES) + " |"
    sep = "|---|" + "|".join(["---"] * len(SCHWARTZ_VALUES)) + "|"
    lines.extend([header, sep])
    for r in rows:
        vals = " | ".join(f"{r['profile'].get(v, 0):.3f}" for v in SCHWARTZ_VALUES)
        lines.append(f"| {r['model']} | {vals} |")

    if any(r["bt_profile"] for r in rows):
        lines.extend(["", "## Bradley-Terry profile (pairwise-derived)", ""])
        lines.extend([header, sep])
        for r in rows:
            vals = " | ".join(f"{r['bt_profile'].get(v, 0):.3f}" for v in SCHWARTZ_VALUES)
            lines.append(f"| {r['model']} | {vals} |")

    md = "\n".join(lines) + "\n"
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(md)
        print(f"Wrote {args.markdown}")
    else:
        print(md)


if __name__ == "__main__":
    main()
