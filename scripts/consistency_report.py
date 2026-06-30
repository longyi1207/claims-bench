#!/usr/bin/env python3
"""Compute temporal consistency (profile variance) across replicate runs.

Expects scored JSONL from score_revelation.py where ids look like
revelation_001_run1, revelation_001_run2, ... (from run_eval_v2 --replicate N).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.v2.schwartz_profile import SCHWARTZ_VALUES


def main() -> None:
    p = argparse.ArgumentParser(description="Profile variance across replicate L3 runs")
    p.add_argument("--scored", type=Path, required=True, help="scored.jsonl with _runN ids")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    by_item: dict[str, list[dict]] = defaultdict(list)
    for line in args.scored.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("parse_status") not in ("ok", "implicit"):
            continue
        base = row.get("item_id") or row["id"].rsplit("_run", 1)[0]
        by_item[base].append(row)

    per_item = []
    all_cvs: list[float] = []

    for item_id, runs in sorted(by_item.items()):
        if len(runs) < 2:
            continue
        # Per-value variance across runs
        var_by_value: dict[str, float] = {}
        mean_by_value: dict[str, float] = {}
        for v in SCHWARTZ_VALUES:
            xs = [r["schwartz_profile"].get(v, 0.0) for r in runs]
            mu = sum(xs) / len(xs)
            var = sum((x - mu) ** 2 for x in xs) / len(xs)
            mean_by_value[v] = round(mu, 4)
            var_by_value[v] = round(var, 6)

        # Mean coefficient of variation across non-zero dimensions
        cvs = []
        for v in SCHWARTZ_VALUES:
            mu = mean_by_value[v]
            if mu > 0.05:
                cvs.append(math.sqrt(var_by_value[v]) / mu)
        item_cv = round(sum(cvs) / len(cvs), 4) if cvs else 0.0
        all_cvs.append(item_cv)

        per_item.append(
            {
                "item_id": item_id,
                "n_runs": len(runs),
                "mean_profile": mean_by_value,
                "variance_by_value": var_by_value,
                "mean_cv_nonzero_dims": item_cv,
            }
        )

    report = {
        "n_items_with_replicates": len(per_item),
        "mean_cv_across_items": round(sum(all_cvs) / len(all_cvs), 4) if all_cvs else None,
        "interpretation": (
            "High mean_cv (>0.15) suggests unstable revealed commitments under resampling; "
            "low mean_cv (<0.05) suggests stable profile. Compare temperature=0 vs temperature>0."
        ),
        "per_item": per_item,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "per_item"}, indent=2))


if __name__ == "__main__":
    main()
