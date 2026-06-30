"""Validate v2 revelation items and migrated legacy items against item_v2.schema.json."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "schemas" / "item_v2.schema.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


@pytest.fixture(scope="module")
def revelation_items(tmp_path_factory: pytest.TempPathFactory) -> list[dict]:
    out_path = tmp_path_factory.mktemp("v2") / "v2_revelation.jsonl"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "yaml_to_jsonl.py"),
            "--input-dir",
            str(ROOT / "data" / "revelation"),
            "--output",
            str(out_path),
        ],
        check=True,
        cwd=ROOT,
    )
    return [json.loads(line) for line in out_path.read_text().splitlines() if line]


@pytest.fixture(scope="module")
def migrated_legacy_items(tmp_path_factory: pytest.TempPathFactory) -> list[dict]:
    out_path = tmp_path_factory.mktemp("legacy") / "v0.5_full208_v2tags.jsonl"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "migrate_legacy_tags.py"),
            "--input",
            str(ROOT / "data" / "v0.5_full208.jsonl"),
            "--output",
            str(out_path),
        ],
        check=True,
        cwd=ROOT,
    )
    return [json.loads(line) for line in out_path.read_text().splitlines() if line]


def test_yaml_to_jsonl_produces_at_least_one_item(revelation_items: list[dict]) -> None:
    assert len(revelation_items) >= 1


def test_revelation_items_validate_against_item_v2_schema(
    schema: dict, revelation_items: list[dict]
) -> None:
    for item in revelation_items:
        jsonschema.validate(item, schema)


def test_revelation_items_require_l3_fields(revelation_items: list[dict]) -> None:
    for item in revelation_items:
        assert item["layer"] == "L3_revelation"
        assert item["uncertainty"] == "radical_under_spec"
        assert "elicitation" in item
        assert item["gold"]["failure_modes"]
        assert item["gold"]["human_panel"]["required"] is True
        assert item["tags"].get("schwartz_tension")


def test_migrated_legacy_items_have_v2_fields(migrated_legacy_items: list[dict]) -> None:
    assert len(migrated_legacy_items) == 208
    valid_uncertainty = {"gold_clear", "structured_tradeoff", "ambiguous", "radical_under_spec"}
    valid_layer = {"L1_stakeholder", "L2_principle", "L3_revelation"}
    for item in migrated_legacy_items:
        assert item["domain"]
        assert item["uncertainty"] in valid_uncertainty
        assert item["layer"] in valid_layer
        assert item["tags"]["legacy_conflict_type"] == item["conflict_type"]
        # legacy fields preserved
        assert "norm_classes" in item
        assert "conflict_type" in item


def test_migrated_legacy_items_keep_free_text_tags_as_legacy_keywords(
    migrated_legacy_items: list[dict],
) -> None:
    with_keywords = [i for i in migrated_legacy_items if "legacy_keywords" in i]
    assert with_keywords, "expected at least one item with legacy free-text tags preserved"
    for item in with_keywords:
        assert isinstance(item["legacy_keywords"], list)
        assert isinstance(item["tags"], dict)
