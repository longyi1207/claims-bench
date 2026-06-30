"""Parse L3 structured elicitation responses out of raw model output.

Model output is expected to contain a JSON block (optionally fenced in
``` markdown, optionally preceded/followed by prose) matching
data/schemas/revelation_response.schema.json, plus free-text reasoning.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "schemas" / "revelation_response.schema.json"

_FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_BRACE_RE = re.compile(r"\{.*\}", re.DOTALL)


class RevelationParseError(Exception):
    """Raised when no valid structured JSON block can be extracted."""


def _candidate_blobs(text: str) -> list[str]:
    candidates = [m.group(1) for m in _FENCE_RE.finditer(text)]
    if not candidates:
        m = _BRACE_RE.search(text)
        if m:
            candidates.append(m.group(0))
    return candidates


def extract_json_block(text: str) -> dict[str, Any]:
    """Extract the first parseable JSON object from model output.

    Tries fenced ```json blocks first (in case the model emits multiple
    JSON-looking fragments, e.g. one in reasoning prose), then falls back to
    the first balanced-looking {...} span.
    """
    for blob in _candidate_blobs(text):
        try:
            parsed = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise RevelationParseError("No parseable JSON object found in response")


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def parse_response(text: str, schema: dict | None = None) -> dict[str, Any]:
    """Extract and validate a structured response.

    Returns the parsed dict with an added ``_parse_status`` key:
    ``ok`` | ``non_compliant_format`` | ``schema_invalid``.
    On failure, returns a minimal dict carrying the status and raw text so
    callers can still log/inspect it rather than crashing the eval run.
    """
    schema = schema or load_schema()
    try:
        parsed = extract_json_block(text)
    except RevelationParseError:
        return {"_parse_status": "non_compliant_format", "_raw": text}

    try:
        jsonschema.validate(parsed, schema)
    except jsonschema.ValidationError as e:
        parsed["_parse_status"] = "schema_invalid"
        parsed["_validation_error"] = e.message
        return parsed

    parsed["_parse_status"] = "ok"
    return parsed


def extract_reasoning(text: str) -> str:
    """Best-effort extraction of the free-text reasoning portion (part B).

    Strips the first fenced/braced JSON block out of the text and returns
    what's left, trimmed. Not schema-validated — reasoning is free text.
    """
    for blob in _candidate_blobs(text):
        idx = text.find(blob)
        if idx != -1:
            text = text[:idx] + text[idx + len(blob) :]
            break
    return text.strip(" \n`")
