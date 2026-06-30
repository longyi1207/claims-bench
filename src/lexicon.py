"""Lexicon scoring and rollup for CLAIMS-Bench v0.5+."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

LEXICON_PATH = Path(__file__).resolve().parent.parent / "data" / "values_lexicon.json"


@lru_cache(maxsize=1)
def load_lexicon() -> dict:
    return json.loads(LEXICON_PATH.read_text())


def _pattern_score(text: str, patterns: list[str]) -> float:
    if not text or text.startswith("[GENERATION_ERROR"):
        return 0.0
    hits = sum(1 for p in patterns if re.search(p, text, re.I))
    if hits == 0:
        return 0.0
    return min(1.0, 0.35 + 0.22 * min(hits, 3))


def score_lexicon_entries(response: str) -> dict[str, float]:
    """Score all lexicon entries by pattern activation."""
    lex = load_lexicon()
    scores: dict[str, float] = {}
    for e in lex["entries"]:
        patterns = e.get("patterns") or []
        if not patterns and e.get("keywords"):
            patterns = [rf"\b{re.escape(k)}\b" for k in e["keywords"][:3]]
        scores[e["id"]] = _pattern_score(response, patterns) if patterns else 0.0
    return scores


def rollup_mid_level(lexicon_scores: dict[str, float]) -> dict[str, float]:
    lex = load_lexicon()
    out: dict[str, float] = {}
    for mid_id, entry_ids in lex["rollup"]["mid_to_entries"].items():
        vals = [lexicon_scores.get(eid, 0.0) for eid in entry_ids]
        active = [v for v in vals if v > 0]
        # Mean of active entries; 0 if none hit
        out[mid_id] = sum(active) / len(active) if active else 0.0
    return out


def rollup_parent_values(lexicon_scores: dict[str, float]) -> dict[str, float]:
    lex = load_lexicon()
    out: dict[str, float] = {}
    for parent, entry_ids in lex["rollup"]["parent_to_entries"].items():
        vals = [lexicon_scores.get(eid, 0.0) for eid in entry_ids]
        active = [v for v in vals if v > 0]
        out[parent] = sum(active) / len(active) if active else 0.0
    return out


def merge_value_scores(direct: dict[str, float], lexicon_rollup: dict[str, float]) -> dict[str, float]:
    """Combine direct Layer-1 patterns with lexicon rollup (max of each)."""
    keys = set(direct) | set(lexicon_rollup)
    return {k: max(direct.get(k, 0.0), lexicon_rollup.get(k, 0.0)) for k in keys}


def top_lexicon_entries(lexicon_scores: dict[str, float], n: int = 10) -> list[dict]:
    ranked = sorted(lexicon_scores.items(), key=lambda x: -x[1])
    lex = load_lexicon()
    labels = {e["id"]: e["label"] for e in lex["entries"]}
    return [
        {"id": k, "label": labels.get(k, k), "score": round(v, 4)}
        for k, v in ranked[:n]
        if v > 0
    ]


def top_mid_level(mid_scores: dict[str, float], n: int = 10) -> list[dict]:
    lex = load_lexicon()
    labels = {m["id"]: m["label"] for m in lex["mid_level"]}
    ranked = sorted(mid_scores.items(), key=lambda x: -x[1])
    return [
        {"id": k, "label": labels.get(k, k), "score": round(v, 4), "parent_value": lex["rollup"]["mid_to_parent"].get(k)}
        for k, v in ranked[:n]
        if v > 0
    ]


def tag_item_lexicon(item: dict) -> list[str]:
    """Suggest lexicon entry ids for an item from metadata."""
    lex = load_lexicon()
    text = " ".join(
        [
            item.get("prompt", ""),
            item.get("rubric_notes", ""),
            " ".join(item.get("tags") or []),
            " ".join(item.get("value_profile", {}).get("relevant_values", [])),
        ]
    ).lower()

    scored = []
    for e in lex["entries"]:
        kws = [k.lower() for k in (e.get("keywords") or [])]
        hits = sum(1 for k in kws if k in text)
        if hits:
            scored.append((e["id"], hits))
    scored.sort(key=lambda x: -x[1])
    return [s[0] for s in scored[:8]]
