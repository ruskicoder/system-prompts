#!/usr/bin/env python3
"""Self-test for the human skill tool: python3 -m unittest discover -s <skill-dir>/scripts"""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "human_tool.py"
# Codex truncates a skill's main prompt at 8,000 bytes; the generator adds a short header.
SKILL_MD_BUDGET = 7800


def run(*args, stdin=None):
    r = subprocess.run([sys.executable, str(TOOL), *args], input=stdin, capture_output=True, text=True)
    return r.returncode, r.stdout


class HumanToolTest(unittest.TestCase):
    def test_scan_flags_throat_clearing_and_jargon(self):
        rc, out = run("scan", stdin="Here's the thing: we must leverage synergy.")
        self.assertEqual(rc, 1)
        cats = {v["category"] for v in json.loads(out)["violations"]}
        self.assertTrue({"throat_clearing", "jargon"} <= cats)

    def test_scan_protects_literal_use(self):
        rc, out = run("scan", stdin="The loan used 3:1 leverage, secured by the building.")
        self.assertEqual((rc, json.loads(out)["total_violations"]), (0, 0))

    def test_preserve_catches_changed_number(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td, "a.txt"), Path(td, "b.txt")
            a.write_text("Revenue reached $47.3M in Q3 2024.")
            b.write_text("Revenue reached $47M in Q3 2024.")
            rc, out = run("preserve", str(a), str(b))
        self.assertNotEqual(rc, 0)
        self.assertGreaterEqual(json.loads(out)["missing_count"], 1)

    def test_structure_and_silhouette_return_json(self):
        text = "\n\n".join(["However, the plan works. It ships soon."] * 4)
        for cmd in ("structure", "silhouette"):
            rc, out = run(cmd, stdin=text)
            self.assertIn(rc, (0, 1))
            json.loads(out)

    def test_skill_md_fits_budget(self):
        skill = HERE.parent / "SKILL.md"
        if not skill.exists():
            skill = HERE.parent.parent / "human.md"
        size = len(skill.read_bytes())
        self.assertLessEqual(size, SKILL_MD_BUDGET + (300 if skill.name == "SKILL.md" else 0), size)


if __name__ == "__main__":
    unittest.main()
