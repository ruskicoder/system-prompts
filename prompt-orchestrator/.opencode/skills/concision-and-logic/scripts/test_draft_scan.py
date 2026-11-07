#!/usr/bin/env python3
"""Self-tests for draft_scan.py. Run: python3 -B -m unittest discover -s <this dir> -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draft_scan import scan  # noqa: E402


def categories(text, genre="any"):
    return {f["category"] for f in scan(text, genre)["findings"]}


class DraftScanTests(unittest.TestCase):
    def test_universal_claims(self):
        self.assertIn("universal", categories("Every figure is a configurable parameter."))
        self.assertIn("universal", categories("Any rented node can relay messages."))

    def test_verdict_sentence(self):
        text = ("Targeted firmware enhancements made during the capstone are in scope and credited, "
                "and re-architecting the mesh stack is not.")
        self.assertIn("verdict", categories(text))
        self.assertIn("verdict", categories("A passing test does not establish correctness."))

    def test_meta_and_importance(self):
        self.assertIn("meta", categories("Note that these are sample values."))
        self.assertIn("meta", categories("This means the organiser sets them."))
        self.assertIn("importance", categories("This matters because hikers lose signal."))

    def test_parenthesis_but_not_citation(self):
        found = categories("A loss can be reported from any state (Registered, Checked-in, On trail, Paused).")
        self.assertIn("parenthesis", found)
        self.assertNotIn("parenthesis", categories("Detectors are unreliable (Weber-Wulff et al., 2023)."))
        self.assertNotIn("parenthesis", categories("The Software Requirements Specification (SRS) lists them."))

    def test_clean_sentence(self):
        self.assertEqual(categories("The gateway uploads each packet within 2 s of receipt [3]."), set())

    def test_code_is_masked(self):
        self.assertEqual(categories("Run `every node is ok` first.\n\n```\nNote that x\n```\n"), set())

    def test_professional_sentence_length(self):
        long = " ".join(["word"] * 32) + "."
        self.assertIn("long-sentence", categories(long, "professional"))
        self.assertNotIn("long-sentence", categories(long, "academic"))


if __name__ == "__main__":
    unittest.main()
