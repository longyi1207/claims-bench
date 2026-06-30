#!/usr/bin/env python3
"""Aggregate human panel responses for L3 revelation items.

Reads per-panelist JSONL files from data/panel/responses/ and produces:
  - Per-item aggregate: mean Schwartz profile, pairwise frequencies, dispute_index
  - Cross-item summary: most/least disputed items
  - model_comparison stub: per-item Schwartz distance ready for model_human_distance.py

Dispute index definition
------------------------
dispute_index is computed separately for each measurable signal type:

1. schwartz_dispute: mean across ranked values of (std / max_possible_std).
   High = panelists rank the same values very differently.

2. pairwise_dispute: per pair, 1 - |freq_a - freq_b|.
   0 = unanimous, 1 = perfectly split 50/50.
   Report per pair and mean across pairs.

3. epistemic_dispute: entropy of the epistemic_prior distribution,
   normalized to [0, 1] by dividing by log(n_options).

4. composite_dispute_index: weighted mean of the three (equal weights by default).
   This is the single number analogous to v0.5's dispute_index field.

All dispute values are in [0, 1]. Higher = more human disagreement = more genuinely
pluralistic item. Items with composite_dispute_index > 0.6 are flagged
`high_pluralism: true` in the output.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCHWARTZ_VALUES = [
    "self_direction", "stimulation", "hedonism", "achievement", "power",
    "security", "conformity", "tradition", "benevolence", "universalism",
]


# ---------------------------------------------------------------------------
# Dispute index helpers
# ---------------------------------------------------------------------------

def _schwartz_dispute(rank_lists: list[dict[str, int]]) -> float:
    """Mean normalized std of rank positions across panelists, per value."""
    if len(rank_lists) < 2:
        return 0.0
    values_seen: set[str] = set()
    for r in rank_lists:
        values_seen.update(r.keys())
    if not values_seen:
        return 0.0

    stds = []
    for v in values_seen:
        ranks = [r[v] for r in rank_lists if v in r]
        if len(ranks) < 2:
            continue
        n = len(ranks)
        mean = sum(ranks) / n
        variance = sum((x - mean) ** 2 for x in ranks) / (n - 1)
        std = math.sqrt(variance)
        # Max possible std for ranks 1..n_values: roughly (n_values-1)/2
        n_vals = len(values_seen)
        max_std = (n_vals - 1) / 2 if n_vals > 1 else 1.0
        stds.append(std / max_std if max_std > 0 else 0.0)
    return round(sum(stds) / len(stds), 4) if stds else 0.0


def _pairwise_dispute(pairwise_lists: list[dict[str, str]]) -> dict[str, float]:
    """Per pair_id: 1 - |freq_a - freq_b|. 0=unanimous, 1=50/50."""
    pair_counts: dict[str, Counter] = defaultdict(Counter)
    for pw in pairwise_lists:
        for pair_id, choice in pw.items():
            pair_counts[pair_id][choice] += 1

    result: dict[str, float] = {}
    for pair_id, counter in pair_counts.items():
        total = sum(counter.values())
        if total == 0:
            result[pair_id] = 0.0
            continue
        freqs = sorted([v / total for v in counter.values()], reverse=True)
        # dispute = 1 - (dominant share - other shares sum) doesn't generalize cleanly
        # For binary choices: dispute = 1 - |freq_top - freq_second|
        if len(freqs) >= 2:
            result[pair_id] = round(1.0 - abs(freqs[0] - freqs[1]), 4)
        else:
            result[pair_id] = 0.0  # unanimous
    return result


def _epistemic_dispute(prior_list: list[str], n_options: int = 3) -> float:
    """Normalized entropy of epistemic_prior distribution."""
    if not prior_list:
        return 0.0
    counter = Counter(prior_list)
    total = len(prior_list)
    entropy = -sum((c / total) * math.log(c / total) for c in counter.values() if c > 0)
    max_entropy = math.log(n_options)
    return round(entropy / max_entropy, 4) if max_entropy > 0 else 0.0


def compute_dispute_index(
    rank_lists: list[dict[str, int]],
    pairwise_lists: list[dict[str, str]],
    prior_list: list[str],
) -> dict[str, Any]:
    """Compute composite and component dispute indices for one item."""
    schwartz_d = _schwartz_dispute(rank_lists)
    pairwise_d = _pairwise_dispute(pairwise_lists)
    mean_pairwise_d = round(sum(pairwise_d.values()) / len(pairwise_d), 4) if pairwise_d else 0.0
    epistemic_d = _epistemic_dispute(prior_list)

    composite = round((schwartz_d + mean_pairwise_d + epistemic_d) / 3, 4)

    return {
        "composite_dispute_index": composite,
        "schwartz_dispute": schwartz_d,
        "pairwise_dispute_per_pair": pairwise_d,
        "mean_pairwise_dispute": mean_pairwise_d,
        "epistemic_dispute": epistemic_d,
        "high_pluralism": composite > 0.6,
        "n_panelists": len(rank_lists),
    }


# ---------------------------------------------------------------------------
# Per-item aggregation
# ---------------------------------------------------------------------------

def aggregate_item(responses: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate panel responses for a single item."""
    n = len(responses)
    rank_lists = [r["elicitation_response"].get("rank_values", {}) for r in responses]
    pairwise_lists = [r["elicitation_response"].get("pairwise", {}) for r in responses]
    prior_list = [
        r["elicitation_response"].get("epistemic_prior", "")
        for r in responses
        if r["elicitation_response"].get("epistemic_prior")
    ]

    # Mean + std Schwartz ranks
    value_ranks: dict[str, list[int]] = defaultdict(list)
    for rl in rank_lists:
        for v, rank in rl.items():
            value_ranks[v].append(int(rank))

    mean_ranks: dict[str, float] = {}
    std_ranks: dict[str, float] = {}
    for v, ranks in value_ranks.items():
        m = sum(ranks) / len(ranks)
        mean_ranks[v] = round(m, 3)
        if len(ranks) > 1:
            std_ranks[v] = round(math.sqrt(sum((r - m) ** 2 for r in ranks) / (len(ranks) - 1)), 3)
        else:
            std_ranks[v] = 0.0

    # Schwartz score (Borda from mean ranks)
    if mean_ranks:
        n_vals = len(mean_ranks)
        schwartz_profile = {
            v: round((n_vals - mean_ranks[v] + 1) / n_vals, 4)
            for v in mean_ranks
        }
    else:
        schwartz_profile = {}

    # Pairwise choice frequencies
    pair_freq: dict[str, Counter] = defaultdict(Counter)
    for pw in pairwise_lists:
        for pair_id, choice in pw.items():
            pair_freq[pair_id][choice] += 1
    pairwise_frequencies = {
        pair_id: {choice: round(count / n, 3) for choice, count in counter.items()}
        for pair_id, counter in pair_freq.items()
    }

    # Epistemic prior histogram
    epistemic_counter = Counter(prior_list)
    epistemic_hist = {k: round(v / len(prior_list), 3) for k, v in epistemic_counter.items()} if prior_list else {}

    dispute = compute_dispute_index(rank_lists, pairwise_lists, prior_list)

    return {
        "n_panelists": n,
        "mean_schwartz_ranks": mean_ranks,
        "std_schwartz_ranks": std_ranks,
        "schwartz_profile": schwartz_profile,
        "pairwise_frequencies": pairwise_frequencies,
        "epistemic_prior_histogram": epistemic_hist,
        "dispute": dispute,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description="Aggregate human panel responses for CLAIMS-Bench L3")
    p.add_argument(
        "--responses-dir",
        type=Path,
        default=Path("data/panel/responses"),
        help="Directory of per-panelist JSONL files",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("data/panel/panel_aggregate.json"),
        help="Output aggregate JSON",
    )
    p.add_argument(
        "--min-n",
        type=int,
        default=3,
        help="Minimum panelists to include an item in the output",
    )
    args = p.parse_args()

    # Load all responses, group by item_id
    by_item: dict[str, list[dict]] = defaultdict(list)
    response_files = list(args.responses_dir.glob("*.jsonl")) if args.responses_dir.exists() else []
    for fpath in response_files:
        for line in fpath.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            by_item[row["item_id"]].append(row)

    if not by_item:
        print(f"No response files found in {args.responses_dir}. Nothing to aggregate.")
        return

    results: dict[str, Any] = {}
    skipped = []
    for item_id, responses in sorted(by_item.items()):
        if len(responses) < args.min_n:
            skipped.append({"item_id": item_id, "n": len(responses)})
            continue
        results[item_id] = aggregate_item(responses)

    # Summary: rank items by composite dispute index
    dispute_ranking = sorted(
        [
            {
                "item_id": iid,
                "composite_dispute_index": agg["dispute"]["composite_dispute_index"],
                "high_pluralism": agg["dispute"]["high_pluralism"],
                "n_panelists": agg["n_panelists"],
            }
            for iid, agg in results.items()
        ],
        key=lambda x: -x["composite_dispute_index"],
    )

    output = {
        "n_items_aggregated": len(results),
        "n_items_skipped_low_n": len(skipped),
        "skipped": skipped,
        "dispute_ranking": dispute_ranking,
        "high_pluralism_items": [d for d in dispute_ranking if d["high_pluralism"]],
        "by_item": results,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(f"Aggregated {len(results)} items → {args.out}")
    print(f"High-pluralism items (dispute > 0.6): {len(output['high_pluralism_items'])}")
    if dispute_ranking:
        print(f"Most disputed: {dispute_ranking[0]['item_id']} ({dispute_ranking[0]['composite_dispute_index']})")
        print(f"Least disputed: {dispute_ranking[-1]['item_id']} ({dispute_ranking[-1]['composite_dispute_index']})")


if __name__ == "__main__":
    main()
