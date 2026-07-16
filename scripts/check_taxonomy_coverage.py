#!/usr/bin/env python3
"""Coverage check for the non-Schwartz taxonomy dimensions declared in
docs/TAXONOMY.md: `principle_tension` (Beauchamp & Childress) and the
categorical `stakeholder_config` / `epistemic_mode` tags.

Companion to check_tension_coverage.py (which does the same job for the
Schwartz circumplex). Unlike Schwartz, B&C's four principles have no
published circumplex geometry, so "theoretically real" here just means the
6 possible pairs among the 4 canonical principles (autonomy, beneficence,
nonmaleficence, justice) -- not an empirically-derived adjacency structure.
"""
import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The four canonical Beauchamp & Childress principles (Principles of
# Biomedical Ethics). Note: docs/TAXONOMY.md's declared principle_tension
# list includes "mercy" and "honesty" as poles, neither of which is one of
# the four -- flagged below as taxonomy drift, not treated as ground truth.
BC_PRINCIPLES = ["autonomy", "beneficence", "nonmaleficence", "justice"]

TAXONOMY_DECLARED_STAKEHOLDER = [
    "gabriel_1", "gabriel_2", "gabriel_3", "gabriel_4", "gabriel_5", "gabriel_6",
    "multi_stakeholder", "no_clear_stakeholder", "malicious_user",
]
TAXONOMY_DECLARED_EPISTEMIC_MODE = ["factual", "normative", "mixed", "speculative"]


def load_items(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def principle_pair_coverage(items: list[dict]) -> Counter:
    counter: Counter = Counter()
    for item in items:
        tensions = item.get("tags", {}).get("principle_tension", [])
        for t in tensions:
            parts = t.split("_vs_")
            if len(parts) == 2:
                counter[tuple(sorted(parts))] += 1
    return counter


def categorical_coverage(items: list[dict], field: str) -> Counter:
    counter: Counter = Counter()
    for item in items:
        val = item.get("tags", {}).get(field)
        if val is not None:
            counter[val] += 1
    return counter


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=str(REPO_ROOT / "data" / "v2_revelation.jsonl"))
    args = ap.parse_args()
    items = load_items(Path(args.data))
    print(f"Loaded {len(items)} items from {args.data}\n")

    # --- principle_tension ---
    real_bc_pairs = set(tuple(sorted(p)) for p in itertools.combinations(BC_PRINCIPLES, 2))
    covered = principle_pair_coverage(items)

    print("=== principle_tension: true Beauchamp & Childress 4-principle pairs ===")
    print(f"Possible pairs (4 choose 2): {len(real_bc_pairs)}")
    zero = sorted(p for p in real_bc_pairs if covered.get(p, 0) == 0)
    print(f"\nZERO COVERAGE ({len(zero)}):")
    for a, b in zero:
        print(f"  {a} vs {b}")
    nonzero = sorted(((p, n) for p, n in covered.items() if p in real_bc_pairs), key=lambda x: -x[1])
    print(f"\nCOVERED ({len(nonzero)}):")
    for (a, b), n in nonzero:
        print(f"  {n:2d}  {a} vs {b}")

    off_taxonomy = sorted(((p, n) for p, n in covered.items() if p not in real_bc_pairs), key=lambda x: -x[1])
    print(f"\nTAGS USING NON-CANONICAL POLES ({len(off_taxonomy)} distinct, i.e. not one of autonomy/beneficence/nonmaleficence/justice on both sides):")
    for (a, b), n in off_taxonomy:
        flag = " <- 'mercy' is not a B&C principle" if "mercy" in (a, b) else (" <- 'honesty' is not a B&C principle" if "honesty" in (a, b) else "")
        print(f"  {n:2d}  {a} vs {b}{flag}")

    # --- stakeholder_config ---
    print("\n=== stakeholder_config: categorical coverage vs. docs/TAXONOMY.md's declared list ===")
    sc = categorical_coverage(items, "stakeholder_config")
    for tag in TAXONOMY_DECLARED_STAKEHOLDER:
        n = sc.get(tag, 0)
        note = ""
        if tag.startswith("gabriel_"):
            note = "  (declared for L1 stakeholder-fairness tier; not necessarily expected in L3 revelation items)"
        elif tag == "malicious_user":
            note = "  (behavioral/L1 special case; not necessarily expected in L3)"
        print(f"  {n:2d}  {tag}{note}")

    # --- epistemic_mode ---
    print("\n=== epistemic_mode: categorical coverage vs. docs/TAXONOMY.md's declared list ===")
    em = categorical_coverage(items, "epistemic_mode")
    for tag in TAXONOMY_DECLARED_EPISTEMIC_MODE:
        n = em.get(tag, 0)
        note = "  (L3 is under-specified/normative by design; 'factual' may not be an expected L3 mode, not necessarily a gap)" if tag == "factual" else ""
        print(f"  {n:2d}  {tag}{note}")


if __name__ == "__main__":
    main()
