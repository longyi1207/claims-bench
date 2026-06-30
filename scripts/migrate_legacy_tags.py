#!/usr/bin/env python3
"""Add v2 multidimensional tags to v0.5 legacy items, per docs/TAXONOMY.md.

Legacy fields (conflict_type, norm_classes, stakeholders, ...) are kept as-is.
New top-level fields added: domain, uncertainty, layer.
New `tags` object added (does not overwrite the legacy free-text `tags` list,
which is renamed to `legacy_keywords`).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# legacy conflict_type -> (domain, [principle_tension], layer)
# Table rows from docs/TAXONOMY.md; extra conflict_types found in v0.5 data
# (developer_vs_society, hhh_interpersonal, intent_vs_interest, society_vs_user)
# are mapped by analogy and noted in docs/V2_DELTA.md.
CONFLICT_TYPE_MAP: dict[str, tuple[str, list[str], str]] = {
    "malicious_user": ("harm_compliance", ["autonomy_vs_nonmaleficence"], "L1_stakeholder"),
    "rights_vs_welfare": (
        "resource_allocation",
        ["autonomy_vs_beneficence", "privacy_vs_collective_welfare"],
        "L2_principle",
    ),
    "developer_vs_user": ("developer_incentive", ["autonomy_vs_beneficence"], "L1_stakeholder"),
    "developer_vs_society": (
        "developer_incentive",
        ["beneficence_vs_nonmaleficence"],
        "L1_stakeholder",
    ),
    "pluralism_dispute": ("cultural_practice", ["honesty_vs_beneficence"], "L2_principle"),
    "hhh_intrapersonal": ("epistemic_integrity", ["honesty_vs_beneficence"], "L2_principle"),
    "hhh_interpersonal": ("epistemic_integrity", ["honesty_vs_beneficence"], "L2_principle"),
    "temporal_shift": ("cultural_practice", ["tradition_vs_self_direction"], "L2_principle"),
    "intent_vs_interest": ("harm_compliance", ["autonomy_vs_beneficence"], "L1_stakeholder"),
    "society_vs_user": ("resource_allocation", ["autonomy_vs_beneficence"], "L1_stakeholder"),
}

# legacy difficulty already uses the v2 uncertainty vocabulary (see docs/TAXONOMY.md)
DIFFICULTY_TO_UNCERTAINTY = {
    "gold_clear": "gold_clear",
    "structured_tradeoff": "structured_tradeoff",
    "ambiguous": "ambiguous",
}


def stakeholder_config_for(item: dict[str, Any]) -> str | list[str] | None:
    gabriel = item.get("gabriel_misalignment_type")
    if gabriel is not None:
        return f"gabriel_{gabriel}"
    if item.get("conflict_type") == "malicious_user":
        return "malicious_user"
    if len(item.get("stakeholders") or []) >= 3:
        return "multi_stakeholder"
    return None


def migrate_item(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    conflict_type = item.get("conflict_type")
    domain, principle_tension, layer = CONFLICT_TYPE_MAP.get(
        conflict_type, ("harm_compliance", [], "L1_stakeholder")
    )
    uncertainty = DIFFICULTY_TO_UNCERTAINTY.get(item.get("difficulty"), "structured_tradeoff")

    out["domain"] = domain
    out["uncertainty"] = uncertainty
    out["layer"] = layer

    tags: dict[str, Any] = {
        "epistemic_mode": "normative",
        "principle_tension": principle_tension,
        "legacy_conflict_type": conflict_type,
    }
    stakeholder_config = stakeholder_config_for(item)
    if stakeholder_config is not None:
        tags["stakeholder_config"] = stakeholder_config

    out["tags"] = tags
    if "tags" in item and isinstance(item["tags"], list):
        out["legacy_keywords"] = item["tags"]

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/v0.5_full208.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/v0.5_full208_v2tags.jsonl"))
    parser.add_argument("--limit", type=int, default=None, help="Migrate only first N items (for review)")
    args = parser.parse_args()

    items = []
    with args.input.open() as f:
        for i, line in enumerate(f):
            if args.limit is not None and i >= args.limit:
                break
            items.append(json.loads(line))

    migrated = [migrate_item(item) for item in items]

    unmapped = sorted({m["tags"]["legacy_conflict_type"] for m in migrated} - set(CONFLICT_TYPE_MAP))
    if unmapped:
        print(f"WARNING: conflict_types with no explicit mapping (used fallback): {unmapped}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for m in migrated:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    print(f"Migrated {len(migrated)} items -> {args.output}")


if __name__ == "__main__":
    main()
