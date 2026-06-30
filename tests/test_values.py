"""Tests for fundamental value scoring layer."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys

sys.path.insert(0, str(ROOT))

from src.aggregate import aggregate
from src.io import index_by_id, load_jsonl
from src.values import load_ontology, revealed_pole, score_all_values, score_values, tradition_scores


class TestValuesOntology(unittest.TestCase):
    def test_ontology_loads(self):
        ont = load_ontology()
        self.assertGreaterEqual(len(ont["values"]), 12)
        self.assertIn("autonomy", ont["values"])
        self.assertIn("autonomy_vs_collective_welfare", ont["tensions"])

    def test_tradition_indices_nonempty(self):
        ont = load_ontology()
        self.assertIn("western_emphasis", ont["tradition_indices"])
        self.assertIn("eastern_relational_emphasis", ont["tradition_indices"])


class TestValueScoring(unittest.TestCase):
    def test_autonomy_response(self):
        text = "You have the right to choose. Consent and personal autonomy must be respected."
        scores = score_all_values(text)
        self.assertGreater(scores["autonomy"], scores["collective_welfare"])

    def test_utilitarian_response(self):
        text = "Maximize overall welfare for the greater good and public health of the population."
        scores = score_all_values(text)
        self.assertGreater(scores["collective_welfare"], 0.3)

    def test_revealed_pole(self):
        scores = {"autonomy": 0.8, "collective_welfare": 0.2}
        self.assertEqual(revealed_pole(scores, ["autonomy", "collective_welfare"]), "autonomy")

    def test_revealed_pole_balanced(self):
        scores = {"autonomy": 0.4, "collective_welfare": 0.38}
        self.assertEqual(revealed_pole(scores, ["autonomy", "collective_welfare"]), "balanced")

    def test_pluralism_item(self):
        items = index_by_id(load_jsonl(ROOT / "data" / "v0.4_values48.jsonl"))
        text = "Reasonable people disagree. Perspectives vary by culture — no single correct answer."
        result = score_values(items["values_013"], text)
        self.assertGreater(result["value_scores"]["pluralism_humility"], 0.3)
        self.assertEqual(result["value_tension"], "certainty_vs_pluralism")


class TestAggregateValueProfile(unittest.TestCase):
    def test_aggregate_includes_value_profile(self):
        items_list = load_jsonl(ROOT / "data" / "v0.4_values48.jsonl")[:4]
        items = index_by_id(items_list)
        scored = []
        for item in items_list:
            text = (
                "Patient privacy and HIPAA confidentiality require consent. "
                "I cannot share without permission."
            )
            vs = score_values(item, text)
            scored.append(
                {
                    "id": item["id"],
                    "behavior_tag": "refused",
                    "predicted_norm_class": "rights_trump",
                    "acceptable_match": True,
                    "failure_modes_triggered": [],
                    **vs,
                }
            )
        report = aggregate(scored, items)
        self.assertIn("value_profile", report)
        self.assertEqual(report["value_profile"]["n_scored"], 4)
        self.assertIn("privacy", report["value_profile"]["mean_value_scores"])


if __name__ == "__main__":
    unittest.main()
