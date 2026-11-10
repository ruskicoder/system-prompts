#!/usr/bin/env python3
"""`harnessctl.py ci-install`: put the core rules into a repository's CI, on the user's command only.

GitHub remote: `.github/workflows/harness-rules.yml`. GitLab remote: `.gitlab/harness-rules.yml` (and a
`.gitlab-ci.yml` that includes it, when none exists). Any other host: local `pre-commit` and
`commit-msg` hooks in `.git/hooks`. Every case vendors the checker into `.harness/ci/` with a rule
registry for the repository's profile:

- own (the remote owner is the account the agent signs in as): every gate rule gates.
- external: prose style rules become advisory; attribution, secrets and invisible characters still gate.

Files are written and left uncommitted; committing and pushing stay the user's call.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import harness_lib as h

HOOK_MARK = "# prompt-orchestrator-harness ci-install"
STYLE_RULES = ("prose.em-dash", "prose.en-dash-separator", "prose.banned-opener", "prose.banned-phrase")
BUNDLE = {  # source path under the skills folder -> path under .harness/ci/
    "ci-enforcement/check.py": "ci-enforcement/check.py",
    "ci-enforcement/guard.py": "ci-enforcement/guard.py",
    "ci-enforcement/allowed-models.txt": "ci-enforcement/allowed-models.txt",
    "no-ai-trailer/scripts/ai_trailer.py": "no-ai-trailer/scripts/ai_trailer.py",
    "human/scripts/banned_phrase_scan.py": "human/scripts/banned_phrase_scan.py",
    "human/scripts/_lang.py": "human/scripts/_lang.py",
    "concision-and-logic/scripts/draft_scan.py": "concision-and-logic/scripts/draft_scan.py",
}
SCP_RE = re.compile(r"^(?:[^@/]+@)?([^/:]+):(?!//)(.+)$")  # git@host:owner/repo.git

PRE_COMMIT = f"""#!/bin/sh
{HOOK_MARK}
# Checks the working-tree copy of each staged file. Remove this file to stop the check.
C="$(git rev-parse --show-toplevel)/.harness/ci/ci-enforcement/check.py"
[ -f "$C" ] || exit 0
git diff --cached --name-only --diff-filter=ACMR -z | xargs -0 -r sh -c '
  python3 -B "$0" prose "$@" && python3 -B "$0" secrets "$@" && python3 -B "$0" unicode "$@"' "$C"
"""
COMMIT_MSG = f"""#!/bin/sh
{HOOK_MARK}
C="$(git rev-parse --show-toplevel)/.harness/ci/ci-enforcement/check.py"
[ -f "$C" ] || exit 0
# Check only the message: drop the diff that `git commit -v` appends below the scissors line.
MSG="$(mktemp)"
sed '/^# ------------------------ >8 ------------------------$/,$d' "$1" > "$MSG"
python3 -B "$C" attribution --pr-body-file "$MSG"; code=$?
rm -f "$MSG"
exit $code
"""


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def parse_remote(url: str) -> tuple[str, str, str]:
    """Return (host kind, host, owner) for a remote URL; kind is github, gitlab or other."""
    from urllib.parse import urlsplit
    url = url.strip()
    if "://" in url:
        parts = urlsplit(url)
        host, path = (parts.hostname or "").lower(), parts.path
    else:
        m = SCP_RE.match(url)
        if not m:
            return "other", "", ""
        host, path = m.group(1).lower(), m.group(2)
    segments = [seg for seg in path.strip("/").split("/") if seg]
    if not host or len(segments) < 2:  # owner plus at least one more segment (GitLab allows subgroups)
        return "other", host, ""
    owner = segments[0]
    kind = "github" if "github" in host else "gitlab" if "gitlab" in host else "other"
    return kind, host, owner


def signed_in_account(kind: str) -> str | None:
    commands = {"github": ["gh", "api", "user", "--jq", ".login"], "gitlab": ["glab", "api", "user"]}
    if kind not in commands or not shutil.which(commands[kind][0]):
        return None
    try:
        out = subprocess.run(commands[kind], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    text = out.stdout.strip()
    if kind == "gitlab":
        try:
            return json.loads(text).get("username")
        except ValueError:
            return None
    return text or None


def decide_profile(args, repo: Path, kind: str, owner: str) -> tuple[str, str]:
    if args.profile:
        return args.profile, "given on the command line"
    config, _ = h.find_repo_config(repo)
    if config.get("ci_profile") in ("own", "external"):
        return config["ci_profile"], "ci_profile in .harness.toml"
    account = signed_in_account(kind)
    if account is None:
        return "external", "could not read the signed-in account, so style rules stay advisory"
    if account.lower() == owner.lower():
        return "own", f"remote owner {owner} is the signed-in account"
    return "external", f"remote owner {owner} is not the signed-in account {account}"


def skills_source() -> Path:
    for candidate in (h.HARNESS_HOME.parent / "skills", Path.home() / ".claude" / "skills",
                      Path.home() / ".agents" / "skills"):
        if (candidate / "ci-enforcement" / "check.py").is_file():
            return candidate
    raise SystemExit("ci-install: the ci-enforcement skill is not installed; run the installer first")


def profiled_registry(text: str, profile: str) -> str:
    if profile == "own":
        return text
    for rule_id in STYLE_RULES:
        text, count = re.subn(rf'(- id: "{re.escape(rule_id)}"\n(?:    [a-z]+: "[^"]*"\n)*?    enforcement: )"gate"',
                              r'\1"advisory"', text)
        if count != 1:  # never install an "external" registry that still gates style by accident
            raise SystemExit(f"ci-install: could not make {rule_id} advisory; rules.yaml format changed")
    return text


def run(args) -> int:
    top = git(Path(args.repo).expanduser().resolve(), "rev-parse", "--show-toplevel")
    if not top:
        print(f"ci-install: {args.repo} is not inside a git repository")
        return 2
    repo = Path(top)
    remote = git(repo, "remote", "get-url", "origin") or next(
        (git(repo, "remote", "get-url", r) for r in git(repo, "remote").split()), "")
    kind, host, owner = parse_remote(remote)
    profile, why = decide_profile(args, repo, kind, owner)
    src = skills_source()
    templates = src / "ci-enforcement" / "templates"

    plan: list[tuple[Path, str, bool]] = []  # (path, content, executable)
    for rel_src, rel_dst in BUNDLE.items():
        plan.append((repo / ".harness" / "ci" / rel_dst, (src / rel_src).read_text(encoding="utf-8"), False))
    registry = profiled_registry((src / "ci-enforcement" / "rules.yaml").read_text(encoding="utf-8"), profile)
    plan.append((repo / ".harness" / "ci" / "ci-enforcement" / "rules.yaml", registry, False))
    notes = []
    if kind == "github":
        text = (templates / "harness-rules.github.yml").read_text(encoding="utf-8").replace("{profile}", profile)
        plan.append((repo / ".github" / "workflows" / "harness-rules.yml", text, False))
    elif kind == "gitlab":
        text = (templates / "harness-rules.gitlab.yml").read_text(encoding="utf-8").replace("{profile}", profile)
        plan.append((repo / ".gitlab" / "harness-rules.yml", text, False))
        ci_file = repo / ".gitlab-ci.yml"
        if not ci_file.exists():
            plan.append((ci_file, "include:\n  - local: .gitlab/harness-rules.yml\n", False))
        elif "harness-rules.yml" not in ci_file.read_text(encoding="utf-8"):
            notes.append("add `include: [{local: .gitlab/harness-rules.yml}]` to .gitlab-ci.yml; "
                         "it was left untouched")
    else:
        hooks_path = git(repo, "config", "core.hooksPath")
        # In a linked worktree .git is a file; ask git where the hooks folder really is.
        hooks = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "hooks"
        if hooks_path:
            notes.append(f"core.hooksPath is {hooks_path}, so git would ignore {hooks}; no local hooks written")
        else:
            for name, body in (("pre-commit", PRE_COMMIT), ("commit-msg", COMMIT_MSG)):
                target = hooks / name
                if target.exists() and HOOK_MARK not in target.read_text(encoding="utf-8", errors="replace"):
                    notes.append(f"{name} hook exists and is not ours; left untouched")
                    continue
                plan.append((target, body, True))
        notes.append(f"remote host {host or 'unknown'} has no supported CI; local git hooks only")

    print(f"ci-install: {repo}")
    print(f"  host: {kind}{' (' + host + ')' if host else ''}; profile: {profile} ({why})")
    written = []
    for path, content, executable in plan:
        try:
            rel = path.relative_to(repo)
        except ValueError:  # hooks of a linked worktree live in the main repository
            rel = path
        if path.exists() and path.read_text(encoding="utf-8", errors="replace") == content:
            continue
        if not args.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            if executable:
                path.chmod(0o755)
        written.append(str(rel))
    verb = "would write" if args.dry_run else "wrote"
    print(f"  {verb} {len(written)} file(s)" + (":" if written else "; everything is current"))
    for rel in written:
        print(f"    {rel}")
    for note in notes:
        print(f"  note: {note}")
    if written and not args.dry_run and kind in ("github", "gitlab"):
        print("  nothing is committed or pushed; review the files, then commit them yourself")
    return 0
