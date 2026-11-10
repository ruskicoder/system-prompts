#!/usr/bin/env python3
"""Claude Code PreToolUse guard for the gates an admin identity could otherwise skip.

Reads the hook JSON on stdin and checks Bash commands. Exit 2 blocks the call and tells the agent
why; exit 0 lets it run. Refuses:

    guard.admin-merge           gh pr merge --admin
    guard.no-verify             git ... --no-verify, git commit -n, git -c core.hooksPath=...
    guard.force-push-protected  a force push to, or deletion of, a protected branch
    guard.protection-change     gh api (or curl to api.github.com) writing branch protection or rulesets

Protected branches: main, master, release/* and any glob in CI_GUARD_PROTECTED (comma separated).
Compound commands (&&, ||, ;, |) and `bash -c "..."` are split and each part is checked.
Standard library only. Model: skills/no-ai-trailer/scripts/guard.py.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

GUARDS = {
    "guard.admin-merge": "gh pr merge --admin bypasses branch protection",
    "guard.no-verify": "skipping git hooks bypasses the commit checks",
    "guard.force-push-protected": "force-pushing to or deleting a protected branch rewrites shared history",
    "guard.protection-change": "changing branch protection or rulesets lifts the gate",
}
OPERATORS = {"&&", "||", ";", "|", "&", "\n"}
WRAPPERS = {"sudo", "env", "command", "time", "nohup", "exec", "xargs"}
SHELLS = {"sh", "bash", "zsh", "dash"}
PROTECTION_PATH = re.compile(r"(^|/)(repos/[^/\s]+/[^/\s]+/)?(branches/[^/\s]+/protection\b|rulesets\b)|/orgs/[^/\s]+/rulesets\b")
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}


def protected(branch: str) -> bool:
    branch = branch.removeprefix("refs/heads/")
    extra = [p.strip() for p in os.environ.get("CI_GUARD_PROTECTED", "").split(",") if p.strip()]
    return any(fnmatch.fnmatch(branch, p) for p in ["main", "master", "release/*", *extra])


def segments(command: str) -> list[list[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        tokens = list(lexer)
    except ValueError:
        return [command.split()]
    out, cur = [], []
    for tok in tokens:
        if tok in OPERATORS or set(tok) <= set(";&|"):
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        out.append(cur)
    return out


def strip_prefix(words: list[str]) -> list[str]:
    i = 0
    while i < len(words) and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]) or words[i] in WRAPPERS):
        i += 1
    return words[i:]


def current_branch(cwd: str | None) -> str | None:
    try:
        out = subprocess.run(["git", "symbolic-ref", "--short", "HEAD"], cwd=cwd or None,
                             capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def check_git(words: list[str], cwd: str | None) -> list[tuple[str, str]]:
    hits = []
    i = 1
    while i < len(words) and words[i].startswith("-"):
        flag = words[i]
        value = words[i + 1] if flag in GIT_GLOBAL_WITH_VALUE and i + 1 < len(words) else ""
        if (flag == "-c" and value.lower().startswith("core.hookspath")) or flag.lower().startswith("-ccore.hookspath"):
            hits.append(("guard.no-verify", "git -c core.hooksPath override"))
        i += 2 if flag in GIT_GLOBAL_WITH_VALUE else 1
    if i >= len(words):
        return hits
    sub, rest = words[i], words[i + 1:]
    if "--no-verify" in rest:
        hits.append(("guard.no-verify", f"git {sub} --no-verify"))
    if sub == "commit" and any(re.match(r"^-[a-zA-Z]*n[a-zA-Z]*$", w) for w in rest):
        hits.append(("guard.no-verify", "git commit -n"))
    if sub == "push":
        hits += check_push(rest, cwd)
    return hits


PUSH_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}


def check_push(rest: list[str], cwd: str | None) -> list[tuple[str, str]]:
    force = deleting = every_branch = False
    positional: list[str] = []
    skip = False
    for w in rest:
        if skip:
            skip = False
        elif w in PUSH_WITH_VALUE:
            skip = True
        elif w in {"-f", "--force"} or w.startswith(("--force-with-lease", "--force-if-includes")):
            force = True
        elif re.match(r"^-[a-zA-Z]*f[a-zA-Z]*$", w):
            force = True
        elif w in {"-d", "--delete"}:
            deleting = True
        elif w in {"--all", "--branches", "--mirror"}:
            every_branch = True
            force = force or w == "--mirror"
        elif not w.startswith("-"):
            positional.append(w)
    targets: list[tuple[str, bool]] = []  # (branch, this refspec rewrites or deletes it)
    for spec in positional[1:]:
        plus = spec.startswith("+")
        spec = spec[1:] if plus else spec
        if spec.startswith(":"):
            targets.append((spec[1:], True))
            continue
        dst = spec.split(":", 1)[-1]
        if dst in {"HEAD", "@", ""}:
            dst = current_branch(cwd) or ""
        targets.append((dst, plus))
    if every_branch:
        targets += [("main", False), ("master", False)]
    if not positional[1:] and not every_branch:
        branch = current_branch(cwd)
        if branch is None:
            if force or deleting:
                return [("guard.force-push-protected",
                         "force push with no branch named and the current branch unknown; name the branch")]
            return []
        targets.append((branch, False))
    return [("guard.force-push-protected", f"force push or delete of protected branch {dst!r}")
            for dst, special in targets if dst and protected(dst) and (force or deleting or special)]


def check_gh(words: list[str]) -> list[tuple[str, str]]:
    if len(words) >= 3 and words[1] == "pr" and words[2] == "merge" and "--admin" in words[3:]:
        return [("guard.admin-merge", "gh pr merge --admin")]
    if len(words) >= 2 and words[1] == "api":
        method, path, has_fields = "GET", "", False
        rest = words[2:]
        for j, w in enumerate(rest):
            if w in {"-X", "--method"} and j + 1 < len(rest):
                method = rest[j + 1].upper()
            elif w.startswith("--method="):
                method = w.split("=", 1)[1].upper()
            elif re.match(r"^-X[A-Za-z]+$", w):
                method = w[2:].upper()
            elif w in {"-f", "-F", "--field", "--raw-field", "--input"} or w.startswith(("--field=", "--raw-field=", "--input=")):
                has_fields = True
            elif not w.startswith("-") and not path and (j == 0 or rest[j - 1] not in {"-X", "--method", "-H", "--header", "-f", "-F", "--field", "--raw-field", "--input", "-q", "--jq", "-t", "--template", "--hostname", "-p", "--preview", "--cache"}):
                path = w
        if method == "GET" and has_fields:
            method = "POST"
        if method in WRITE_METHODS and PROTECTION_PATH.search(path.split("?")[0]):
            return [("guard.protection-change", f"gh api {method} {path}")]
    return []


def check_curl(words: list[str]) -> list[tuple[str, str]]:
    text = " ".join(words)
    if "api.github.com" not in text:
        return []
    method = "GET"
    for j, w in enumerate(words):
        if w in {"-X", "--request"} and j + 1 < len(words):
            method = words[j + 1].upper()
        elif re.match(r"^-X[A-Za-z]+$", w):
            method = w[2:].upper()
        elif w in {"-d", "--data", "--data-raw", "--json"} and method == "GET":
            method = "POST"
    urls = [w for w in words if "api.github.com" in w]
    if method in WRITE_METHODS and any(PROTECTION_PATH.search(u.split("api.github.com", 1)[1].split("?")[0]) for u in urls):
        return [("guard.protection-change", f"curl {method} to branch protection or rulesets")]
    return []


def check_command(command: str, cwd: str | None = None, depth: int = 0) -> list[tuple[str, str]]:
    hits = []
    for seg in segments(command):
        words = strip_prefix(seg)
        if not words:
            continue
        exe = os.path.basename(words[0])
        if exe in SHELLS and depth < 3:
            for j, w in enumerate(words[1:], start=1):
                if re.match(r"^-[a-zA-Z]*c$", w) and j + 1 < len(words):
                    hits += check_command(words[j + 1], cwd, depth + 1)
                    break
        elif exe == "git":
            hits += check_git(words, cwd)
        elif exe == "gh":
            hits += check_gh(words)
        elif exe == "curl":
            hits += check_curl(words)
    return hits


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = str((payload.get("tool_input") or {}).get("command", ""))
    hits = check_command(command, payload.get("cwd"))
    if not hits:
        return 0
    lines = [f"{gid}: {what} ({GUARDS[gid]})" for gid, what in dict.fromkeys(hits)]
    print("ci-enforcement guard: blocked. " + "; ".join(lines)
          + ". Ask the user; do not work around the gate.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
