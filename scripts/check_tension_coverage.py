#!/usr/bin/env python3
"""Coverage check: which theoretically-real Schwartz circumplex tensions
(the `opposes` pairs in data/schwartz_backbone.yaml) have zero L3 items?

Run after adding items to confirm a gap is closed, or periodically to decide
where new items would actually add information vs. pad item count.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_backbone(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def theoretical_opposite_pairs(backbone: dict) -> set[tuple[str, str]]:
    pairs = set()
    for value, meta in backbone["values"].items():
        for opposite in meta.get("opposes", []):
            pairs.add(tuple(sorted((value, opposite))))
    return pairs


def item_tension_pairs(items: list[dict]) -> Counter:
    counter: Counter = Counter()
    for item in items:
        tensions = item.get("tags", {}).get("schwartz_tension", [])
        for t in tensions:
            parts = t.split("_vs_")
            if len(parts) == 2:
                counter[tuple(sorted(parts))] += 1
    return counter


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=str(REPO_ROOT / "data" / "v2_revelation.jsonl"))
    ap.add_argument("--backbone", default=str(REPO_ROOT / "data" / "schwartz_backbone.yaml"))
    args = ap.parse_args()

    items = [json.loads(line) for line in Path(args.data).read_text().splitlines() if line.strip()]
    backbone = load_backbone(Path(args.backbone))

    real_pairs = theoretical_opposite_pairs(backbone)
    covered = item_tension_pairs(items)

    zero_coverage = sorted(p for p in real_pairs if covered.get(p, 0) == 0)
    thin_coverage = sorted(
        (p, covered[p]) for p in real_pairs if 0 < covered.get(p, 0) <= 1
    )
    well_covered = sorted(
        (p, covered[p]) for p in real_pairs if covered.get(p, 0) >= 2
    )

    print(f"Loaded {len(items)} items from {args.data}")
    print(f"Theoretically-real circumplex-opposite pairs (from `opposes` in backbone): {len(real_pairs)}")
    print()

    print(f"=== ZERO COVERAGE ({len(zero_coverage)} pairs) — real theoretical tensions with no item ===")
    for a, b in zero_coverage:
        print(f"  {a} vs {b}")
    print()

    print(f"=== THIN COVERAGE ({len(thin_coverage)} pairs, exactly 1 item) ===")
    for (a, b), n in thin_coverage:
        print(f"  {n}  {a} vs {b}")
    print()

    print(f"=== WELL COVERED ({len(well_covered)} pairs, >=2 items) ===")
    for (a, b), n in sorted(well_covered, key=lambda x: -x[1]):
        print(f"  {n:2d}  {a} vs {b}")
    print()

    # Non-theoretical pairs that DO have items — not necessarily wrong (real
    # dilemmas often invoke more than one circumplex diagonal), but worth a
    # human glance: are these testing a real secondary tension, or drift?
    non_theoretical = sorted(
        (p, n) for p, n in covered.items() if p not in real_pairs
    )
    if non_theoretical:
        print(f"=== ITEMS TAGGED WITH NON-OPPOSITE PAIRS ({len(non_theoretical)}) — adjacent on circumplex, review whether the tension is real or drift ===")
        for (a, b), n in non_theoretical:
            print(f"  {n:2d}  {a} vs {b}")


if __name__ == "__main__":
    main()
