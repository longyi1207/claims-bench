"""Tests for v0.5 values lexicon."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.lexicon import load_lexicon, rollup_parent_values, score_lexicon_entries
from src.io import load_jsonl


class TestLexicon(unittest.TestCase):
    def test_lexicon_size(self):
        lex = load_lexicon()
        self.assertGreaterEqual(lex["stats"]["n_entries"], 180)
        self.assertGreaterEqual(lex["stats"]["n_mid_level"], 50)

    def test_all_entries_have_parent(self):
        lex = load_lexicon()
        parents = set(lex["layer1_values"])
        for e in lex["entries"]:
            self.assertIn(e["parent_value"], parents, e["id"])
            self.assertIn(e["mid_level"], lex["rollup"]["mid_to_entries"])

    def test_udhr_privacy_response(self):
        text = "HIPAA protects patient privacy. No arbitrary interference with correspondence without consent."
        scores = score_lexicon_entries(text)
        self.assertGreater(scores.get("udhr_art12", 0), 0)
        rollup = rollup_parent_values(scores)
        self.assertGreater(rollup.get("privacy", 0), 0)

    def test_confucian_harmony_response(self):
        text = "Preserve family harmony and filial piety toward your parents during Spring Festival."
        scores = score_lexicon_entries(text)
        active = [k for k, v in scores.items() if v > 0]
        self.assertTrue(any("confucius" in k or "ai_spring" in k for k in active))

    def test_values_items_have_lexicon_tags(self):
        rows = load_jsonl(ROOT / "data" / "v0.5_values48.jsonl")
        self.assertEqual(len(rows), 48)
        tagged = [r for r in rows if r.get("lexicon_tags")]
        self.assertEqual(len(tagged), 48)
        for r in tagged:
            self.assertGreaterEqual(len(r["lexicon_tags"]), 1)


if __name__ == "__main__":
    unittest.main()
