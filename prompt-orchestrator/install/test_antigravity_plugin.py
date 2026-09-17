"""Run with: python3 -B -m unittest discover -s install -p 'test_*.py' -v"""

import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import antigravity_plugin as plugin


class PluginInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="antigravity test ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "source repo"
        for relative in (plugin.PACKAGE_PATH, Path(".agents/skills"), Path("tools"), Path("install")):
            shutil.copytree(plugin.ROOT / relative, self.root / relative,
                            ignore=shutil.ignore_patterns("__pycache__"))
        self.config = self.base / "user config"
        self.package = self.root / plugin.PACKAGE_PATH
        self.target = self.config / "plugins" / plugin.PLUGIN_NAME
        self.count = len(json.loads((self.root / "tools/registry.json").read_text()))

    def install(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return plugin.install(self.root, self.config)

    def test_fresh_install_and_exact_content(self):
        target, backup = self.install()
        self.assertIsNone(backup)
        self.assertEqual(self.count, plugin.validate_package(target, self.root))
        self.assertEqual({"plugins"}, {p.name for p in self.config.iterdir()})

    def test_update_preserves_backup_neighbors_and_supports_rollback(self):
        self.install()
        marker = self.target / "local-customization.txt"
        marker.write_text("preserve me")
        sibling = self.config / "plugins/another-plugin"
        sibling.mkdir()
        (sibling / "plugin.json").write_text('{"name":"another-plugin"}')
        shared = self.config.parent / ".agents/skills/existing/SKILL.md"
        shared.parent.mkdir(parents=True)
        shared.write_text("unchanged")
        target, backup = self.install()
        self.assertEqual("preserve me", (backup / marker.name).read_text())
        self.assertFalse((target / marker.name).exists())
        self.assertEqual({plugin.PLUGIN_NAME, "another-plugin"},
                         {p.name for p in (self.config / "plugins").iterdir()})
        self.assertEqual("unchanged", shared.read_text())
        target.rename(self.config / "retired-install")
        backup.rename(target)
        self.assertEqual("preserve me", marker.read_text())

    def test_invalid_payloads_fail_before_destination_writes(self):
        manifest = self.package / "plugin.json"
        original = manifest.read_bytes()
        for bad in ('{', '{}', '[]', '{"name":"wrong"}'):
            with self.subTest(manifest=bad):
                manifest.write_text(bad)
                with self.assertRaises((ValueError, TypeError)):
                    self.install()
                self.assertFalse(self.config.exists())
        manifest.write_bytes(original)
        skill = next((self.package / "skills").glob("*/SKILL.md"))
        skill.unlink()
        with self.assertRaises(ValueError):
            self.install()
        self.assertFalse(self.config.exists())

    def test_changed_skill_is_rejected(self):
        skill = next((self.package / "skills").glob("*/SKILL.md"))
        skill.write_text("corrupted")
        with self.assertRaises(ValueError):
            self.install()
        self.assertFalse(self.config.exists())

    def test_extra_skill_is_rejected(self):
        (self.package / "skills/stale").mkdir()
        with self.assertRaises(ValueError):
            self.install()
        self.assertFalse(self.config.exists())

    def test_failed_staging_leaves_previous_install_untouched(self):
        self.install()
        with patch.object(plugin.shutil, "copytree", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.install()
        self.assertEqual(self.count, plugin.validate_package(self.target, self.root))
        self.assertFalse((self.config / "plugin-backups").exists())

    def test_failed_publish_restores_previous_install(self):
        self.install()
        marker = self.target / "previous.txt"
        marker.write_text("original")
        rename = Path.rename

        def fail_publish(path, destination):
            if path.parent.name.startswith(".orchestrator-stage-"):
                raise OSError("publish failed")
            return rename(path, destination)

        with patch.object(Path, "rename", fail_publish):
            with self.assertRaisesRegex(OSError, "publish failed"):
                self.install()
        self.assertEqual("original", marker.read_text())

    def test_file_target_is_rejected(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("keep")
        with self.assertRaises(ValueError):
            self.install()
        self.assertEqual("keep", self.target.read_text())

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

    @unittest.skipUnless(shutil.which("bash"), "Bash unavailable")
    def test_bash_entrypoint_and_failure_exit(self):
        command = ["bash", str(self.root / "install/install-antigravity.sh"),
                   "--config-dir", str(self.config)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(self.count, plugin.validate_package(self.target, self.root))
        (self.package / "plugin.json").unlink()
        self.assertNotEqual(0, subprocess.run(command, capture_output=True).returncode)

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell unavailable")
    def test_powershell_entrypoint_and_failure_exit(self):
        command = [shutil.which("pwsh") or shutil.which("powershell"), "-NoProfile",
                   "-File", str(self.root / "install/install-antigravity.ps1"),
                   "-ConfigDir", str(self.config)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(self.count, plugin.validate_package(self.target, self.root))
        (self.package / "plugin.json").unlink()
        self.assertNotEqual(0, subprocess.run(command, capture_output=True).returncode)


if __name__ == "__main__":
    unittest.main()
