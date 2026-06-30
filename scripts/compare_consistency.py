#!/usr/bin/env python3
"""Compare two consistency reports (e.g. temp=0.0 vs temp=0.7)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    p = argparse.ArgumentParser(description="Compare L3 consistency reports")
    p.add_argument("--a", type=Path, required=True, help="First consistency JSON")
    p.add_argument("--label-a", type=str, default="a")
    p.add_argument("--b", type=Path, required=True, help="Second consistency JSON")
    p.add_argument("--label-b", type=str, default="b")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    ra, rb = load(args.a), load(args.b)
    by_item_a = {x["item_id"]: x for x in ra.get("per_item", [])}
    by_item_b = {x["item_id"]: x for x in rb.get("per_item", [])}
    common = sorted(set(by_item_a) & set(by_item_b))

    rows = []
    for item_id in common:
        cva = by_item_a[item_id]["mean_cv_nonzero_dims"]
        cvb = by_item_b[item_id]["mean_cv_nonzero_dims"]
        rows.append(
            {
                "item_id": item_id,
                f"cv_{args.label_a}": cva,
                f"cv_{args.label_b}": cvb,
                "cv_delta": round(cvb - cva, 4),
                "more_stable_under": args.label_a if cva < cvb else args.label_b,
            }
        )

    report = {
        "label_a": args.label_a,
        "label_b": args.label_b,
        "mean_cv_a": ra.get("mean_cv_across_items"),
        "mean_cv_b": rb.get("mean_cv_across_items"),
        "mean_cv_delta": round(
            (rb.get("mean_cv_across_items") or 0) - (ra.get("mean_cv_across_items") or 0), 4
        ),
        "per_item": rows,
        "interpretation": (
            "Positive cv_delta means label_b is less stable (higher variance). "
            "Expect temp=0.0 < temp=0.7 on mean_cv if profiles reflect real commitments."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "per_item"}, indent=2))


if __name__ == "__main__":
    main()
