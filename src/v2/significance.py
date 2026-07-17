"""Statistical significance testing for cross-model Schwartz profile comparisons.

Addresses a gap flagged in NOVELTY_AND_THEORY_REVIEW_2026-07.md: prior CLAIMS-Bench
baselines (and the closest published neighbor, ConflictScope) report profile
differences between models as plain means with no confidence intervals or
hypothesis tests. This module fixes that.

No scipy/statsmodels dependency -- bootstrap, permutation tests, Cohen's d, and
Benjamini-Hochberg FDR correction are all straightforward in pure numpy.

Two comparison modes:
  - `bootstrap_ci` / `permutation_test`: treat each item's replicate runs as
    exchangeable observations (flat bootstrap). Simple, but ignores that
    replicates of the same item are more similar to each other than to
    replicates of a different item.
  - `item_cluster_bootstrap_ci`: two-stage (item, then replicate-within-item)
    resampling -- a nonparametric stand-in for a mixed-effects model with item
    as a random effect, without requiring statsmodels. Preferred when replicate
    data is available; falls back to flat bootstrap for n_replicates=1.
"""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np

SCHWARTZ_VALUES = [
    "self_direction", "stimulation", "hedonism", "achievement", "power",
    "security", "conformity", "tradition", "benevolence", "universalism",
]


def bootstrap_ci(
    values: Sequence[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 0
) -> dict:
    """Flat (non-hierarchical) percentile bootstrap CI for the mean."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return {"mean": None, "ci_low": None, "ci_high": None, "n": 0}
    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_boot)
    n = arr.size
    for i in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means[i] = sample.mean()
    lo, hi = np.percentile(boot_means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"mean": float(arr.mean()), "ci_low": float(lo), "ci_high": float(hi), "n": int(n)}


def item_cluster_bootstrap_ci(
    per_item_replicates: dict[str, Sequence[float]],
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict:
    """Two-stage bootstrap: resample items with replacement, then resample
    replicates within each sampled item with replacement. Accounts for
    within-item correlation the way a mixed-effects model (item as random
    intercept) would, without requiring statsmodels."""
    item_ids = list(per_item_replicates.keys())
    if not item_ids:
        return {"mean": None, "ci_low": None, "ci_high": None, "n_items": 0}
    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_boot)
    arrays = {k: np.asarray(v, dtype=float) for k, v in per_item_replicates.items()}
    n_items = len(item_ids)
    for i in range(n_boot):
        sampled_items = rng.choice(item_ids, size=n_items, replace=True)
        pooled = []
        for it in sampled_items:
            a = arrays[it]
            if a.size == 0:
                continue
            pooled.append(rng.choice(a, size=a.size, replace=True))
        if not pooled:
            boot_means[i] = np.nan
            continue
        boot_means[i] = np.concatenate(pooled).mean()
    boot_means = boot_means[~np.isnan(boot_means)]
    grand_mean = np.mean([arr.mean() for arr in arrays.values() if arr.size])
    lo, hi = np.percentile(boot_means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {
        "mean": float(grand_mean),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "n_items": n_items,
        "n_boot_valid": int(boot_means.size),
    }


def permutation_test(
    group_a: Sequence[float], group_b: Sequence[float], n_perm: int = 5000, seed: int = 0
) -> dict:
    """Two-sided permutation test on the difference in means."""
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        return {"observed_diff": None, "p_value": None, "n_a": a.size, "n_b": b.size}
    observed = a.mean() - b.mean()
    pooled = np.concatenate([a, b])
    n_a = a.size
    rng = np.random.default_rng(seed)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pooled)
        perm_diff = pooled[:n_a].mean() - pooled[n_a:].mean()
        if abs(perm_diff) >= abs(observed):
            count += 1
    p_value = (count + 1) / (n_perm + 1)  # add-one smoothing, avoids p=0
    return {"observed_diff": float(observed), "p_value": float(p_value), "n_a": int(n_a), "n_b": int(n_b := b.size)}


def cohens_d(group_a: Sequence[float], group_b: Sequence[float]) -> float | None:
    """Cohen's d using pooled standard deviation."""
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size < 2 or b.size < 2:
        return None
    n_a, n_b = a.size, b.size
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    pooled_sd = math.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    if pooled_sd == 0:
        return None
    return float((a.mean() - b.mean()) / pooled_sd)


def benjamini_hochberg(p_values: Sequence[float], alpha: float = 0.05) -> list[bool]:
    """Benjamini-Hochberg FDR correction. Returns a boolean list (same order
    as input) of which hypotheses remain significant after correction."""
    p = np.asarray(p_values, dtype=float)
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    thresholds = (np.arange(1, n + 1) / n) * alpha
    below = ranked <= thresholds
    if not below.any():
        return [False] * n
    max_rank = np.max(np.where(below)[0])
    significant = np.zeros(n, dtype=bool)
    significant[order[: max_rank + 1]] = True
    return significant.tolist()


def compare_models_on_dimension(
    model_a_per_item: dict[str, Sequence[float]],
    model_b_per_item: dict[str, Sequence[float]],
    n_boot: int = 2000,
    n_perm: int = 5000,
    seed: int = 0,
) -> dict:
    """Full comparison for one Schwartz dimension between two models, using
    per-item replicate data. Returns CIs (item-cluster bootstrap), a
    permutation-test p-value (flat, on all replicate observations pooled),
    and Cohen's d on per-item means (one observation per item, avoiding
    pseudo-replication from treating replicates as independent for the
    effect-size calculation)."""
    ci_a = item_cluster_bootstrap_ci(model_a_per_item, n_boot=n_boot, seed=seed)
    ci_b = item_cluster_bootstrap_ci(model_b_per_item, n_boot=n_boot, seed=seed + 1)

    flat_a = [v for vals in model_a_per_item.values() for v in vals]
    flat_b = [v for vals in model_b_per_item.values() for v in vals]
    perm = permutation_test(flat_a, flat_b, n_perm=n_perm, seed=seed)

    item_means_a = [float(np.mean(v)) for v in model_a_per_item.values() if len(v)]
    item_means_b = [float(np.mean(v)) for v in model_b_per_item.values() if len(v)]
    d = cohens_d(item_means_a, item_means_b)

    return {
        "model_a": ci_a,
        "model_b": ci_b,
        "permutation_p_value": perm["p_value"],
        "cohens_d_on_item_means": d,
    }


def compare_models_all_dimensions(
    model_a_profiles: dict[str, dict[str, Sequence[float]]],
    model_b_profiles: dict[str, dict[str, Sequence[float]]],
    n_boot: int = 2000,
    n_perm: int = 5000,
    fdr_alpha: float = 0.05,
) -> dict:
    """model_X_profiles: {item_id: {schwartz_value: [replicate_1, replicate_2, ...]}}.
    Runs compare_models_on_dimension for all 10 Schwartz values, then applies
    Benjamini-Hochberg correction across the resulting 10 p-values."""
    per_dim = {}
    p_values = []
    for i, value in enumerate(SCHWARTZ_VALUES):
        a_per_item = {
            item: profile.get(value, []) for item, profile in model_a_profiles.items()
        }
        b_per_item = {
            item: profile.get(value, []) for item, profile in model_b_profiles.items()
        }
        result = compare_models_on_dimension(a_per_item, b_per_item, n_boot=n_boot, n_perm=n_perm, seed=i)
        per_dim[value] = result
        p_values.append(result["permutation_p_value"] if result["permutation_p_value"] is not None else 1.0)

    significant_flags = benjamini_hochberg(p_values, alpha=fdr_alpha)
    for value, sig in zip(SCHWARTZ_VALUES, significant_flags):
        per_dim[value]["significant_after_fdr"] = bool(sig)

    return per_dim
