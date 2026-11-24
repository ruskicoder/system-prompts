"""Run with: python3 -B -m unittest discover -s install -p 'test_*.py' -v

The installers copy the package; tests/installers/ covers that part. These tests cover
validate_package(), which skills/validate_skills.py runs in CI.
"""

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import antigravity_plugin as plugin


class PluginPackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="antigravity test ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "source repo"
        for relative in (plugin.PACKAGE_PATH, Path(".agents/skills"), Path("tools"), Path("install")):
            shutil.copytree(plugin.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))
        self.package = self.root / plugin.PACKAGE_PATH
        self.count = len(json.loads((self.root / "tools/registry.json").read_text()))

    def validate(self):
        return plugin.validate_package(self.package, self.root)

    def test_generated_package_is_valid(self):
        self.assertEqual(self.count, self.validate())

    def test_invalid_manifest_is_rejected(self):
        manifest = self.package / "plugin.json"
        for bad in ('{', '{}', '[]', '{"name":"wrong"}'):
            with self.subTest(manifest=bad):
                manifest.write_text(bad)
                with self.assertRaises((ValueError, TypeError)):
                    self.validate()

    def test_missing_skill_is_rejected(self):
        next((self.package / "skills").glob("*/SKILL.md")).unlink()
        with self.assertRaises(ValueError):
            self.validate()

    def test_changed_skill_is_rejected(self):
        next((self.package / "skills").glob("*/SKILL.md")).write_text("corrupted")
        with self.assertRaises(ValueError):
            self.validate()

    def test_changed_companion_file_is_rejected(self):
        companion = next(p for p in (self.package / "skills").rglob("*") if p.is_file() and p.name != "SKILL.md")
        companion.write_text("corrupted")
        with self.assertRaises(ValueError):
            self.validate()

    def test_extra_skill_is_rejected(self):
        (self.package / "skills/stale").mkdir()
        with self.assertRaises(ValueError):
            self.validate()

    def test_generator_reproduces_package(self):
        spec = importlib.util.spec_from_file_location("generator", self.root / "tools/generate_integrations.py")
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        # Canonical files remain in the real repository; rendering goes into this fixture.
        generator.SKILLS_DIR = plugin.ROOT / "skills"
        generator.WORKFLOWS_DIR = plugin.ROOT / "workflows"
        generator.ROOT = plugin.ROOT
        output = self.base / "rendered"
        entries = generator.load_registry()
        for entry in entries:
            generator.write_skill_md(entry, output)
            self.assertEqual((output / entry["id"] / "SKILL.md").read_bytes(),
                             (self.package / "skills" / entry["id"] / "SKILL.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
