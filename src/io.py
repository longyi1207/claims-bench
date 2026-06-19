"""JSONL I/O helpers."""

from __future__ import annotations

import json
from pathlib import Path


def load_jsonl(path: Path | str) -> list[dict]:
    path = Path(path)
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path | str, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def index_by_id(rows: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in rows}
