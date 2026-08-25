"""Parity tests for the Inspect port of the L3 pipeline.

The migration risk that actually matters is silent prompt drift: if the Inspect
task sends a slightly different prompt than `run_eval_v2.py` did, every number in
the paper becomes non-comparable and nothing errors. These tests pin the wire
format against the legacy path for all 80 items, at zero API cost.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from run_eval import build_messages
from run_eval_v2 import build_elicitation_instructions, build_messages_v2
from src.io import load_jsonl
from src.v2.schwartz_profile import SCHWARTZ_VALUES

inspect_task = pytest.importorskip(
    "inspect_task", reason="inspect-ai not installed (pip install -r requirements.txt)"
)

DATA = Path(__file__).parent.parent / "data" / "v2_revelation.jsonl"
ITEMS = load_jsonl(DATA)


def legacy_wire_messages(item: dict) -> list[dict]:
    """Exactly what `generate_one_v2()` hands to a backend today.

    It does not call `build_messages_v2()`; it mutates the item's prompt and goes
    through `run_eval.build_messages()`. Reproduced here so the parity assertion
    is against the code path that actually produced the published results.
    """
    item_for_backend = dict(item)
    item_for_backend["prompt"] = (
        item["prompt"].rstrip() + "\n\n" + build_elicitation_instructions(item)
    )
    return build_messages(item_for_backend)


def test_items_present():
    assert len(ITEMS) == 80


@pytest.mark.parametrize("item", ITEMS, ids=[i["id"] for i in ITEMS])
def test_inspect_prompt_matches_legacy_wire_format(item):
    sample = inspect_task.record_to_sample(item)
    got = [{"role": m.role, "content": m.content} for m in sample.input]
    assert got == legacy_wire_messages(item)


@pytest.mark.parametrize("item", ITEMS, ids=[i["id"] for i in ITEMS])
def test_build_messages_v2_matches_legacy_wire_format(item):
    """The two legacy prompt builders must agree — `build_messages_v2()` is the
    documented one, `generate_one_v2()` is the one that actually ran."""
    assert build_messages_v2(item) == legacy_wire_messages(item)


def test_sample_ids_are_item_ids():
    ids = [inspect_task.record_to_sample(i).id for i in ITEMS]
    assert ids == [i["id"] for i in ITEMS]
    assert len(set(ids)) == len(ids)


def test_subset_filters_partition_the_set():
    structured = inspect_task.load_items(DATA, "structured")
    implicit = inspect_task.load_items(DATA, "implicit")
    assert len(structured) + len(implicit) == len(ITEMS)
    assert not {i["id"] for i in structured} & {i["id"] for i in implicit}


def test_score_value_always_covers_ten_dimensions():
    """Ragged score keys would make the per-dimension metrics incomparable
    across samples."""
    for profile in ({}, {"universalism": 1.0}, {"bogus_value": 3.0}):
        value = inspect_task._as_score_value(profile)
        assert set(value) == set(SCHWARTZ_VALUES)
        assert all(isinstance(v, float) for v in value.values())


def test_item_metadata_round_trips():
    item = ITEMS[0]
    sample = inspect_task.record_to_sample(item)
    assert sample.metadata["item"] == item
    # metadata must be JSON-serializable — Inspect writes it to the eval log
    json.dumps(sample.metadata)


# --------------------------------------------------------------------------- #
# Azure content filtering
# --------------------------------------------------------------------------- #
#
# Regression for a bug found 2026-08-25: Azure sometimes returns HTTP 200 whose
# completion body IS the content-filter notice. Detecting only the 400 path let
# 14 such rows enter the dataset as if the model had answered (all
# revelation_064; gpt-4o-mini 10/10 replicates, gpt-4o 3/10 — the filter is not
# deterministic, so it skews replicate distributions as well as dropping items).


def test_filter_notice_returned_as_content_is_detected():
    from src.providers import looks_like_filter_response

    notice = (
        "The response was filtered due to the prompt triggering Azure OpenAI's "
        "content management policy. Please modify your prompt and retry. To learn "
        "more about our content filtering policies please read our documentation: "
        "https://go.microsoft.com/fwlink/?linkid=2198766"
    )
    assert looks_like_filter_response(notice)
    assert looks_like_filter_response("  " + notice + "\n")


def test_real_answers_are_not_flagged_as_filtered():
    from src.providers import looks_like_filter_response

    assert not looks_like_filter_response("")
    assert not looks_like_filter_response("I would intervene to stop the killing.")
    # A long answer that merely discusses content policy is not a filter notice.
    long_answer = (
        "Content moderation policy is one of the competing considerations here. "
        * 40
    )
    assert not looks_like_filter_response(long_answer)


def test_provider_filtered_scores_as_empty_profile():
    from src.providers import PROVIDER_FILTERED_PREFIX

    assert inspect_task._as_score_value({}) == {v: 0.0 for v in SCHWARTZ_VALUES}
    assert PROVIDER_FILTERED_PREFIX.startswith("[PROVIDER_FILTERED")
