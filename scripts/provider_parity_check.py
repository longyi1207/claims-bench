#!/usr/bin/env python3
"""Did switching provider (or harness) change what the model says?

Two things changed at once in August 2026: generation moved from the hand-rolled
loop to Inspect, and OpenAI calls moved from api.openai.com to Azure OpenAI
(repo policy — Azure credits vs. a personal card, `../../docs/AZURE.md`). Both are
supposed to be measurement-neutral. Neither is neutral by assumption:

- **Azure applies content filtering that api.openai.com does not.** Several L3
  items are historically sensitive (1943 Netherlands harboring, colonial rebellion
  loyalty, refusing a kill order). A filtered refusal would enter the pipeline as a
  parse failure or a flattened profile and read as a *value commitment of the
  model* — the exact failure mode this benchmark is supposed to detect in others.
- Snapshot pinning differs: Azure deploys `gpt-4o 2024-11-20` explicitly, while
  `gpt-4o` on api.openai.com is a moving alias.

This script diffs two runs of the *same items* and reports where they disagree:
refusal/filter markers, parse status, and per-item Schwartz profile distance.

    python scripts/provider_parity_check.py \\
        --a outputs/expansion_044_080/gpt-4o_scored.jsonl \\
        --b outputs/expansion_044_080_azure/gpt-4o_scored.jsonl \\
        --label-a "openai-direct + legacy loop" \\
        --label-b "azure + inspect" \\
        --responses-a outputs/expansion_044_080/gpt-4o_responses.jsonl \\
        --responses-b outputs/expansion_044_080_azure/gpt-4o_responses.jsonl

Exit status is 1 if any item shows a refusal/filter marker on one side only, or a
parse-status flip — i.e. something a human must look at before trusting the numbers.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io import load_jsonl
from src.v2.schwartz_profile import SCHWARTZ_VALUES

# Substrings that indicate the *deployment* refused, not the model deliberating.
FILTER_MARKERS = [
    "content management policy",
    "content_filter",
    "responsible ai",
    "was filtered",
    "i'm sorry, but i can't assist",
    "i cannot assist with that request",
    "[generation_error",
]


def looks_filtered(text: str) -> list[str]:
    low = (text or "").lower()
    return [m for m in FILTER_MARKERS if m in low]


def profile_distance(pa: dict, pb: dict) -> float:
    """L1 distance over the 10 Schwartz dimensions (0 = identical)."""
    return round(
        sum(abs(float(pa.get(v, 0.0)) - float(pb.get(v, 0.0))) for v in SCHWARTZ_VALUES), 4
    )


def index(rows: list[dict]) -> dict[str, dict]:
    return {r.get("item_id") or r["id"].rsplit("_run", 1)[0]: r for r in rows}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--a", type=Path, required=True, help="scored.jsonl, side A (reference)")
    p.add_argument("--b", type=Path, required=True, help="scored.jsonl, side B (new path)")
    p.add_argument("--responses-a", type=Path, default=None)
    p.add_argument("--responses-b", type=Path, default=None)
    p.add_argument("--label-a", default="A")
    p.add_argument("--label-b", default="B")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    a, b = index(load_jsonl(args.a)), index(load_jsonl(args.b))
    resp_a = index(load_jsonl(args.responses_a)) if args.responses_a else {}
    resp_b = index(load_jsonl(args.responses_b)) if args.responses_b else {}

    common = sorted(set(a) & set(b))
    only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))

    parse_flips, filtered, distances = [], [], []
    for item_id in common:
        ra, rb = a[item_id], b[item_id]
        if ra.get("parse_status") != rb.get("parse_status"):
            parse_flips.append(
                {"item_id": item_id, args.label_a: ra.get("parse_status"), args.label_b: rb.get("parse_status")}
            )
        ma = looks_filtered(resp_a.get(item_id, {}).get("response", "") or ra.get("reasoning_text", ""))
        mb = looks_filtered(resp_b.get(item_id, {}).get("response", "") or rb.get("reasoning_text", ""))
        if bool(ma) != bool(mb):
            filtered.append({"item_id": item_id, args.label_a: ma, args.label_b: mb})
        if ra.get("schwartz_profile") and rb.get("schwartz_profile"):
            distances.append((item_id, profile_distance(ra["schwartz_profile"], rb["schwartz_profile"])))

    dists = [d for _, d in distances]
    mean_d = round(sum(dists) / len(dists), 4) if dists else None
    worst = sorted(distances, key=lambda x: -x[1])[:8]

    print(f"\n## Provider/harness parity: {args.label_a}  vs  {args.label_b}\n")
    print(f"items compared: {len(common)}   only in A: {len(only_a)}   only in B: {len(only_b)}")
    print(f"parse-status flips: {len(parse_flips)}")
    print(f"one-sided refusal/filter markers: {len(filtered)}")
    print(f"mean per-item L1 profile distance (0-20 scale): {mean_d}")
    if worst:
        print("\nlargest per-item profile differences:")
        for item_id, d in worst:
            print(f"  {item_id}: {d}")
    for row in parse_flips:
        print(f"  PARSE FLIP {row}")
    for row in filtered:
        print(f"  FILTER MARKER {row}")

    report = {
        "label_a": args.label_a,
        "label_b": args.label_b,
        "n_common": len(common),
        "only_a": only_a,
        "only_b": only_b,
        "parse_flips": parse_flips,
        "one_sided_filter_markers": filtered,
        "mean_l1_profile_distance": mean_d,
        "per_item_distance": dict(distances),
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"\nwrote {args.out}")

    if parse_flips or filtered:
        print("\nFAIL: differences need a human look before these runs are pooled.")
        sys.exit(1)
    print("\nOK: no parse flips, no one-sided filter markers.")


if __name__ == "__main__":
    main()
