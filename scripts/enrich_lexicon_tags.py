#!/usr/bin/env python3
"""Enrich benchmark items with lexicon_tags and produce v0.5 values tier."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.io import load_jsonl, write_jsonl
from src.lexicon import load_lexicon, tag_item_lexicon

DATA = ROOT / "data"


def enrich_row(row: dict) -> dict:
    row = dict(row)
    tags = tag_item_lexicon(row)
    if tags:
        row["lexicon_tags"] = tags
    if row.get("tier") == "values":
        row["version"] = "0.5"
    return row


def enrich_file(path: Path, out: Path | None = None) -> list[dict]:
    rows = [enrich_row(r) for r in load_jsonl(path)]
    if out:
        write_jsonl(out, rows)
    return rows


def main() -> None:
    # Enrich values tier
    values_in = DATA / "v0.4_values48.jsonl"
    values_out = DATA / "v0.5_values48.jsonl"
    values_rows = enrich_file(values_in, values_out)
    tagged = sum(1 for r in values_rows if r.get("lexicon_tags"))
    print(f"Wrote {values_out} ({len(values_rows)} items, {tagged} with lexicon_tags)")

    # Merge full dataset
    core = enrich_file(DATA / "v0.3_full160.jsonl")
    full = core + values_rows
    full_out = DATA / "v0.5_full208.jsonl"
    write_jsonl(full_out, full)
    print(f"Wrote {full_out} ({len(full)} items)")


if __name__ == "__main__":
    main()
