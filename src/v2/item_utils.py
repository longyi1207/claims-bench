"""Helpers for L3 item typing (structured vs implicit)."""

from __future__ import annotations


def is_implicit_item(item: dict) -> bool:
    """True for behavioral + temporal shift items (free-text, judge-inferred profile)."""
    if item.get("elicitation_type") == "implicit":
        return True
    elicitation = item.get("elicitation") or {}
    return elicitation.get("format") == "implicit"


def is_structured_item(item: dict) -> bool:
    return not is_implicit_item(item)
