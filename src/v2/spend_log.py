"""Append-only spend log per BUDGET.md: outputs/spend_log.jsonl.

No cost estimation is attempted here — provider pricing changes too often
to hardcode reliably, and a fabricated number is worse than none. Pass
`est_usd` explicitly (e.g. from the provider's dashboard) once known.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

DEFAULT_LOG_PATH = Path("outputs/spend_log.jsonl")


def log_spend(
    provider: str,
    model: str,
    items: int,
    est_usd: float | None = None,
    notes: str = "",
    path: Path = DEFAULT_LOG_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "provider": provider,
        "model": model,
        "items": items,
        "est_usd": est_usd,
        "notes": notes,
    }
    with path.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def total_spend(path: Path = DEFAULT_LOG_PATH) -> float:
    if not path.exists():
        return 0.0
    total = 0.0
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            total += entry.get("est_usd") or 0.0
    return total
