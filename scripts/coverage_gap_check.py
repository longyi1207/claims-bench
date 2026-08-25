#!/usr/bin/env python3
"""Does "near-zero hedonism/stimulation" survive the coverage-gap items?

`paper/claims_bench_v2.md` §6.1 reports near-zero `stimulation` and `hedonism`
across all three models, with an explicit caveat: the 30-item pilot subset it was
computed on contains **no item that pits hedonism or stimulation against its real
circumplex-opposite value**. Items 044–049 were authored precisely to close that
gap, and 050–055 to test `justice` against the three Beauchamp & Childress
principles it had never been tested against. Until those items are actually run,
both "findings" are unfalsifiable — a property of the item set, not of the models.

This script slices a scored run by item group and prints the per-group mean
profile, so the two claims become checkable:

    python scripts/coverage_gap_check.py \\
        --scored outputs/expansion_044_080/*_scored.jsonl \\
        --baseline outputs/baseline_v2_structured/*_scored.jsonl \\
        --out outputs/expansion_044_080/coverage_gap_check.json

Groups are defined by the item's own `tags.schwartz_tension` /
`tags.principle_tension`, not by id range, so they stay correct if the item set
is renumbered.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io import index_by_id, load_jsonl
from src.v2.schwartz_profile import SCHWARTZ_VALUES

# The two values §6.1 calls near-zero, and the principle §3.2 calls untested.
FOCUS_VALUES = ["hedonism", "stimulation"]
FOCUS_PRINCIPLE = "justice"


def item_groups(item: dict) -> list[str]:
    tags = item.get("tags") or {}
    schwartz = [t for t in (tags.get("schwartz_tension") or [])]
    principle = [t for t in (tags.get("principle_tension") or [])]
    groups = []
    for v in FOCUS_VALUES:
        if any(v in t for t in schwartz):
            groups.append(f"tests_{v}")
    if any(FOCUS_PRINCIPLE in t for t in principle):
        groups.append("tests_justice")
    if not groups:
        groups.append("other")
    return groups


def mean_profile(rows: list[dict]) -> dict[str, float]:
    scored = [r for r in rows if r.get("schwartz_profile")]
    if not scored:
        return {}
    out = {v: 0.0 for v in SCHWARTZ_VALUES}
    for r in scored:
        for v in SCHWARTZ_VALUES:
            out[v] += float(r["schwartz_profile"].get(v, 0.0))
    return {v: round(x / len(scored), 4) for v, x in out.items()}


def summarize(scored_paths: list[Path], items: dict[str, dict], label: str) -> dict:
    by_model_group: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for p in scored_paths:
        for row in load_jsonl(p):
            item = items.get(row.get("item_id") or row["id"].rsplit("_run", 1)[0])
            if item is None:
                continue
            model = row.get("model") or p.stem.replace("_scored", "")
            for g in item_groups(item):
                by_model_group[model][g].append(row)
            by_model_group[model]["ALL"].append(row)

    result = {"label": label, "models": {}}
    for model, groups in sorted(by_model_group.items()):
        result["models"][model] = {
            g: {
                "n_items": len(rows),
                "n_with_profile": sum(1 for r in rows if r.get("schwartz_profile")),
                "mean_profile": mean_profile(rows),
            }
            for g, rows in sorted(groups.items())
        }
    return result


def print_focus_table(summary: dict) -> None:
    print(f"\n### {summary['label']}")
    print(f"\n| model | group | n (scored) | hedonism | stimulation | top-3 |")
    print("|---|---|---|---|---|---|")
    for model, groups in summary["models"].items():
        for g, d in groups.items():
            prof = d["mean_profile"]
            if not prof:
                print(f"| {model} | {g} | {d['n_with_profile']}/{d['n_items']} | — | — | (no scored profile) |")
                continue
            top3 = ", ".join(
                f"{k}={v:.2f}" for k, v in sorted(prof.items(), key=lambda x: -x[1])[:3]
            )
            print(
                f"| {model} | {g} | {d['n_with_profile']}/{d['n_items']} | "
                f"{prof['hedonism']:.3f} | {prof['stimulation']:.3f} | {top3} |"
            )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scored", type=Path, nargs="+", required=True, help="scored.jsonl from the new items")
    p.add_argument("--baseline", type=Path, nargs="*", default=[], help="scored.jsonl from the pilot subset")
    p.add_argument("--data", type=Path, default=Path("data/v2_revelation.jsonl"))
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--label", default=None, help="label for the --scored set")
    p.add_argument("--baseline-label", default="pilot subset (001-030, published 6.1)")
    args = p.parse_args()

    items = index_by_id(load_jsonl(args.data))

    summaries = [summarize(args.scored, items, args.label or "scored run")]
    if args.baseline:
        summaries.append(summarize(args.baseline, items, args.baseline_label))

    for s in summaries:
        print_focus_table(s)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(summaries, indent=2) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
