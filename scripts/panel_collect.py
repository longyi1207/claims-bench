#!/usr/bin/env python3
"""CLI to record or import human panel responses for L3 revelation items."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io import load_jsonl
from src.v2.revelation_parse import load_schema, parse_response

DEFAULT_DATA = ROOT / "data" / "v2_revelation.jsonl"
DEFAULT_PANEL_ITEMS = [
    "revelation_003",
    "revelation_005",
    "revelation_016",
    "revelation_020",
    "revelation_022",
    "revelation_026",
    "revelation_027",
    "revelation_028",
]
RESPONSES_DIR = ROOT / "data" / "panel" / "responses"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_panel_items(data_path: Path, item_ids: list[str]) -> list[dict]:
    by_id = {row["id"]: row for row in load_jsonl(data_path)}
    missing = [i for i in item_ids if i not in by_id]
    if missing:
        raise SystemExit(f"Unknown panel item ids: {missing}")
    return [by_id[i] for i in item_ids]


def _format_item_prompt(item: dict) -> str:
    elicitation = item.get("elicitation", {})
    lines = [item["prompt"].strip(), ""]
    for task in elicitation.get("tasks", []):
        t = task.get("type")
        if t == "rank_values":
            lines.append(f"Rank task: {task['instruction']}")
        elif t == "pairwise_choice":
            lines.append("Pairwise choices:")
            for pair in task["pairs"]:
                lines.append(f"  [{pair['id']}] (A) {pair['label_a']}  vs  (B) {pair['label_b']}")
        elif t == "epistemic_prior":
            lines.append(f"Epistemic: {task['question']}")
            lines.append(f"  Options: {', '.join(task['options'])}")
    lines.append("")
    lines.append(elicitation.get("output_instruction", "").strip())
    return "\n".join(lines)


def cmd_record(args: argparse.Namespace) -> None:
    items = _load_panel_items(args.data, args.items)
    schema = load_schema()
    out_path = RESPONSES_DIR / f"{args.panelist_id}.jsonl"
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    existing = {r["item_id"] for r in load_jsonl(out_path)} if out_path.exists() else set()
    print(f"Panelist: {args.panelist_id} → {out_path}")
    if existing:
        print(f"Resuming — skipping {len(existing)} completed items.")

    with out_path.open("a") as f:
        for item in items:
            if item["id"] in existing:
                continue
            print("\n" + "=" * 72)
            print(_format_item_prompt(item))
            print("=" * 72)
            print("Paste full response (JSON block + reasoning), then blank line + END:")
            chunks: list[str] = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                chunks.append(line)
            response_text = "\n".join(chunks).strip()
            structured = parse_response(response_text, schema)

            row = {
                "item_id": item["id"],
                "panelist_id": args.panelist_id,
                "timestamp": _utc_now(),
                "demographics": args.demographics or {},
                "elicitation_response": {
                    k: structured[k]
                    for k in ("rank_values", "pairwise", "epistemic_prior")
                    if k in structured
                },
                "free_reasoning": response_text.split("```")[-1].strip() if "```" in response_text else "",
                "confidence": args.confidence,
                "raw_response": response_text,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            print(f"Saved {item['id']} (parse={structured.get('_parse_status')})")

    print(f"\nDone. Run: python3 scripts/panel_aggregate.py --responses-dir {RESPONSES_DIR}")


def cmd_import(args: argparse.Namespace) -> None:
    schema = load_schema()
    src = Path(args.file)
    out_path = RESPONSES_DIR / f"{args.panelist_id}.jsonl"
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    n_ok = 0
    with out_path.open("a") as out:
        for line in src.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            row.setdefault("panelist_id", args.panelist_id)
            row.setdefault("timestamp", _utc_now())
            raw = row.get("raw_response") or row.get("response", "")
            if raw:
                structured = parse_response(raw, schema)
                row.setdefault("elicitation_response", {})
                for k in ("rank_values", "pairwise", "epistemic_prior"):
                    if k in structured and k not in row["elicitation_response"]:
                        row["elicitation_response"][k] = structured[k]
                if structured.get("_parse_status") == "ok":
                    n_ok += 1
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Imported → {out_path} ({n_ok} parse-ok rows)")


def main() -> None:
    p = argparse.ArgumentParser(description="Collect human panel responses for CLAIMS-Bench L3")
    sub = p.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("export", help="Write panel survey markdown")
    ex.add_argument("--out-dir", type=Path, default=ROOT / "data" / "panel" / "survey")
    ex.add_argument("--data", type=Path, default=DEFAULT_DATA)

    rec = sub.add_parser("record", help="Interactive CLI session")
    rec.add_argument("--panelist-id", required=True)
    rec.add_argument("--data", type=Path, default=DEFAULT_DATA)
    rec.add_argument("--items", nargs="+", default=DEFAULT_PANEL_ITEMS)
    rec.add_argument("--confidence", type=int, default=3)
    rec.add_argument("--demographics", type=json.loads, default=None)

    imp = sub.add_parser("import", help="Import JSONL file for a panelist")
    imp.add_argument("--panelist-id", required=True)
    imp.add_argument("--file", type=Path, required=True)

    args = p.parse_args()
    if args.cmd == "export":
        sys.path.insert(0, str(ROOT / "scripts"))
        import export_panel_survey  # noqa: E402

        export_panel_survey.main(args)
    elif args.cmd == "record":
        cmd_record(args)
    elif args.cmd == "import":
        cmd_import(args)


if __name__ == "__main__":
    main()
