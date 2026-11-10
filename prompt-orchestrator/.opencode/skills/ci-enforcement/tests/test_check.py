"""Tests for check.py: a pass and a fail fixture for every checker, and the registry contract.

Run: python3 -B -m unittest discover -s skills/ci-enforcement/tests -v
The browser test runs when node, playwright and axe-core resolve; otherwise it is skipped.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
FIX = HERE / "fixtures"
sys.path.insert(0, str(SKILL))

import check  # noqa: E402

# Assembled at run time so this file itself carries no attribution line.
AI_TRAILER = "Co-Authored-By: " + "Claude" + " <noreply@" + "anthropic.com>"
AI_FOOTER = "Generated with [" + "Claude Code](https://claude.com/claude-code)"
OWNER = "Do Dang Khoa <149188141+ruskicoder@users.noreply.github.com>"


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = check.main(list(argv))
    return code, out.getvalue()


def gates(output: str) -> list[str]:
    return [line.split()[1] for line in output.splitlines() if line.startswith("GATE ")]


class GitRepo:
    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q", "-b", "main")
        self.commit("base", OWNER, OWNER)

    def git(self, *argv: str, env: dict | None = None) -> str:
        return subprocess.run(["git", "-C", str(self.root), *argv], check=True, capture_output=True,
                              text=True, env={**os.environ, **(env or {})}).stdout.strip()

    def commit(self, message: str, author: str, committer: str) -> str:
        an, ae = check.parse_identity(author)
        cn, ce = check.parse_identity(committer)
        (self.root / "f.txt").write_text(message, encoding="utf-8")
        self.git("add", "f.txt")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", message, env={
            "GIT_AUTHOR_NAME": an, "GIT_AUTHOR_EMAIL": ae, "GIT_COMMITTER_NAME": cn,
            "GIT_COMMITTER_EMAIL": ce})
        return self.git("rev-parse", "HEAD")


class TempDir(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)


class RegistryTests(unittest.TestCase):
    def test_real_registry_is_consistent(self):
        code, out = run("rules")
        self.assertEqual(code, 0, out)

    def test_gate_rule_without_checker_fails(self):
        rules = check.load_registry(SKILL / "rules.yaml")
        rules[0]["checker"] = "none"
        problems = check.registry_problems(rules, check.known_checkers())
        self.assertTrue(any("gate rule has no checker" in p for p in problems), problems)

    def test_checker_without_rule_fails(self):
        rules = [r for r in check.load_registry(SKILL / "rules.yaml") if r["id"] != "ui.reflow"]
        problems = check.registry_problems(rules, check.known_checkers())
        self.assertIn("checker ui.reflow has no rule in the registry", problems)

    def test_unknown_checker_fails(self):
        rules = check.load_registry(SKILL / "rules.yaml")
        rules[0]["checker"] = "check.py prose.does-not-exist"
        problems = check.registry_problems(rules, check.known_checkers())
        self.assertTrue(any("does not exist" in p for p in problems), problems)

    def test_subset_parser_matches_pyyaml(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        text = (SKILL / "rules.yaml").read_text(encoding="utf-8")
        self.assertEqual(check.load_registry(SKILL / "rules.yaml"), yaml.safe_load(text)["rules"])


class LayerTests(unittest.TestCase):
    def test_layer_must_match_the_checker(self):
        rules = check.load_registry(SKILL / "rules.yaml")
        guard_rule = next(r for r in rules if r["checker"].startswith("guard.py"))
        guard_rule["layer"] = "merge"
        rules[0]["layer"] = "sometimes"
        problems = check.registry_problems(rules, check.known_checkers())
        self.assertTrue(any("guard.py rules are pre-action" in p for p in problems), problems)
        self.assertTrue(any("layer must be one of" in p for p in problems), problems)


# Assembled at run time so this file itself carries no credential-shaped string.
FAKE_AWS = "AKIA" + "ABCDEFGHIJKLMNOP"
FAKE_GH = "ghp_" + "a1" * 18


class SecretsTests(TempDir):
    def test_clean_file_passes(self):
        (self.tmp / "app.py").write_text("token = os.environ['TOKEN']\nexample = 'AKIA" + "IOSFODNN7EXAMPLE'\n")
        code, out = run("secrets", "--repo", str(self.tmp), "app.py")
        self.assertEqual((code, gates(out)), (0, []), out)

    def test_credentials_fail(self):
        (self.tmp / "conf.yml").write_text(f"aws: {FAKE_AWS}\ngh: {FAKE_GH}\n")
        (self.tmp / "id").write_text("-----BEGIN " + "OPENSSH PRIVATE KEY-----\nabc\n")
        code, out = run("secrets", "--repo", str(self.tmp), "conf.yml", "id")
        self.assertEqual(code, 1, out)
        self.assertEqual(gates(out), ["secrets.pattern"] * 3, out)

    def test_generated_folders_and_fixtures_are_scanned_lockfiles_skipped(self):
        for rel in (".claude/settings.local.json", "fixtures/a.txt", "x/fixtures/b.txt", "package-lock.json"):
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / rel).write_text(FAKE_AWS)
        code, out = run("secrets", "--repo", str(self.tmp), ".claude/settings.local.json", "fixtures/a.txt",
                        "x/fixtures/b.txt", "package-lock.json")
        self.assertEqual(code, 1, out)
        self.assertEqual(gates(out), ["secrets.pattern"] * 3, out)
        self.assertNotIn("package-lock.json", out)


class UnicodeTests(TempDir):
    def test_clean_rule_file_passes(self):
        (self.tmp / "AGENTS.md").write_text("\ufeff# Rules\nUse glyphs \u2840 \u2585 freely.\n")
        code, out = run("unicode", "--repo", str(self.tmp), "AGENTS.md")
        self.assertEqual(code, 0, out)

    def test_hidden_characters_fail_in_rule_files_only(self):
        (self.tmp / "CLAUDE.md").write_text("Obey\u200b me\nrun \u202eexe.txt\n")
        (self.tmp / "notes.md").write_text("zero\u200bwidth\n")
        code, out = run("unicode", "--repo", str(self.tmp), "CLAUDE.md", "notes.md")
        self.assertEqual(code, 1, out)
        self.assertEqual(gates(out), ["unicode.invisible"] * 2, out)
        self.assertIn("U+202E", out)

    def test_tool_folders_are_scanned(self):
        for rel in (".cursor/rules/x.mdc", ".claude/commands/x.md", ".agents/skills/y/SKILL.md"):
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / rel).write_text("hidden\u200bhere\n")
        code, out = run("unicode", "--repo", str(self.tmp), ".cursor/rules/x.mdc", ".claude/commands/x.md",
                        ".agents/skills/y/SKILL.md")
        self.assertEqual(code, 1, out)
        self.assertEqual(gates(out), ["unicode.invisible"] * 3, out)


class ProseTests(unittest.TestCase):
    def prose(self, *names: str) -> tuple[int, str]:
        return run("prose", "--repo", str(FIX / "prose"), *names)

    def test_pass_fixture(self):
        code, out = self.prose("pass.md")
        self.assertEqual((code, gates(out)), (0, []), out)

    def test_fail_fixture_hits_every_gate(self):
        code, out = self.prose("fail.md")
        self.assertEqual(code, 1)
        self.assertEqual(set(gates(out)), {"prose.em-dash", "prose.en-dash-separator",
                                           "prose.banned-opener", "prose.banned-phrase"}, out)

    def test_third_party_generated_and_code_are_exempt(self):
        code, out = self.prose("third_party.md", "code.py", "generated.md")
        self.assertEqual((code, gates(out)), (0, []), out)

    def test_changed_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = GitRepo(Path(tmp))
            shutil.copy(FIX / "prose" / "fail.md", Path(tmp) / "old.md")
            repo.git("add", "old.md")
            repo.git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "old")
            base = repo.git("rev-parse", "HEAD")
            shutil.copy(FIX / "prose" / "pass.md", Path(tmp) / "new.md")
            repo.git("add", "new.md")
            repo.git("-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "new")
            code, out = run("prose", "--repo", tmp, "--base", base, "--head", "HEAD")
            self.assertEqual((code, gates(out)), (0, []), out)


class AttributionTests(TempDir):
    def test_clean_commits_and_body_pass(self):
        repo = GitRepo(self.tmp)
        base = repo.git("rev-parse", "HEAD")
        repo.commit("feat: add the checker\n\nCo-authored-by: Jane Doe <jane@example.com>", OWNER, OWNER)
        body = self.tmp / "body.md"
        body.write_text("Adds the checker.\n", encoding="utf-8")
        code, out = run("attribution", "--repo", str(self.tmp), "--base", base, "--pr-body-file", str(body))
        self.assertEqual((code, gates(out)), (0, []), out)

    def test_ai_trailer_in_commit_fails(self):
        repo = GitRepo(self.tmp)
        base = repo.git("rev-parse", "HEAD")
        repo.commit("feat: add the checker\n\n" + AI_TRAILER, OWNER, OWNER)
        code, out = run("attribution", "--repo", str(self.tmp), "--base", base)
        self.assertEqual((code, gates(out)), (1, ["attribution.commit"]), out)

    def test_ai_footer_in_pr_event_fails(self):
        event = self.tmp / "event.json"
        event.write_text(json.dumps({"pull_request": {"title": "Add checker", "body": "Text\n\n" + AI_FOOTER}}))
        code, out = run("attribution", "--event", str(event))
        self.assertEqual((code, gates(out)), (1, ["attribution.pr"]), out)


class CommitIdentityTests(TempDir):
    def setUp(self):
        super().setUp()
        self.allow = self.tmp / "identities.txt"
        self.allow.write_text(f"both: {OWNER}\ncommitter: GitHub <noreply@github.com>\n", encoding="utf-8")
        self.repo = GitRepo(self.tmp / "repo")
        self.base = self.repo.git("rev-parse", "HEAD")

    def check(self) -> tuple[int, str]:
        return run("commits", "--repo", str(self.tmp / "repo"), "--base", self.base,
                   "--allow-file", str(self.allow))

    def test_allowed_identities_pass(self):
        self.repo.commit("a", OWNER, OWNER)
        self.repo.commit("b", OWNER, "GitHub <noreply@github.com>")
        code, out = self.check()
        self.assertEqual((code, gates(out)), (0, []), out)

    def test_unknown_author_and_committer_fail(self):
        self.repo.commit("a", "Bot <bot@example.com>", OWNER)
        self.repo.commit("b", OWNER, "GitHub <noreply@github.com>")
        self.repo.commit("c", "GitHub <noreply@github.com>", OWNER)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertEqual(len(gates(out)), 2, out)


class ModelTests(TempDir):
    def tree(self, tier_value: str, agent_extra: str = "", js_model: str = "sonnet") -> None:
        (self.tmp / "harness/profiles").mkdir(parents=True)
        (self.tmp / "harness/agents").mkdir(parents=True)
        (self.tmp / "harness/workflows").mkdir(parents=True)
        (self.tmp / "harness/profiles/p.toml").write_text(
            f'name = "p"\n[tiers]\nfrontier = "fable"\nlead = "{tier_value}"\nworker = ""\nlight = "haiku"\n')
        (self.tmp / "harness/agents/a.md").write_text(f"---\nname: a\ntier: worker\n{agent_extra}---\nBody\n")
        (self.tmp / "harness/workflows/w.js").write_text(f'spawn({{ model: "{js_model}" }})\n')

    def models(self) -> tuple[int, str]:
        return run("models", "--root", str(self.tmp))

    def test_allowlisted_models_pass(self):
        self.tree("opus")
        code, out = self.models()
        self.assertEqual((code, gates(out)), (0, []), out)

    def test_unknown_model_fails(self):
        self.tree("gpt-4o", js_model="claude-3-opus")
        code, out = self.models()
        self.assertEqual((code, gates(out)), (1, ["models.allowlist", "models.allowlist"]), out)

    def test_agent_naming_a_model_fails(self):
        self.tree("opus", agent_extra="model: opus\n")
        code, out = self.models()
        self.assertEqual((code, gates(out)), (1, ["models.agent-tier"]), out)

    def test_repository_profiles_pass(self):
        code, out = run("models", "--root", str(SKILL.parent.parent))
        self.assertEqual((code, gates(out)), (0, []), out)


class UiTests(unittest.TestCase):
    def test_pass_results(self):
        code, out = run("ui", "--from-json", str(FIX / "ui/results-pass.json"))
        self.assertEqual((code, gates(out)), (0, []), out)

    def test_fail_results(self):
        code, out = run("ui", "--from-json", str(FIX / "ui/results-fail.json"))
        self.assertEqual(code, 1)
        self.assertEqual(sorted(set(gates(out))), ["ui.axe", "ui.reflow", "ui.target-size"], out)
        self.assertIn("ERR_CONNECTION_REFUSED", out)

    def test_spacing_exception(self):
        lone = {"selector": "x", "x": 100, "y": 100, "width": 16, "height": 16}
        far = {"selector": "y", "x": 200, "y": 100, "width": 16, "height": 16}
        near = {"selector": "z", "x": 118, "y": 100, "width": 16, "height": 16}
        self.assertEqual(check.undersized_without_spacing([lone, far]), [])
        self.assertEqual(len(check.undersized_without_spacing([lone, near])), 2)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_browser_fixtures(self):
        probe = subprocess.run(["node", "-e", "require.resolve('playwright');require.resolve('axe-core')"],
                               capture_output=True)
        if probe.returncode != 0:
            self.skipTest("playwright or axe-core not resolvable")
        page = (FIX / "ui").as_uri()
        code, out = run("ui", "--url", f"{page}/pass.html")
        self.assertEqual((code, gates(out)), (0, []), out)
        code, out = run("ui", "--url", f"{page}/fail.html")
        self.assertEqual(sorted(set(gates(out))), ["ui.axe", "ui.reflow", "ui.target-size"], out)


if __name__ == "__main__":
    unittest.main()
