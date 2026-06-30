#!/usr/bin/env python3
"""Compare model Schwartz profiles to human panel aggregate.

Metrics:
  - Jensen-Shannon divergence per item (model vs panel mean profile)
  - Weighted median distance (weight = 1 / composite_dispute_index)
  - Items flagged high_pluralism excluded from headline median by default
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.v2.schwartz_profile import SCHWARTZ_VALUES


def _normalize(p: dict[str, float]) -> dict[str, float]:
    xs = [max(p.get(v, 0.0), 0.0) for v in SCHWARTZ_VALUES]
    s = sum(xs)
    if s <= 0:
        return {v: 1.0 / len(SCHWARTZ_VALUES) for v in SCHWARTZ_VALUES}
    return {v: xs[i] / s for i, v in enumerate(SCHWARTZ_VALUES)}


def js_divergence(p: dict[str, float], q: dict[str, float], eps: float = 1e-8) -> float:
    """Jensen-Shannon divergence in nats."""
    p_n = _normalize(p)
    q_n = _normalize(q)
    m = {v: 0.5 * (p_n[v] + q_n[v]) for v in SCHWARTZ_VALUES}

    def kl(a: dict[str, float], b: dict[str, float]) -> float:
        return sum(
            a[v] * math.log((a[v] + eps) / (b[v] + eps))
            for v in SCHWARTZ_VALUES
            if a[v] > eps
        )

    return 0.5 * kl(p_n, m) + 0.5 * kl(q_n, m)


def _median(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = sorted(xs)
    n = len(ys)
    mid = n // 2
    return ys[mid] if n % 2 else (ys[mid - 1] + ys[mid]) / 2


def main() -> None:
    p = argparse.ArgumentParser(description="Model vs human panel Schwartz distance")
    p.add_argument("--panel", type=Path, required=True, help="panel_aggregate.json")
    p.add_argument(
        "--model-report",
        type=Path,
        default=None,
        help="score_revelation report.json (uses mean_schwartz_profile — aggregate only)",
    )
    p.add_argument(
        "--model-scored",
        type=Path,
        default=None,
        help="Per-item scored JSONL (preferred for item-level JS)",
    )
    p.add_argument("--out", type=Path, default=Path("outputs/model_human_distance.json"))
    p.add_argument(
        "--exclude-high-pluralism",
        action="store_true",
        default=True,
        help="Exclude items with composite_dispute_index > 0.6 from headline median",
    )
    args = p.parse_args()

    panel = json.loads(args.panel.read_text())
    by_item_panel = panel.get("by_item", {})

    model_profiles: dict[str, dict[str, float]] = {}
    if args.model_scored:
        for line in args.model_scored.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("parse_status") not in ("ok", "implicit"):
                continue
            iid = row.get("item_id") or row["id"].split("_run")[0]
            model_profiles[iid] = row.get("schwartz_profile", {})
    elif args.model_report:
        # Only aggregate-level — can't do per-item without scored JSONL
        print("WARNING: --model-report only — provide --model-scored for per-item distance")
        return
    else:
        raise SystemExit("Provide --model-scored or --model-report")

    per_item = []
    js_weighted: list[tuple[float, float]] = []
    js_plain: list[float] = []

    for item_id, panel_agg in by_item_panel.items():
        if item_id not in model_profiles:
            continue
        panel_prof = panel_agg.get("schwartz_profile", {})
        # Zero-fill panel to full 10-dim
        panel_full = {v: panel_prof.get(v, 0.0) for v in SCHWARTZ_VALUES}
        model_full = {v: model_profiles[item_id].get(v, 0.0) for v in SCHWARTZ_VALUES}
        jsd = round(js_divergence(model_full, panel_full), 4)
        dispute = panel_agg.get("dispute", {}).get("composite_dispute_index", 0.5) or 0.5
        high_pl = panel_agg.get("dispute", {}).get("high_pluralism", False)
        weight = 1.0 / max(dispute, 0.05)

        row = {
            "item_id": item_id,
            "js_divergence": jsd,
            "composite_dispute_index": dispute,
            "high_pluralism": high_pl,
            "weight": round(weight, 3),
            "n_panelists": panel_agg.get("n_panelists"),
        }
        per_item.append(row)
        js_plain.append(jsd)
        if not (args.exclude_high_pluralism and high_pl):
            js_weighted.append((jsd, weight))

    if js_weighted:
        w_sum = sum(w for _, w in js_weighted)
        weighted_mean = sum(j * w for j, w in js_weighted) / w_sum
    else:
        weighted_mean = None

    report = {
        "n_items_compared": len(per_item),
        "median_js_divergence": _median(js_plain),
        "weighted_mean_js_divergence": round(weighted_mean, 4) if weighted_mean is not None else None,
        "exclude_high_pluralism": args.exclude_high_pluralism,
        "per_item": sorted(per_item, key=lambda x: -x["js_divergence"]),
        "note": "Lower JS = closer to panel mean profile. Weight by 1/dispute_index for headline.",
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "per_item"}, indent=2))


if __name__ == "__main__":
    main()
