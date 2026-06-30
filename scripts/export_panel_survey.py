#!/usr/bin/env python3
"""Export human panel survey packet (8 L3 structured items)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io import load_jsonl

PANEL_ITEMS = [
    "revelation_003",
    "revelation_005",
    "revelation_016",
    "revelation_020",
    "revelation_022",
    "revelation_026",
    "revelation_027",
    "revelation_028",
]

SCHWARTZ_GLOSS = {
    "self_direction": "independent thought, autonomy, exploring",
    "stimulation": "excitement, novelty, challenge",
    "hedonism": "pleasure, enjoyment",
    "achievement": "personal success, competence, ambition",
    "power": "social status, dominance, control",
    "security": "safety, stability, predictability",
    "conformity": "restraint, following rules, fitting in",
    "tradition": "respect for customs, religion, cultural continuity",
    "benevolence": "care for close others, loyalty, family",
    "universalism": "tolerance, justice, protection for all",
}


def _format_item(item: dict, idx: int) -> str:
    elicitation = item.get("elicitation", {})
    lines = [
        f"## Item {idx}: {item['id']} ({item.get('domain', '')})",
        "",
        item["prompt"].strip(),
        "",
    ]
    for task in elicitation.get("tasks", []):
        t = task.get("type")
        if t == "rank_values":
            lines.append("### Rank these values (1 = most important to your recommendation)")
            lines.append(task["instruction"])
            lines.append("")
            lines.append("Values: " + ", ".join(SCHWARTZ_GLOSS.keys()))
            lines.append("")
            for v, gloss in SCHWARTZ_GLOSS.items():
                lines.append(f"- **{v}**: {gloss}")
        elif t == "pairwise_choice":
            lines.append("### Pairwise choices (pick A or B for each)")
            for pair in task["pairs"]:
                lines.append(f"- **{pair['id']}**: (A) {pair['label_a']}  OR  (B) {pair['label_b']}")
        elif t == "epistemic_prior":
            lines.append(f"### Epistemic stance: {task['question']}")
            for opt in task["options"]:
                lines.append(f"- {opt}")
    lines.append("")
    lines.append("### Free reasoning (≤300 words)")
    lines.append("_Explain your ranking and choices. No single right answer._")
    lines.append("")
    return "\n".join(lines)


def main(args: argparse.Namespace | None = None) -> None:
    if args is None:
        p = argparse.ArgumentParser(description="Export panel survey packet")
        p.add_argument("--out-dir", type=Path, default=ROOT / "data" / "panel" / "survey")
        p.add_argument("--data", type=Path, default=ROOT / "data" / "v2_revelation.jsonl")
        args = p.parse_args()

    by_id = {r["id"]: r for r in load_jsonl(args.data)}
    items = [by_id[i] for i in PANEL_ITEMS]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    md_parts = [
        "# CLAIMS-Bench Human Panel Survey (v2)",
        "",
        "**Time:** ~30 minutes | **Items:** 8 | **No right answers**",
        "",
        "We study how people prioritize values under uncertainty. Your responses are anonymous.",
        "",
        "---",
        "",
    ]
    for i, item in enumerate(items, 1):
        md_parts.append(_format_item(item, i))
        md_parts.append("---")
        md_parts.append("")

    survey_md = args.out_dir / "panel_survey.md"
    survey_md.write_text("\n".join(md_parts), encoding="utf-8")

    manifest = {
        "item_ids": PANEL_ITEMS,
        "n_items": len(PANEL_ITEMS),
        "collect_command": "python3 scripts/panel_collect.py record --panelist-id pXX",
        "aggregate_command": "python3 scripts/panel_aggregate.py",
        "items": [
            {"id": it["id"], "domain": it.get("domain"), "pair_id": it.get("pair_id")}
            for it in items
        ],
    }
    (args.out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )

    recruit = args.out_dir.parent / "RECRUIT.md"
    recruit.write_text(
        """# Human Panel Recruitment (v2 pilot)

## Target
- **n=5** unpaid friends first (protocol debug)
- **n=10** paid ($25/session) after protocol stable

## Diversity axes (self-report)
Culture/regions lived, professional background, age, religious/secular.

## Session flow
1. Consent + framing (2 min) — see `survey/panel_survey.md` intro
2. Training item optional: `revelation_001` (not in main packet)
3. Main: 8 items in `survey/panel_survey.md` (~20 min)
4. Debrief notes optional

## Recording responses
```bash
cd code/claims_bench
python3 scripts/panel_collect.py record --panelist-id p01
# or import from Google Form export:
python3 scripts/panel_collect.py import --panelist-id p02 --file form_export.jsonl
```

## After collection
```bash
python3 scripts/panel_aggregate.py --responses-dir data/panel/responses
python3 scripts/model_human_distance.py \\
  --panel data/panel/panel_aggregate.json \\
  --model-report outputs/baseline_v2_structured/gpt-4o_report.json
```

Store responses in `data/panel/responses/<panelist_id>.jsonl` (gitignore if PII).
""",
        encoding="utf-8",
    )

    print(f"Wrote {survey_md}")
    print(f"Wrote {args.out_dir / 'manifest.json'}")
    print(f"Wrote {recruit}")


if __name__ == "__main__":
    main()
