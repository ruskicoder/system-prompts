"""Self-tests for utils.parse_skill_md and utils.set_skill_description. Run:
    python3 -B -m unittest discover -s skills/skill-creator/scripts -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import utils  # noqa: E402


def parse(frontmatter: str):
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n# Body\n")
        return utils.parse_skill_md(Path(tmp))


class ParseDescription(unittest.TestCase):
    def test_single_line(self):
        name, desc, _ = parse("name: a\ndescription: One line.")
        self.assertEqual((name, desc), ("a", "One line."))

    def test_quoted_single_line(self):
        self.assertEqual(parse('name: a\ndescription: "Quoted: text."')[1], "Quoted: text.")

    def test_plain_multiline(self):
        fm = "name: a\ndescription: First part,\n  second part,\n  third part.\nargument-hint: x"
        self.assertEqual(parse(fm)[1], "First part, second part, third part.")

    def test_quoted_multiline(self):
        fm = 'name: a\ndescription: "First part\n  and second."\nother: y'
        self.assertEqual(parse(fm)[1], "First part and second.")

    def test_folded_and_literal_indicators(self):
        for indicator in (">", ">-", ">+", "|", "|-", "|+"):
            fm = f"name: a\ndescription: {indicator}\n  First line\n  second line\nother: y"
            self.assertEqual(parse(fm)[1], "First line second line", indicator)

    def test_next_key_not_swallowed(self):
        _, desc, _ = parse("name: a\ndescription: Short.\nargument-hint: [x]")
        self.assertEqual(desc, "Short.")

    def test_description_last_in_frontmatter(self):
        self.assertEqual(parse("name: a\ndescription: Start\n  end.")[1], "Start end.")

    def test_blank_line_inside_block(self):
        self.assertEqual(parse("name: a\ndescription: >\n  One\n\n  Two\nother: y")[1], "One Two")

    def test_missing_frontmatter(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text("no frontmatter")
            with self.assertRaises(ValueError):
                utils.parse_skill_md(Path(tmp))


class SetDescription(unittest.TestCase):
    def test_replaces_multiline_description_only(self):
        src = "---\nname: a\ndescription: Old part\n  more old.\nargument-hint: x\n---\n\n# Body\ndescription: keep\n"
        out = utils.set_skill_description(src, 'New "quoted": text')
        self.assertIn("name: a\n", out)
        self.assertIn("argument-hint: x\n", out)
        self.assertTrue(out.endswith("# Body\ndescription: keep\n"))
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "SKILL.md").write_text(out)
            self.assertEqual(utils.parse_skill_md(Path(tmp))[1], 'New "quoted": text')


if __name__ == "__main__":
    unittest.main()
