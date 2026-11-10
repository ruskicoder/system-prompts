"""Tests for guard.py: each refused command and the commands it must let through.

Run: python3 -B -m unittest discover -s skills/ci-enforcement/tests -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL))

import guard  # noqa: E402

REFUSED = {
    "guard.admin-merge": [
        "gh pr merge 12 --admin --squash",
        "cd repo && gh pr merge --admin",
    ],
    "guard.no-verify": [
        "git commit --no-verify -m 'fix'",
        "git commit -nm 'fix'",
        "git push --no-verify origin feature",
        "git -c core.hooksPath=/dev/null commit -m fix",
    ],
    "guard.force-push-protected": [
        "git push -f origin main",
        "git push --force-with-lease origin master",
        "git push origin +main",
        "git push origin HEAD:main --force",
        "git push origin :release/2.0",
        "git push --delete origin master",
        "git push --mirror origin",
        "bash -c 'git push -f origin main'",
        "FOO=1 git push -fu origin main",
    ],
    "guard.protection-change": [
        "gh api -X PUT repos/o/r/branches/main/protection --input body.json",
        "gh api --method DELETE repos/o/r/branches/main/protection/enforce_admins",
        "gh api repos/o/r/rulesets -f name=loose",
        "gh api -XPATCH /orgs/o/rulesets/7 --input r.json",
        "curl -X PUT -H 'Authorization: token x' https://api.github.com/repos/o/r/branches/main/protection -d @b.json",
    ],
}
ALLOWED = [
    "git push -u origin claude/feature",
    "git push --force-with-lease origin claude/feature",
    "git push origin main",
    "git commit -m 'mention --no-verify in prose'",
    "gh pr merge 12 --squash",
    "gh pr view 12 --json body",
    "gh api repos/o/r/branches/main/protection",
    "gh api repos/o/r/rulesets",
    "gh api repos/o/r/pulls -f title=x",
    "curl https://api.github.com/repos/o/r/branches/main/protection",
    "echo 'git push -f origin main'",
    "python3 -m unittest",
]


class GuardTests(unittest.TestCase):
    def test_refused(self):
        for gid, commands in REFUSED.items():
            for command in commands:
                with self.subTest(command=command):
                    self.assertIn(gid, [h[0] for h in guard.check_command(command, "/nonexistent")])

    def test_allowed(self):
        for command in ALLOWED:
            with self.subTest(command=command):
                self.assertEqual(guard.check_command(command, "/nonexistent"), [])

    def test_protected_globs(self):
        self.assertTrue(guard.protected("release/1.0"))
        self.assertFalse(guard.protected("claude/x"))
        os.environ["CI_GUARD_PROTECTED"] = "prod, stable/*"
        try:
            self.assertTrue(guard.protected("stable/3"))
        finally:
            del os.environ["CI_GUARD_PROTECTED"]

    def test_force_push_without_branch_uses_current_branch(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", "-b", "main", tmp], check=True)
            self.assertTrue(guard.check_command("git push --force", tmp))
            subprocess.run(["git", "-C", tmp, "checkout", "-q", "-b", "topic"], check=True)
            self.assertEqual(guard.check_command("git push --force", tmp), [])

    def test_hook_protocol(self):
        def call(command: str) -> int:
            payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": "/"})
            return subprocess.run([sys.executable, "-B", str(SKILL / "guard.py")], input=payload,
                                  capture_output=True, text=True).returncode
        self.assertEqual(call("gh pr merge 1 --admin"), 2)
        self.assertEqual(call("gh pr merge 1"), 0)
        other = json.dumps({"tool_name": "Edit", "tool_input": {"command": "gh pr merge --admin"}})
        self.assertEqual(subprocess.run([sys.executable, "-B", str(SKILL / "guard.py")], input=other,
                                        capture_output=True, text=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()
