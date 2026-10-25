#!/usr/bin/env python3
"""Force AI attribution off in every installed tool. Safe to run any number of times.

Runs at install time and at every Claude Code session start (it registers itself as a
SessionStart hook). Each run:
  1. Claude Code  ~/.claude/settings.json: attribution {commit: "", pr: "", sessionUrl: false},
     plus the SessionStart hook (this script) and the PreToolUse guard (guard.py).
  2. VS Code      User/settings.json for Code, Insiders and VSCodium on Linux, macOS and Windows:
     git.addAICoAuthor "off".
  3. Cursor CLI   ~/.cursor/cli-config.json, when it exists: attributeCommitsToAgent and
     attributePRsToAgent false.
  4. git          a global core.hooksPath at ~/.config/git/no-ai-trailer/hooks whose commit-msg
     strips AI trailers, then every hook hands over to the repository's own .git/hooks/<name>.
     An existing core.hooksPath that is not ours is left alone and reported.

Prints one line per change. --quiet prints only changes and problems. --home DIR targets a
different home (tests). --check makes no changes and exits 1 when anything is off.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARK = "no-ai-trailer"
ATTRIBUTION = {"commit": "", "pr": "", "sessionUrl": False}

# Every client-side hook git runs from core.hooksPath. Each one hands over to the repository's
# own hook so git-lfs and other per-repository hooks keep working.
HOOK_NAMES = [
    "applypatch-msg", "pre-applypatch", "post-applypatch", "pre-commit", "pre-merge-commit",
    "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout",
    "post-merge", "pre-push", "post-rewrite", "reference-transaction", "push-to-checkout",
    "pre-auto-gc", "sendemail-validate", "post-index-change",
]
CHAIN = """\
# Hand over to the repository's own hook, if any.
hook_dir="$(git rev-parse --git-common-dir 2>/dev/null)/hooks"
if [ -x "$hook_dir/{name}" ]; then
    exec "$hook_dir/{name}" "$@"
fi
exit 0
"""
COMMIT_MSG = """\
#!/bin/sh
# no-ai-trailer: strip AI attribution from the commit message.
for py in python3 python; do
    if command -v "$py" >/dev/null 2>&1; then
        "$py" "{cleaner}" clean "$1" || exit 1
        break
    fi
done
"""


class Run:
    def __init__(self, home: Path, check: bool, quiet: bool):
        self.home, self.check, self.quiet = home, check, quiet
        self.changes: list[str] = []
        self.notes: list[str] = []

    def change(self, msg: str) -> None:
        self.changes.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def load_json(path: Path, run: Run):
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        run.note(f"{path}: not plain JSON (comments or trailing commas?), set it by hand")
        return None


def save_json(path: Path, data: dict, run: Run) -> None:
    if run.check:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def hook_entry(command: str, matcher: str | None, message: str) -> dict:
    entry = {"hooks": [{"type": "command", "command": command, "timeout": 10, "statusMessage": message}]}
    if matcher:
        entry["matcher"] = matcher
    return entry


def ensure_hook(hooks: dict, event: str, entry: dict) -> bool:
    """Add or refresh our entry for one hook event. Returns True when something changed."""
    entries = hooks.setdefault(event, [])
    ours = [e for e in entries if any(MARK in str(h.get("command", "")) for h in e.get("hooks", []))]
    if ours == [entry]:
        return False
    hooks[event] = [e for e in entries if e not in ours] + [entry]
    return True


def claude(run: Run) -> None:
    path = run.home / ".claude" / "settings.json"
    if not path.parent.exists():
        return
    data = load_json(path, run)
    if data is None:
        return
    changed = []
    if data.get("attribution") != ATTRIBUTION:
        data["attribution"] = dict(ATTRIBUTION)
        changed.append("attribution off")
    if data.get("includeCoAuthoredBy") is not None and data["includeCoAuthoredBy"] is not False:
        data["includeCoAuthoredBy"] = False
        changed.append("includeCoAuthoredBy false")
    hooks = data.setdefault("hooks", {})
    py = shlex.quote(sys.executable or "python3")
    start = hook_entry(f"{py} {shlex.quote(str(HERE / 'ensure_attribution_off.py'))} --quiet",
                       None, "no-ai-trailer: forcing AI attribution off...")
    guard = hook_entry(f"{py} {shlex.quote(str(HERE / 'guard.py'))}",
                       "Bash|mcp__.*", "no-ai-trailer: checking for AI attribution...")
    if ensure_hook(hooks, "SessionStart", start):
        changed.append("SessionStart hook")
    if ensure_hook(hooks, "PreToolUse", guard):
        changed.append("PreToolUse guard")
    if changed:
        save_json(path, data, run)
        run.change(f"{path}: " + ", ".join(changed))


def vscode(run: Run) -> None:
    roots = [run.home / ".config", run.home / "Library" / "Application Support",
             run.home / "AppData" / "Roaming"]
    for path in (root / app / "User" / "settings.json" for root in roots
                 for app in ("Code", "Code - Insiders", "VSCodium")):
        if not path.exists():
            continue
        data = load_json(path, run)
        if data is None or data.get("git.addAICoAuthor") == "off":
            continue
        data["git.addAICoAuthor"] = "off"
        save_json(path, data, run)
        run.change(f"{path}: git.addAICoAuthor off")


def cursor(run: Run) -> None:
    path = run.home / ".cursor" / "cli-config.json"
    if not path.exists():
        return
    data = load_json(path, run)
    if data is None:
        return
    attr = data.setdefault("attribution", {})
    if attr.get("attributeCommitsToAgent") is False and attr.get("attributePRsToAgent") is False:
        return
    attr["attributeCommitsToAgent"] = False
    attr["attributePRsToAgent"] = False
    save_json(path, data, run)
    run.change(f"{path}: commit and PR attribution off")


def git(run: Run, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, HOME=str(run.home))
    env.pop("GIT_CONFIG_GLOBAL", None)
    if run.home != Path.home():
        env["XDG_CONFIG_HOME"] = str(run.home / ".config")
    return subprocess.run(["git", *args], capture_output=True, text=True, env=env)


def git_hooks(run: Run) -> None:
    if shutil.which("git") is None:
        run.note("git not found, commit-msg hook not installed")
        return
    target = run.home / ".config" / "git" / MARK
    hooks_dir = target / "hooks"
    current = git(run, "config", "--global", "--get", "core.hooksPath").stdout.strip()
    if current and Path(os.path.expanduser(current)) != hooks_dir:
        run.note(f"global core.hooksPath is {current}; add {target / 'ai_trailer.py'} clean \"$1\" to its commit-msg by hand")
        return
    wanted = {"ai_trailer.py": (HERE / "ai_trailer.py").read_text(encoding="utf-8")}
    for name in HOOK_NAMES:
        body = COMMIT_MSG.format(cleaner=target / "ai_trailer.py") if name == "commit-msg" else "#!/bin/sh\n"
        wanted[f"hooks/{name}"] = body + CHAIN.format(name=name)
    stale = [rel for rel, text in wanted.items()
             if not (target / rel).exists() or (target / rel).read_text(encoding="utf-8") != text
             or (rel.startswith("hooks/") and not os.access(target / rel, os.X_OK))]
    if stale and not run.check:
        for rel in stale:
            path = target / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(wanted[rel], encoding="utf-8")
            if rel.startswith("hooks/"):
                path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if stale:
        run.change(f"{target}: {len(stale)} file(s) refreshed")
    if not current:
        if not run.check:
            git(run, "config", "--global", "core.hooksPath", str(hooks_dir))
        run.change(f"git global core.hooksPath set to {hooks_dir}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    run = Run(args.home, args.check, args.quiet)
    for step in (claude, vscode, cursor, git_hooks):
        step(run)
    verb = "would change" if run.check else "changed"
    for msg in run.changes:
        print(f"no-ai-trailer {verb}: {msg}")
    for msg in run.notes:
        print(f"no-ai-trailer note: {msg}")
    if not run.changes and not run.quiet:
        print("no-ai-trailer: AI attribution already off everywhere")
    return 1 if run.check and run.changes else 0


if __name__ == "__main__":
    sys.exit(main())
