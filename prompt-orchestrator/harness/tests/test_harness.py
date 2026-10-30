"""Harness self-tests. Run: python3 -B -m unittest discover -s harness/tests -v"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
SCRIPTS = HARNESS / "scripts"
ROOT = HARNESS.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "install"))

import harness_lib as h  # noqa: E402
import harnessctl  # noqa: E402
import install  # noqa: E402
import install_harness as ih  # noqa: E402
import render  # noqa: E402

GIT = shutil.which("git")
MODES = dict(h.DEFAULT_MODES)


class TempHome(unittest.TestCase):
    """Every test gets its own HOME and harness state, so nothing touches the real machine."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="harness ")
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name) / "home"
        self.home.mkdir()
        self.env = {**os.environ, "HOME": str(self.home), "PO_HARNESS_HOME": str(Path(tmp.name) / "po"),
                    "USERPROFILE": str(self.home)}
        self.env.pop("CODEX_HOME", None)
        self.saved = {k: os.environ.get(k) for k in ("HOME", "PO_HARNESS_HOME", "USERPROFILE", "CODEX_HOME")}
        os.environ.update({k: self.env[k] for k in ("HOME", "PO_HARNESS_HOME", "USERPROFILE")})
        os.environ.pop("CODEX_HOME", None)
        self.addCleanup(self.restore_env)

    def restore_env(self):
        for key, value in self.saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def hook(self, script, payload, *args):
        proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args], input=json.dumps(payload),
                              capture_output=True, text=True, env=self.env, timeout=60)
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc.stdout.strip()

    def set_profile(self, provider, name):
        h.write_user_config({"profiles": {provider: name}, "plan_source": "user",
                             "plan_set_at": time.strftime("%Y-%m-%d")})


class ModeTests(unittest.TestCase):
    def quota(self, five, week, week_elapsed, now=1_000_000.0):
        return {"ts": now, "five_hour": {"used": five, "resets_at": now + 3600},
                "seven_day": {"used": week, "resets_at": now + (1 - week_elapsed) * h.WINDOWS["seven_day"]}}

    def mode(self, *args):
        return h.compute_mode(self.quota(*args), MODES, now=1_000_000.0)["mode"]

    def test_bands(self):
        self.assertEqual("Surplus", self.mode(10, 20, 0.5))      # pace -30
        self.assertEqual("Normal", self.mode(10, 50, 0.5))       # pace 0
        self.assertEqual("Conserve", self.mode(10, 65, 0.5))     # pace +15
        self.assertEqual("Conserve", self.mode(80, 50, 0.5))     # 5-hour at 75%+
        self.assertEqual("Critical", self.mode(90, 50, 0.5))
        self.assertEqual("Critical", self.mode(10, 95, 0.99))

    def test_boundaries(self):
        self.assertEqual("Surplus", self.mode(0, 35, 0.5))       # pace exactly -15
        self.assertEqual("Normal", self.mode(0, 60, 0.5))        # pace exactly +10
        self.assertEqual("Conserve", self.mode(75, 0, 0.5))

    def test_stale_or_missing_is_normal(self):
        old = self.quota(95, 95, 0.5, now=1_000_000.0 - 3600)
        result = h.compute_mode(old, MODES, now=1_000_000.0)
        self.assertEqual(("Normal", True), (result["mode"], result["stale"]))
        self.assertEqual("Normal", h.compute_mode({}, MODES)["mode"])

    def test_fable_command_detection(self):
        self.assertTrue(h.is_fable_command("OK, spin up Fable for the migration plan"))
        self.assertTrue(h.is_fable_command("Use FABLE on this"))
        self.assertFalse(h.is_fable_command("don't use fable here"))
        self.assertFalse(h.is_fable_command("we should not spin up fable yet"))
        self.assertFalse(h.is_fable_command("review the auth module"))


class HookTests(TempHome):
    def test_statusline_caches_and_displays(self):
        now = time.time()
        out = self.hook("statusline.py", {
            "session_id": "s1", "model": {"display_name": "Opus"}, "context_window": {"used_percentage": 12},
            "rate_limits": {"five_hour": {"used_percentage": 4, "resets_at": now + 3600},
                            "seven_day": {"used_percentage": 11, "resets_at": now + 4 * 86400}}})
        self.assertIn("Opus", out)
        self.assertIn("5h 4%", out)
        self.assertEqual(11, h.read_quota("claude")["seven_day"]["used"])

    def test_mode_tag_and_change_only(self):
        self.set_profile("claude", "claude-max")
        now = time.time()
        h.write_quota("claude", {"five_hour": {"used": 4, "resets_at": now + 3600},
                                 "seven_day": {"used": 50, "resets_at": now + 3.5 * 86400}}, "statusline")
        start = self.hook("mode_hook.py", {"session_id": "s2"}, "start")
        self.assertIn("harness: claude-max", start)
        self.assertIn("Normal", start)
        self.assertEqual("", self.hook("mode_hook.py", {"session_id": "s2", "prompt": "fix the bug"}, "prompt"))
        h.write_quota("claude", {"five_hour": {"used": 95, "resets_at": now + 3600}}, "statusline")
        self.assertIn("Critical", self.hook("mode_hook.py", {"session_id": "s2", "prompt": "next"}, "prompt"))

    def test_fallback_profile_asks_for_autosetup(self):
        out = self.hook("mode_hook.py", {"session_id": "s3"}, "start")
        self.assertIn("claude-pro (fallback)", out)
        self.assertIn("/autosetup", out)

    def test_session_profile_override(self):
        self.set_profile("claude", "claude-max")
        out = self.hook("mode_hook.py", {"session_id": "s4", "prompt": "harness profile: claude-pro"}, "prompt")
        self.assertIn("claude-pro (session)", out)
        self.assertEqual("claude-max", h.user_config()["profiles"]["claude"])

    def test_fable_gate(self):
        self.set_profile("claude", "claude-max")
        spawn = {"session_id": "s5", "tool_name": "Agent",
                 "tool_input": {"subagent_type": "critical-architect", "prompt": "design"}}
        denied = json.loads(self.hook("fable_gate.py", spawn))
        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        normal = {"session_id": "s5", "tool_name": "Agent", "tool_input": {"subagent_type": "reviewer"}}
        self.assertEqual("", self.hook("fable_gate.py", normal))
        line = self.hook("mode_hook.py", {"session_id": "s5", "prompt": "spin up Fable for this"}, "prompt")
        self.assertIn("authorized by user command", line)
        self.assertEqual("", self.hook("fable_gate.py", spawn))
        self.assertEqual(1, h.fable_runs_since(0))

    def test_fable_needs_credits_on_pro(self):
        self.set_profile("claude", "claude-pro")
        self.hook("mode_hook.py", {"session_id": "s6", "prompt": "use fable please"}, "prompt")
        spawn = {"session_id": "s6", "tool_name": "Agent", "tool_input": {"subagent_type": "x", "model": "fable"}}
        self.assertIn("no included Fable", self.hook("fable_gate.py", spawn))
        self.hook("mode_hook.py", {"session_id": "s6", "prompt": "ok, Fable with credits"}, "prompt")
        self.assertEqual("", self.hook("fable_gate.py", spawn))

    @unittest.skipUnless(GIT, "git unavailable")
    def test_verify_gate_blocks_then_caps(self):
        repo = self.home / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        flag = repo / "ok.flag"
        check = f'{sys.executable} -c "import sys, pathlib; sys.exit(0 if pathlib.Path(\'ok.flag\').exists() else 1)"'
        (repo / ".harness.toml").write_text(f"verify = {json.dumps(check)}\n")
        (repo / "a.txt").write_text("x\n")
        payload = {"session_id": "s7", "cwd": str(repo), "hook_event_name": "Stop"}
        for attempt in (1, 2, 3):
            out = json.loads(self.hook("verify_gate.py", payload))
            self.assertEqual("block", out["decision"])
            self.assertIn(f"({attempt}/3)", out["reason"])
        capped = json.loads(self.hook("verify_gate.py", payload))
        self.assertIn("stop allowed", capped["systemMessage"])
        flag.write_text("")
        self.assertEqual("", self.hook("verify_gate.py", payload))
        self.assertEqual("", self.hook("verify_gate.py", payload))  # unchanged tree: skipped

    def test_verify_gate_without_config(self):
        self.assertEqual("", self.hook("verify_gate.py", {"session_id": "s8", "cwd": str(self.home)}))


class RenderTests(unittest.TestCase):
    def test_every_tool_renders_with_marker(self):
        agents = render.load_agents()
        self.assertEqual(16, len(agents))
        with tempfile.TemporaryDirectory() as tmp:
            for tool, profiles in render.TOOL_PROFILES.items():
                for name in profiles:
                    files = render.render_tool(tool, name, Path(tmp) / tool / name, agents)
                    self.assertEqual(16, len(files))
                    for path in files:
                        self.assertIn(h.MARKER, path.read_text())

    def test_claude_fields(self):
        agent = next(a for a in render.load_agents() if a["name"] == "ingest")
        _, text = render.render_claude(agent, h.load_profile("claude-max"))
        self.assertIn('model: "sonnet"', text)
        self.assertIn('disallowedTools: "Write, Edit, NotebookEdit"', text)
        self.assertIn("omitClaudeMd: true", text)
        crit = next(a for a in render.load_agents() if a["name"] == "critical-architect")
        self.assertIn('model: "fable"', render.render_claude(crit, h.load_profile("claude-max"))[1])
        self.assertIn('model: "opus"', render.render_claude(crit, h.load_profile("claude-pro"))[1])
        refactor = next(a for a in render.load_agents() if a["name"] == "refactor")
        self.assertIn('isolation: "worktree"', render.render_claude(refactor, h.load_profile("claude-max"))[1])

    def test_codex_effort_clamp_and_toml(self):
        import tomllib
        agent = next(a for a in render.load_agents() if a["name"] == "reviewer")
        profile = {"tiers": {"worker": "m1"}, "efforts": {"m1": ["low", "medium", "xhigh"]}}
        _, text = render.render_codex(agent, profile)
        data = tomllib.loads(text)
        self.assertEqual("xhigh", data["model_reasoning_effort"])  # high unsupported, next one up
        self.assertEqual("m1", data["model"])
        self.assertIn("read-only", data["developer_instructions"])

    def test_no_low_effort_and_no_overlap(self):
        agents = render.load_agents()
        self.assertFalse(any(a["effort"] == "low" for a in agents))
        self.assertEqual([], render.description_overlap(agents))


class InstallerTests(TempHome):
    def test_claude_install_and_uninstall_round_trip(self):
        claude = self.home / ".claude"
        (claude / "rules").mkdir(parents=True)
        legacy = claude / "rules" / "instructions.instructions.md"
        legacy.write_text("legacy rules\n")
        original = {"env": {"KEEP": "1"}, "statusLine": {"type": "command", "command": "my-status.sh"},
                    "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "mine"}]}]}}
        (claude / "settings.json").write_text(json.dumps(original))
        (claude / "CLAUDE.md").write_text("<!-- prompt-orchestrator:start -->\n@AGENTS.md\n<!-- prompt-orchestrator:end -->\n")
        (claude / "agents").mkdir()
        (claude / "agents" / "reviewer.md").write_text("my own reviewer\n")
        ih.LEGACY_KIRO = legacy
        notes = ih.install_tool("claude", ih.main.__globals__["argparse"].Namespace(
            profile="claude-max", no_subagent_model=False, no_statusline=False, no_hooks=False,
            no_legacy_move=False, discover=False, force_cursor_agents=False))
        settings = json.loads((claude / "settings.json").read_text())
        self.assertEqual("sonnet", settings["env"]["CLAUDE_CODE_SUBAGENT_MODEL"])
        self.assertIn("statusline.py", settings["statusLine"]["command"])
        self.assertEqual("my-status.sh", h.user_config()["statusline_wrap"])
        self.assertIn("SessionStart", settings["hooks"])
        self.assertEqual(2, len(settings["hooks"]["PreToolUse"]))
        self.assertIn("@HARNESS.md", (claude / "CLAUDE.md").read_text())
        self.assertEqual("my own reviewer\n", (claude / "agents" / "reviewer.md").read_text())
        self.assertTrue(any("skipped" in n and "reviewer.md" in n for n in notes))
        self.assertTrue((claude / "agents" / "ingest.md").exists())
        self.assertTrue((claude / "workflows" / "pr-sweep.js").exists())
        self.assertFalse(legacy.exists())
        self.assertEqual("claude-max", h.user_config()["profiles"]["claude"])
        self.assertTrue((ih.data_home() / "scripts" / "mode_hook.py").exists())

        ih.uninstall_tool("claude")
        self.assertEqual(original, json.loads((claude / "settings.json").read_text()))
        self.assertNotIn("HARNESS", (claude / "CLAUDE.md").read_text())
        self.assertFalse((claude / "agents" / "ingest.md").exists())
        self.assertTrue((claude / "agents" / "reviewer.md").exists())
        self.assertEqual("legacy rules\n", legacy.read_text())
        self.assertFalse(ih.data_home().exists())

    def test_codex_install(self):
        codex = self.home / ".codex"
        codex.mkdir()
        (codex / "AGENTS.md").write_text("# core\n")
        ih.install_tool("codex", ih.main.__globals__["argparse"].Namespace(
            profile=None, no_subagent_model=False, no_statusline=False, no_hooks=False,
            no_legacy_move=True, discover=False, force_cursor_agents=False))
        self.assertTrue((codex / "agents" / "reviewer.toml").exists())
        self.assertIn("Harness Overlay", (codex / "AGENTS.md").read_text())
        self.assertIn("Stop", json.loads((codex / "hooks.json").read_text())["hooks"])
        ih.uninstall_tool("codex")
        self.assertEqual("# core\n", (codex / "AGENTS.md").read_text())
        self.assertFalse((codex / "agents" / "reviewer.toml").exists())

    def test_ctl_usage_parse(self):
        usage = {"plan": {"plan": "Max", "windows": [
            {"label": "5-hour limit", "percentUsed": 4, "resetsAt": "2026-10-30T04:00:00.088Z"},
            {"label": "Weekly · all models", "percentUsed": 11, "resetsAt": "2026-11-02T13:00:00.088Z"},
            {"label": "Weekly · Fable", "percentUsed": 0, "resetsAt": "2026-11-02T13:00:00.000Z"}]}}
        plan, windows, fable = harnessctl.parse_usage(usage)
        self.assertEqual("Max", plan)
        self.assertEqual(4, windows["five_hour"]["used"])
        self.assertEqual(11, windows["seven_day"]["used"])
        self.assertEqual(0, fable["used"])

    def test_installer_flags(self):
        plan = install.initial_plan(install.parse_args(["--core", "--yes"]))
        self.assertFalse(plan["harness"])
        self.assertTrue(plan["core"])
        plan = install.initial_plan(install.parse_args(["--harness-only", "--tools", "claude,codex", "--no-hooks"]))
        self.assertEqual((["claude", "codex"], False, True, False),
                         (plan["tools"], plan["core"], plan["harness"], plan["globals"]["hooks"]))
        plan = install.initial_plan(install.parse_args([]))
        self.assertTrue(plan["core"] and plan["harness"])
        args = install.harness_args({**plan, "profile_claude": "claude-max"}, "claude")
        self.assertIn("claude-max", args)
        with self.assertRaises(SystemExit):
            install.parse_args(["--tools", "nope"])


if __name__ == "__main__":
    unittest.main()
