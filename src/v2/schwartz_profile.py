"""Infer Schwartz value profile from structured L3 elicitation.

Two complementary scoring methods:

1. **Borda count** (`infer_profile`, `infer_full_profile`): from `rank_values`.
   Fast, interpretable, but ordinal only — can't express "security much more
   important than universalism" vs "barely prefer."

2. **Bradley-Terry** (`bradley_terry_profile`): from pairwise choices annotated
   with `pole_a`/`pole_b` Schwartz values. Each choice of label_a over label_b
   is treated as a win for pole_a over pole_b. BT estimates a utility/strength
   score per value using Zermelo's iterative algorithm. Requires pole annotations
   in item YAMLs (added to all 20 items in Phase 2/3). Treats pairwise data as
   cardinal signal rather than discarding it.

For cross-item aggregation: collect `(pole_a, pole_b, winner_pole)` tuples from
all scored items for a model, then call `bradley_terry_profile` on the full list.
"""

from __future__ import annotations

import math
from typing import Any

# Canonical Schwartz 10 — used for Borda profile and main BT profile.
SCHWARTZ_VALUES = [
    "self_direction",
    "stimulation",
    "hedonism",
    "achievement",
    "power",
    "security",
    "conformity",
    "tradition",
    "benevolence",
    "universalism",
]

# Supplementary probes (Haidt MFT — not Schwartz canonical).
# Excluded from Borda (rank_values tasks never include them).
# Included in BT when they appear as pole annotations in pairwise pairs.
# Reported in a separate "supplementary_probes" key, not in schwartz_profile.
# Source: Haidt & Joseph (2004); Graham et al. (2009).
SUPPLEMENTARY_PROBES = ["sanctity"]

ALL_TRACKED_VALUES = SCHWARTZ_VALUES + SUPPLEMENTARY_PROBES


def ranks_to_scores(rank_values: dict[str, int]) -> dict[str, float]:
    """Convert rank dict (1=best) to normalized 0-1 scores (Borda count)."""
    if not rank_values:
        return {}
    n = len(rank_values)
    scores: dict[str, float] = {}
    for value, rank in rank_values.items():
        # rank 1 -> 1.0, rank n -> 1/n
        scores[value] = (n - rank + 1) / n
    return scores


def infer_profile(elicitation_response: dict[str, Any]) -> dict[str, float]:
    """Build partial Schwartz profile from parsed revelation response.

    Returns scores only for the values the model actually ranked (partial
    vector — most items rank 5 of the 10 Schwartz values).
    """
    rank_values = elicitation_response.get("rank_values") or {}
    return ranks_to_scores({k: int(v) for k, v in rank_values.items()})


def infer_full_profile(elicitation_response: dict[str, Any]) -> dict[str, float]:
    """Build the full 10-dim Schwartz vector, zero-filling unranked values.

    Use this for cross-item/cross-model aggregation where vectors must be
    directly comparable; use `infer_profile` when you want to distinguish
    "ranked low" from "not asked about."
    """
    partial = infer_profile(elicitation_response)
    return {value: partial.get(value, 0.0) for value in SCHWARTZ_VALUES}


def pairwise_summary(elicitation_response: dict[str, Any]) -> dict[str, str]:
    """Return pair_id -> chosen option id (label_a or label_b)."""
    pairwise = elicitation_response.get("pairwise") or {}
    return {k: str(v) for k, v in pairwise.items()}


def extract_pairwise_comparisons(
    item: dict[str, Any], elicitation_response: dict[str, Any]
) -> list[tuple[str, str, str]]:
    """Extract (pole_a, pole_b, winner_pole) tuples from a single scored item.

    Returns an empty list if the item has no pole annotations or parse failed.
    Only considers pairs where both pole_a and pole_b are valid Schwartz values.
    """
    chosen = pairwise_summary(elicitation_response)
    if not chosen:
        return []

    pairs_spec = (
        item.get("elicitation", {})
        .get("tasks") or []
    )
    comparisons: list[tuple[str, str, str]] = []
    for task in pairs_spec:
        if task.get("type") != "pairwise_choice":
            continue
        for pair in task.get("pairs", []):
            pid = pair.get("id")
            pole_a = pair.get("pole_a")
            pole_b = pair.get("pole_b")
            if not (pid and pole_a and pole_b):
                continue
            if pole_a not in ALL_TRACKED_VALUES or pole_b not in ALL_TRACKED_VALUES:
                continue
            selection = chosen.get(pid)
            if selection == "label_a":
                comparisons.append((pole_a, pole_b, pole_a))
            elif selection == "label_b":
                comparisons.append((pole_a, pole_b, pole_b))
            # Unknown selection: skip

    return comparisons


def bradley_terry_profile(
    comparisons: list[tuple[str, str, str]],
    n_iter: int = 100,
    eps: float = 1e-8,
) -> dict[str, float]:
    """Estimate Schwartz value strengths from pairwise comparison wins.

    Uses Zermelo's (1929) iterative algorithm for Bradley-Terry MLE.
    Each tuple (pole_a, pole_b, winner) contributes one comparison.
    Values never observed return strength 0.

    Returns a dict mapping each Schwartz value to a normalized score in [0, 1].
    If there are fewer than 2 distinct values observed, returns empty dict.
    """
    if not comparisons:
        return {}

    # Count wins and opponents
    values_seen: set[str] = set()
    wins: dict[str, float] = {}
    games: dict[str, dict[str, float]] = {}  # games[i][j] = n times i faced j

    for pole_a, pole_b, winner in comparisons:
        values_seen.add(pole_a)
        values_seen.add(pole_b)
        wins[winner] = wins.get(winner, 0.0) + 1.0
        games.setdefault(pole_a, {})
        games.setdefault(pole_b, {})
        games[pole_a][pole_b] = games[pole_a].get(pole_b, 0.0) + 1.0
        games[pole_b][pole_a] = games[pole_b].get(pole_a, 0.0) + 1.0

    if len(values_seen) < 2:
        return {}

    # Initialize strengths uniformly
    strength: dict[str, float] = {v: 1.0 for v in values_seen}

    # Zermelo iteration: s_i = W_i / sum_j( n_ij / (s_i + s_j) )
    for _ in range(n_iter):
        new_strength: dict[str, float] = {}
        for v in values_seen:
            denom = sum(
                games[v].get(u, 0.0) / (strength[v] + strength[u])
                for u in values_seen
                if u != v and games.get(v, {}).get(u, 0.0) > 0
            )
            if denom < eps:
                new_strength[v] = strength[v]
            else:
                new_strength[v] = wins.get(v, 0.0) / denom

        # Normalize so max = 1 to prevent scale drift
        max_s = max(new_strength.values()) if new_strength else 1.0
        if max_s < eps:
            max_s = 1.0
        new_strength = {v: s / max_s for v, s in new_strength.items()}

        # Check convergence
        delta = sum(abs(new_strength[v] - strength[v]) for v in values_seen)
        strength = new_strength
        if delta < eps:
            break

    # Return canonical Schwartz profile + separate supplementary probes.
    # sanctity (and any future SUPPLEMENTARY_PROBES) are tracked but not mixed
    # into the main 10-dim profile so comparisons with Schwartz literature remain valid.
    canonical = {v: round(strength.get(v, 0.0), 4) for v in SCHWARTZ_VALUES}
    supplementary = {v: round(strength.get(v, 0.0), 4) for v in SUPPLEMENTARY_PROBES if v in strength}
    if supplementary:
        canonical["_supplementary"] = supplementary  # type: ignore[assignment]
    return canonical
