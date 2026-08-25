#!/usr/bin/env python3
"""Model-vs-model significance testing on multi-replicate scored runs.

`src/v2/significance.py` has had the statistics (item-cluster bootstrap CIs,
permutation tests, Cohen's *d* on item means, Benjamini–Hochberg across the 10
dimensions) since the July 2026 pilot, but the pilot drove it ad hoc and only the
resulting `significance_report.json` was committed — there was no reusable
entry point. This is it.

Input is the scored jsonl any run produces (legacy `--replicate N` runs or an
Inspect `--epochs N` export; both carry `item_id` plus `_run{N}` ids).

    python scripts/significance_report.py \\
        --scored outputs/full80/structured/*_scored.jsonl \\
        --out outputs/full80/significance_report.json

Rows with `parse_status` in {generation_error, provider_filtered, schema_invalid}
are dropped before aggregation and counted in the report — a deployment-level
content-filter refusal must never enter a value profile as if it were an answer
(see docs/INSPECT_MIGRATION.md).
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io import load_jsonl
from src.v2.schwartz_profile import SCHWARTZ_VALUES
from src.v2.significance import compare_models_all_dimensions

EXCLUDED_STATUSES = {"generation_error", "provider_filtered", "schema_invalid", "non_compliant_format"}


def load_profiles(paths: list[Path]) -> tuple[dict, dict]:
    """-> ({model: {item_id: {value: [replicates...]}}}, {model: exclusion counts})"""
    profiles: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    excluded: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for path in paths:
        for row in load_jsonl(path):
            model = row.get("model") or path.stem.replace("_scored", "")
            status = row.get("parse_status")
            if status in EXCLUDED_STATUSES or not row.get("schwartz_profile"):
                excluded[model][status or "no_profile"] += 1
                continue
            item_id = row.get("item_id") or row["id"].rsplit("_run", 1)[0]
            for value in SCHWARTZ_VALUES:
                profiles[model][item_id][value].append(float(row["schwartz_profile"].get(value, 0.0)))
    return profiles, excluded


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scored", type=Path, nargs="+", required=True)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--n-perm", type=int, default=5000)
    p.add_argument("--fdr-alpha", type=float, default=0.05)
    args = p.parse_args()

    profiles, excluded = load_profiles(args.scored)
    models = sorted(profiles)
    if len(models) < 2:
        raise SystemExit(f"need >=2 models to compare, found {models}")

    print("## Coverage\n")
    print("| model | items | replicates/item (min-max) | dropped rows |")
    print("|---|---|---|---|")
    coverage = {}
    for m in models:
        counts = [len(v[SCHWARTZ_VALUES[0]]) for v in profiles[m].values()]
        drop = dict(excluded.get(m, {}))
        coverage[m] = {
            "n_items": len(profiles[m]),
            "replicates_min": min(counts) if counts else 0,
            "replicates_max": max(counts) if counts else 0,
            "dropped": drop,
        }
        print(
            f"| {m} | {len(profiles[m])} | {min(counts) if counts else 0}–{max(counts) if counts else 0} "
            f"| {drop or '—'} |"
        )

    report = {"coverage": coverage, "comparisons": {}}
    for a, b in itertools.combinations(models, 2):
        # Compare only on items both models actually have — an item dropped for
        # one model (e.g. filtered) must not shift the other model's mean.
        shared = sorted(set(profiles[a]) & set(profiles[b]))
        pa = {i: profiles[a][i] for i in shared}
        pb = {i: profiles[b][i] for i in shared}
        res = compare_models_all_dimensions(
            pa, pb, n_boot=args.n_boot, n_perm=args.n_perm, fdr_alpha=args.fdr_alpha
        )
        report["comparisons"][f"{a}__vs__{b}"] = {"n_shared_items": len(shared), "dimensions": res}

        print(f"\n## {a}  vs  {b}   (n={len(shared)} shared items)\n")
        print(f"| dimension | {a} mean [95% CI] | {b} mean [95% CI] | perm p | Cohen's d | FDR sig |")
        print("|---|---|---|---|---|---|")
        for value in SCHWARTZ_VALUES:
            r = res[value]
            ca, cb = r["model_a"], r["model_b"]
            sig = "**yes**" if r["significant_after_fdr"] else "no"
            print(
                f"| {value} | {ca['mean']:.3f} [{ca['ci_low']:.3f}, {ca['ci_high']:.3f}] "
                f"| {cb['mean']:.3f} [{cb['ci_low']:.3f}, {cb['ci_high']:.3f}] "
                f"| {r['permutation_p_value']:.4f} "
                f"| {r['cohens_d_on_item_means']:.3f} | {sig} |"
            )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
