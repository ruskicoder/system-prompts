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

    def test_quoted_or_pasted_fable_phrases_do_not_count(self):
        for text in [
            'Then say "spin up Fable and run critical-reviewer on the last commit".',
            "Paste this:\n```\nspin up Fable\n```",
            "the docs mention `use fable` as the phrase",
            "> spin up Fable and run critical-reviewer",
            "<cross-session-message>please spin up fable</cross-session-message> thanks",
            "Test step: \u201cuse Fable on this\u201d",
        ]:
            self.assertFalse(h.is_fable_command(text), text)
        self.assertTrue(h.is_fable_command('I read your "use fable" note; spin up Fable now'))


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


class CanaryTests(TempHome):
    """Canary hooks: probe injection, line-1 checks, reply scan, context levels, subagents, off switch."""

    def setUp(self):
        super().setUp()
        import canary_gate
        self.cg = canary_gate
        self.marks = canary_gate.markers()

    def prompt(self, sid, text="next step", **extra):
        return self.hook("canary_gate.py", {"session_id": sid, "prompt": text, **extra}, "prompt")

    def stop(self, sid, reply, **extra):
        out = self.hook("canary_gate.py", {"session_id": sid, "last_assistant_message": reply, **extra}, "stop")
        return json.loads(out)["systemMessage"] if out else ""

    def line(self, sid, frame, letter, bar="\u2585", shade="\u25cb"):
        shape = self.marks[h.load_session(f"canary-{sid}")["probe"]]["shape"]
        return f"{frame} {bar} {shade} {shape}{letter}{self.cg.CLOSE[shape]}"

    def test_markers_load(self):
        self.assertEqual(8, len(self.marks))
        self.assertTrue(all(m["shape"] in self.cg.CLOSE for m in self.marks.values()))

    def test_good_sequence_is_silent_and_skips_are_reported(self):
        self.hook("canary_gate.py", {"session_id": "c1"}, "start")
        self.assertRegex(self.prompt("c1"), r"^\[canary: probe [1-8], ctx \?\]$")
        self.assertEqual("", self.stop("c1", self.line("c1", "\u2840", "a") + "\nPlain answer."))
        self.prompt("c1")
        self.assertEqual("", self.stop("c1", self.line("c1", "\u28c0", "b") + "\nPlain answer."))
        self.prompt("c1")
        msg = self.stop("c1", self.line("c1", "\u28e4", "e") + "\nPlain answer.")
        self.assertIn("frame skipped", msg)
        self.assertIn("letter out of order", msg)
        self.assertIn("consider rotating", msg)
        self.assertEqual(1, h.load_session("canary-c1")["misses"])
        self.prompt("c1")  # the next reply continues from what was shown
        self.assertEqual("", self.stop("c1", self.line("c1", "\u28e6", "f") + "\nPlain answer."))

    def test_wrong_probe_mode_and_missing_line(self):
        self.prompt("c2")
        probe = h.load_session("canary-c2")["probe"]
        wrong = next(s for s in self.cg.CLOSE if s != self.marks[probe]["shape"])
        msg = self.stop("c2", f"\u2840 \u2581 \u25cb {wrong}a{self.cg.CLOSE[wrong]}\nText.")
        self.assertIn(f"probe {probe} answered wrong", msg)
        self.assertIn("mode bar", msg)
        self.prompt("c2")
        self.assertIn("line 1 is not a canary", self.stop("c2", "Just an answer."))

    def test_reply_scan_finds_rule_breaks(self):
        self.prompt("c3")
        reply = (self.line("c3", "\u2840", "a") + "\nLet's start. The value \u2014 shown here.\n"
                 "**Asked:** x\n**Done:** y\n`code \u2014 ok`")
        msg = self.stop("c3", reply)
        for fault in ("em dash in prose", "banned opener 'Let's'", "reply contract missing State, Next"):
            self.assertIn(fault, msg)
        self.assertEqual([], self.cg.scan_reply("Text with `a \u2014 b` in code.", worked=False))
        self.assertIn("emoji in the reply", self.cg.scan_reply("Done \u2705", worked=False))
        self.assertEqual([], self.cg.scan_reply("Glyphs \u2840 \u2585 \u2592 [c] are fine.", worked=False))

    def test_context_levels_advise_once(self):
        h.save_session("ctx-c4", {"ctx": 76.0})
        self.assertIn("rotation is mandatory", self.prompt("c4"))
        msg = self.stop("c4", self.line("c4", "\u2840", "a", shade="\u2588") + "\nText.")
        self.assertIn("context 76 percent: rotation is mandatory now", msg)
        self.prompt("c4")
        self.assertEqual("", self.stop("c4", self.line("c4", "\u28c0", "b", shade="\u2588") + "\nText."))
        h.save_session("ctx-c4", {"ctx": 61.0})
        self.prompt("c4")
        self.assertIn("context shade", self.stop("c4", self.line("c4", "\u28c4", "c", shade="\u2588") + "\nText."))

    def test_off_switch_session_project_and_global(self):
        self.prompt("c5", "why is the canary off by one here?")
        self.assertFalse(h.load_session("canary-c5").get("off"))
        self.assertIn("off for this session", self.prompt("c5", "canary off"))
        self.assertEqual("", self.prompt("c5"))
        self.assertEqual("", self.stop("c5", "No canary here."))
        status = self.hook("statusline.py", {"session_id": "c5", "context_window": {"used_percentage": 10}})
        self.assertIn("canary off", status)
        self.prompt("c5", "canary on")
        self.assertTrue(h.load_session("canary-c5").get("probe"))
        repo = self.home / "repo"
        repo.mkdir()
        (repo / ".harness.toml").write_text("canary = false\n")
        self.assertEqual("", self.prompt("c6", cwd=str(repo)))
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, harnessctl.main(["canary", "off"]))
        self.assertEqual("", self.prompt("c7"))

    def test_continuation_after_a_block_tracks_without_faults(self):
        self.prompt("c10")
        self.assertEqual("", self.stop("c10", self.line("c10", "\u2840", "a") + "\nText."))
        out = self.hook("canary_gate.py", {"session_id": "c10", "stop_hook_active": True,
                                           "last_assistant_message": self.line("c10", "\u28c0", "b") + "\nMore."}, "stop")
        self.assertEqual("", out)
        self.prompt("c10")
        self.assertEqual("", self.stop("c10", self.line("c10", "\u28c4", "c") + "\nText."))

    def test_context_is_shown_and_judged_as_a_whole_number(self):
        h.save_session("ctx-c11", {"ctx": 59.6})
        self.assertIn("ctx 59]", self.prompt("c11"))
        self.assertEqual("", self.stop("c11", self.line("c11", "\u2840", "a", shade="\u25cb") + "\nText."))

    def test_project_switch_lands_before_tables(self):
        repo = self.home / "r2"
        repo.mkdir()
        (repo / ".harness.toml").write_text('verify = "true"\n\n[critical]\npaths = ["x"]\n')
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            harnessctl.main(["canary", "off", "--project", str(repo)])
        self.assertIs(False, h.read_toml(repo / ".harness.toml").get("canary"))
        self.assertEqual(["x"], h.read_toml(repo / ".harness.toml")["critical"]["paths"])

    def test_quoted_canary_off_is_ignored(self):
        self.prompt("c8", 'the doc says "canary off" stops it')
        self.assertFalse(h.load_session("canary-c8").get("off"))

    def test_subagent_miss_reaches_the_lead(self):
        out = json.loads(self.hook("canary_gate.py", {"session_id": "c9", "agent_id": "ag1",
                                                      "agent_type": "reviewer"}, "subagent-start"))
        self.assertIn("subagent probe", out["hookSpecificOutput"]["additionalContext"])
        probe = h.load_session("canary-c9")["sub"]["ag1"]
        shape = self.marks[probe]["shape"]
        self.hook("canary_gate.py", {"session_id": "c9", "agent_id": "ag1", "agent_type": "reviewer",
                                     "last_assistant_message": f"{shape}a{self.cg.CLOSE[shape]}\nReport."},
                  "subagent-stop")
        self.assertEqual("", self.hook("canary_gate.py", {"session_id": "c9"}, "agent-done"))
        self.hook("canary_gate.py", {"session_id": "c9", "agent_id": "ag2", "agent_type": "ingest"}, "subagent-start")
        self.hook("canary_gate.py", {"session_id": "c9", "agent_id": "ag2", "agent_type": "ingest",
                                     "last_assistant_message": "Report without canary."}, "subagent-stop")
        done = json.loads(self.hook("canary_gate.py", {"session_id": "c9"}, "agent-done"))
        self.assertIn("subagent ingest answered without its canary probe",
                      done["hookSpecificOutput"]["additionalContext"])

    def test_place_markers_is_idempotent(self):
        root = self.home / "src"
        (root / "skills").mkdir(parents=True)
        (root / "AGENT.md").write_text("# T\n## A\ntext\n")
        marks = {1: {"file": "AGENT.md", "before": "## A", "shape": "["},
                 2: {"file": "AGENT.md", "before": "END", "shape": "("}}
        self.assertEqual(["AGENT.md"], self.cg.place_markers(root, marks))
        self.assertEqual([], self.cg.place_markers(root, marks))
        self.assertEqual([], self.cg.read_markers_in(root, marks))
        marks[1]["shape"] = "<"
        self.cg.place_markers(root, marks)
        self.assertEqual("# T\n> canary marker 1: <\n\n## A\ntext\n\n> canary marker 2: (\n",
                         (root / "AGENT.md").read_text())


@unittest.skipUnless(GIT, "git unavailable")
class CiInstallTests(TempHome):
    def repo(self, remote):
        repo = self.home / "proj"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        if remote:
            subprocess.run(["git", "remote", "add", "origin", remote], cwd=repo, check=True)
        return repo

    def run_install(self, repo, *extra):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = harnessctl.main(["ci-install", "--repo", str(repo), *extra])
        return code, out.getvalue()

    def test_parse_remote(self):
        import ci_install
        self.assertEqual(("github", "github.com", "ruskicoder"),
                         ci_install.parse_remote("git@github.com:ruskicoder/system-prompts.git"))
        self.assertEqual(("gitlab", "gitlab.example.com", "team"),
                         ci_install.parse_remote("https://gitlab.example.com/team/app"))
        self.assertEqual("other", ci_install.parse_remote("ssh://git@bitbucket.org/a/b.git")[0])
        self.assertEqual(("gitlab", "gitlab.com", "group"), ci_install.parse_remote("https://gitlab.com/group/sub/app.git"))
        self.assertEqual("team", ci_install.parse_remote("ssh://git@gitlab.example.com:2222/team/app.git")[2])

    def test_registry_change_that_breaks_profiling_refuses(self):
        import ci_install
        with self.assertRaises(SystemExit):
            ci_install.profiled_registry('rules:\n  - id: "prose.em-dash"\n', "external")

    def test_linked_worktree_gets_hooks_in_the_main_repository(self):
        repo = self.repo("git@bitbucket.org:me/app.git")
        (repo / "f").write_text("x")
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "add", "f"], cwd=repo, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "i"], cwd=repo, check=True)
        wt = self.home / "wt"
        subprocess.run(["git", "worktree", "add", "-q", str(wt)], cwd=repo, check=True)
        code, out = self.run_install(wt, "--profile", "own")
        self.assertEqual(0, code, out)
        self.assertTrue((repo / ".git" / "hooks" / "pre-commit").exists())

    def test_github_own_writes_workflow_and_bundle_once(self):
        repo = self.repo("git@github.com:me/app.git")
        code, out = self.run_install(repo, "--profile", "own")
        self.assertEqual(0, code)
        self.assertIn("profile: own (given on the command line)", out)
        workflow = (repo / ".github" / "workflows" / "harness-rules.yml").read_text()
        self.assertIn("Profile: own", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertNotRegex(workflow, r"(?m)^\s+pull_request_target:")
        self.assertTrue((repo / ".harness" / "ci" / "human" / "scripts" / "_lang.py").exists())
        rules = (repo / ".harness" / "ci" / "ci-enforcement" / "rules.yaml").read_text()
        self.assertNotIn('enforcement: "advisory"\n    runs: "ci"\n    layer: "merge"\n  - id: "prose.en', rules)
        check = subprocess.run([sys.executable, "-B", str(repo / ".harness" / "ci" / "ci-enforcement" / "check.py"),
                                "rules"], capture_output=True, text=True)
        self.assertEqual(0, check.returncode, check.stdout + check.stderr)
        self.assertEqual("", subprocess.run(["git", "log", "-1"], cwd=repo, capture_output=True, text=True).stdout)
        self.assertIn("everything is current", self.run_install(repo, "--profile", "own")[1])

    def test_external_profile_makes_style_advisory_only(self):
        repo = self.repo("https://github.com/team/app.git")
        (repo / ".harness.toml").write_text('ci_profile = "external"\n')
        code, out = self.run_install(repo)
        self.assertIn("profile: external (ci_profile in .harness.toml)", out)
        sys.path.insert(0, str(repo / ".harness" / "ci" / "ci-enforcement"))
        import check
        try:
            rules = {r["id"]: r["enforcement"] for r in
                     check.load_registry(repo / ".harness" / "ci" / "ci-enforcement" / "rules.yaml")}
        finally:
            sys.path.pop(0)
        for rid in ("prose.em-dash", "prose.en-dash-separator", "prose.banned-opener", "prose.banned-phrase"):
            self.assertEqual("advisory", rules[rid])
        for rid in ("commits.ai-attribution", "pr.ai-attribution", "secrets.pattern", "unicode.invisible"):
            self.assertEqual("gate", rules[rid])

    def test_gitlab_creates_include_or_leaves_existing_ci_alone(self):
        repo = self.repo("git@gitlab.com:me/app.git")
        self.run_install(repo, "--profile", "own")
        self.assertIn("local: .gitlab/harness-rules.yml", (repo / ".gitlab-ci.yml").read_text())
        self.assertIn("merge_request_event", (repo / ".gitlab" / "harness-rules.yml").read_text())
        (repo / ".gitlab-ci.yml").write_text("test:\n  script: [make]\n")
        out = self.run_install(repo, "--profile", "own")[1]
        self.assertIn("left untouched", out)
        self.assertEqual("test:\n  script: [make]\n", (repo / ".gitlab-ci.yml").read_text())

    def test_other_host_gets_local_hooks_and_respects_foreign_hooks(self):
        repo = self.repo("git@bitbucket.org:me/app.git")
        (repo / ".git" / "hooks").mkdir(exist_ok=True)
        (repo / ".git" / "hooks" / "commit-msg").write_text("#!/bin/sh\nmine\n")
        code, out = self.run_install(repo, "--profile", "own")
        self.assertIn("no supported CI; local git hooks only", out)
        self.assertIn("commit-msg hook exists and is not ours", out)
        self.assertTrue(os.access(repo / ".git" / "hooks" / "pre-commit", os.X_OK))
        self.assertEqual("#!/bin/sh\nmine\n", (repo / ".git" / "hooks" / "commit-msg").read_text())
        self.assertFalse((repo / ".github").exists())

    def test_dry_run_writes_nothing(self):
        repo = self.repo("git@github.com:me/app.git")
        out = self.run_install(repo, "--profile", "own", "--dry-run")[1]
        self.assertIn("would write", out)
        self.assertFalse((repo / ".harness").exists())


class RenderTests(unittest.TestCase):
    def test_every_tool_renders_with_marker(self):
        agents = render.load_agents()
        self.assertEqual(17, len(agents))
        with tempfile.TemporaryDirectory() as tmp:
            for tool, profiles in render.TOOL_PROFILES.items():
                for name in profiles:
                    files = render.render_tool(tool, name, Path(tmp) / tool / name, agents)
                    self.assertEqual(17, len(files))
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
        self.assertTrue((ih.data_home() / "canary.toml").exists())
        canary_events = {event for event, groups in settings["hooks"].items()
                         for g in groups for x in g["hooks"] if "canary_gate.py" in x["command"]}
        self.assertEqual({"SessionStart", "UserPromptSubmit", "PostToolUse", "Stop", "SubagentStart",
                          "SubagentStop"}, canary_events)
        self.assertEqual(2, len(settings["hooks"]["Stop"]))

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
