#!/usr/bin/env python3
"""Deterministic CI checker for the rules in rules.yaml. Standard library only.

Subcommands
    rules        check the registry against the checkers in this file and in guard.py
    prose        em dash, en dash separator, banned openers and phrases in changed prose files
    attribution  AI attribution in commit messages and in the pull request title and body
    commits      commit author and committer against an identity allowlist
    models       model ids in plan profiles, agents and workflows against an allowlist
    ui           Playwright plus axe-core at project widths, 400 percent zoom and colour schemes

Exit codes: 0 no gate finding (advisories may print), 1 at least one gate finding,
2 usage error or a missing tool. A missing tool never passes silently.

Sibling skills are imported from the same skills folder, so this file works both in the
repository (skills/ci-enforcement/) and in a generated copy (.claude/skills/ci-enforcement/).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent
for sub in ("no-ai-trailer/scripts", "human/scripts", "concision-and-logic/scripts"):
    sys.path.insert(0, str(SKILLS / sub))

# Checker id -> (subcommand, what it reports). rules.yaml must name each one exactly once.
CHECKERS = {
    "prose.em-dash": ("prose", "em dash in prose"),
    "prose.en-dash-separator": ("prose", "spaced en dash used as a separator"),
    "prose.banned-opener": ("prose", "sentence opens with a banned opener"),
    "prose.banned-phrase": ("prose", "hard-severity phrase from banned_phrase_scan.py"),
    "prose.ai-tell": ("prose", "soft phrase or draft_scan.py tell (advisory)"),
    "attribution.commit": ("attribution", "AI attribution line in a commit message"),
    "attribution.pr": ("attribution", "AI attribution line in the PR title or body"),
    "commits.identity": ("commits", "author or committer not on the allowlist"),
    "models.allowlist": ("models", "model id not on the allowlist"),
    "models.agent-tier": ("models", "agent names a model or an unknown tier"),
    "ui.axe": ("ui", "axe-core WCAG 2.2 A or AA violation"),
    "ui.target-size": ("ui", "pointer target under 24 CSS px without spacing"),
    "ui.reflow": ("ui", "horizontal scroll at 320 CSS px"),
}

PROSE_SUFFIXES = {".md", ".mdx", ".markdown", ".txt", ".rst"}
DEFAULT_EXCLUDES = [
    ".agents/*", ".claude/*", ".opencode/*", ".cursor/*", ".codex/*", ".gemini/*", ".windsurf/*",
    ".kiro/*", "*/.agents/*", "*/.claude/*", "*/.opencode/*", "*/.cursor/*", "*/.codex/*",
    "*/.gemini/*", "*/.windsurf/*", "*/.kiro/*", "*/integrations/*", "*/harness/dist/*",
    "*/node_modules/*", "node_modules/*", "*/fixtures/*", "*CHANGELOG*",
]
BANNED_OPENERS = [
    "Let's", "In order to", "It's worth noting", "Needless to say", "At the end of the day",
    "It goes without saying", "Simply put",
]
TIERS = {"frontier", "lead", "worker", "light", "inherit"}


@dataclass
class Finding:
    checker: str
    where: str
    message: str
    line: int = 0

    @property
    def gate(self) -> bool:
        return self.checker in GATE_CHECKERS


GATE_CHECKERS: set[str] = set()


# ---------------------------------------------------------------- registry

def load_registry(path: Path) -> list[dict]:
    """Read the rules.yaml subset: `rules:` then `- key: "value"` entries with indented keys."""
    rules: list[dict] = []
    current: dict | None = None
    seen_root = False
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        if line == "rules:":
            seen_root = True
            continue
        m = re.match(r"^\s*(-\s+)?([a-z][a-z_-]*):\s+(\".*\")$", line)
        if not seen_root or not m:
            raise ValueError(f"{path}:{number}: outside the supported subset: {raw!r}")
        if m.group(1):
            current = {}
            rules.append(current)
        if current is None:
            raise ValueError(f"{path}:{number}: key before the first list item")
        current[m.group(2)] = json.loads(m.group(3))
    return rules


def registry_problems(rules: list[dict], known: set[str]) -> list[str]:
    """Gate rule without checker, checker without rule, unknown checker, duplicate, bad field."""
    problems = []
    fields = {"id", "rule", "source", "checker", "scope", "enforcement", "runs"}
    ids: set[str] = set()
    used: dict[str, str] = {}
    for rule in rules:
        rid = rule.get("id", "?")
        missing = fields - rule.keys()
        if missing:
            problems.append(f"{rid}: missing {sorted(missing)}")
        if rid in ids:
            problems.append(f"{rid}: duplicate id")
        ids.add(rid)
        if rule.get("scope") not in {"prose", "commits", "ui", "config"}:
            problems.append(f"{rid}: scope must be prose, commits, ui or config")
        if rule.get("enforcement") not in {"gate", "advisory"}:
            problems.append(f"{rid}: enforcement must be gate or advisory")
        checker = rule.get("checker", "none")
        if checker == "none":
            if rule.get("enforcement") == "gate":
                problems.append(f"{rid}: gate rule has no checker")
            continue
        cid = checker.split()[-1]
        if cid not in known:
            problems.append(f"{rid}: checker {checker!r} does not exist")
        if cid in used:
            problems.append(f"{rid}: checker {cid} already enforces {used[cid]}")
        used[cid] = rid
    for cid in sorted(known - used.keys()):
        problems.append(f"checker {cid} has no rule in the registry")
    return problems


def known_checkers() -> set[str]:
    sys.path.insert(0, str(HERE))
    import guard  # noqa: E402

    return set(CHECKERS) | set(guard.GUARDS)


def set_gates(registry: Path) -> None:
    GATE_CHECKERS.clear()
    for rule in load_registry(registry):
        if rule.get("enforcement") == "gate" and rule.get("checker", "none") != "none":
            GATE_CHECKERS.add(rule["checker"].split()[-1])


def cmd_rules(args) -> list[Finding]:
    problems = registry_problems(load_registry(Path(args.registry)), known_checkers())
    for problem in problems:
        print(f"REGISTRY {problem}")
    if problems:
        raise SystemExit(1)
    print(f"registry: {len(load_registry(Path(args.registry)))} rules, every gate rule has a checker")
    return []


# ---------------------------------------------------------------- git helpers

def git(repo: str, *argv: str) -> str:
    out = subprocess.run(["git", "-C", repo, *argv], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"error: git {' '.join(argv)}: {out.stderr.strip()}")
    return out.stdout


def changed_files(repo: str, base: str, head: str) -> list[str]:
    text = git(repo, "diff", "--name-only", "--diff-filter=ACMR", "-z", f"{base}...{head}")
    return [name for name in text.split("\0") if name]


# ---------------------------------------------------------------- prose

def front_matter(text: str) -> dict:
    """Top-level `key: value` pairs of a leading YAML block; enough for origin and model fields."""
    m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    data = {}
    for line in (m.group(1).splitlines() if m else []):
        kv = re.match(r"^([A-Za-z][\w-]*):\s*(.*?)\s*$", line)
        if kv:
            data[kv.group(1)] = kv.group(2).strip("\"'")
    return data


def mask_prose(text: str) -> str:
    """Blank code fences, inline code, block quotes and HTML comments; keep line numbers."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))  # noqa: E731
    text = re.sub(r"(?ms)^(\s*)(```|~~~).*?^\s*\2[^\n]*$", blank, text)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.DOTALL)
    text = re.sub(r"(`+)[^`\n]+?\1", blank, text)
    return re.sub(r"(?m)^\s*>.*$", blank, text)


OPENER_RE = re.compile(
    r"(?:^|[.!?:]\s+|^\s*(?:[-*+]|\d+[.)]|#+)\s+|\|\s*|\*\*)(?:\*\*)?("
    + "|".join(re.escape(o).replace("'", "['’]") for o in BANNED_OPENERS)
    + r")\b",
    re.IGNORECASE,
)
PLACEHOLDER_CELL = re.compile(r"\|\s*[—–]\s*(?=\|)")


def prose_findings(path: str, text: str) -> list[Finding]:
    if front_matter(text).get("origin") == "third-party":
        return []
    findings = []
    masked = mask_prose(text)
    for number, line in enumerate(masked.splitlines(), start=1):
        scan = PLACEHOLDER_CELL.sub("| ", line) if line.lstrip().startswith("|") else line
        if "—" in scan:
            findings.append(Finding("prose.em-dash", path, "em dash: use a comma, a colon or two sentences", number))
        if re.search(r"\s–\s|^–\s", scan):
            findings.append(Finding("prose.en-dash-separator", path, "en dash used as a separator", number))
        for m in OPENER_RE.finditer(scan):
            findings.append(Finding("prose.banned-opener", path, f"banned opener {m.group(1)!r}", number))
    findings += phrase_findings(path, text)
    return findings


def phrase_findings(path: str, text: str) -> list[Finding]:
    import banned_phrase_scan
    import draft_scan

    findings = []
    for v in banned_phrase_scan.scan_for_violations(text):
        checker = "prose.banned-phrase" if v["severity"] == "hard" else "prose.ai-tell"
        hint = f" ({v['suggestion']})" if v.get("suggestion") else ""
        findings.append(Finding(checker, path, f"{v['category']}: {v['phrase']!r}{hint}", v["line_number"]))
    for f in draft_scan.scan(text).get("findings", []):
        if f["category"] == "dash":
            continue  # reported by prose.em-dash and prose.en-dash-separator
        findings.append(Finding("prose.ai-tell", path, f"{f['category']}: {f['match']!r}", f["line"]))
    return findings


def excluded(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def cmd_prose(args) -> list[Finding]:
    repo = Path(args.repo)
    if args.paths:
        names = args.paths
    elif args.base:
        names = changed_files(args.repo, args.base, args.head)
    else:
        raise SystemExit("error: give PATHs or --base and --head")
    patterns = DEFAULT_EXCLUDES + args.exclude
    findings = []
    for name in names:
        path = Path(name) if Path(name).is_absolute() else repo / name
        if path.suffix.lower() not in PROSE_SUFFIXES or excluded(name, patterns) or not path.is_file():
            continue
        findings += prose_findings(name, path.read_text(encoding="utf-8", errors="replace"))
    return findings


# ---------------------------------------------------------------- attribution

def commit_messages(repo: str, base: str, head: str) -> list[tuple[str, str]]:
    raw = git(repo, "log", "--format=%H%x1f%B%x1e", f"{base}..{head}")
    out = []
    for record in raw.split("\x1e"):
        if "\x1f" in record:
            sha, body = record.strip("\n").split("\x1f", 1)
            out.append((sha, body))
    return out


def cmd_attribution(args) -> list[Finding]:
    from ai_trailer import find

    findings = []
    if args.base:
        for sha, body in commit_messages(args.repo, args.base, args.head):
            for hit in find(body):
                findings.append(Finding("attribution.commit", sha[:12], f"AI attribution: {hit.strip()!r}"))
    texts = []
    if args.pr_body_file:
        texts.append(("pr-body", Path(args.pr_body_file).read_text(encoding="utf-8")))
    event = args.event or os.environ.get("GITHUB_EVENT_PATH")
    if event and Path(event).is_file():
        pr = json.loads(Path(event).read_text(encoding="utf-8")).get("pull_request") or {}
        texts += [("pr-title", pr.get("title") or ""), ("pr-body", pr.get("body") or "")]
    for where, text in texts:
        for hit in find(text):
            findings.append(Finding("attribution.pr", where, f"AI attribution: {hit.strip()!r}"))
    if not args.base and not texts:
        raise SystemExit("error: give --base/--head, --pr-body-file or --event")
    return findings


# ---------------------------------------------------------------- commits

def parse_identity(text: str) -> tuple[str, str]:
    m = re.match(r"^\s*(.*?)\s*<([^>]*)>\s*$", text)
    return (m.group(1), m.group(2).lower()) if m else (text.strip(), "")


def load_identities(path: str) -> dict[str, list[tuple[str, str]]]:
    """Lines `author: Name <email>`, `committer: ...` or `both: ...`; `<email>` alone skips the name."""
    allow: dict[str, list[tuple[str, str]]] = {"author": [], "committer": []}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        role, _, value = line.partition(":")
        role = role.strip().lower()
        if role not in {"author", "committer", "both"} or "<" not in value:
            raise SystemExit(f"error: {path}: cannot read {raw!r}")
        for r in (("author", "committer") if role == "both" else (role,)):
            allow[r].append(parse_identity(value))
    return allow


def allowed(name: str, email: str, entries: list[tuple[str, str]]) -> bool:
    return any(email.lower() == e and (not n or n == name) for n, e in entries)


def cmd_commits(args) -> list[Finding]:
    allow = load_identities(args.allow_file)
    raw = git(args.repo, "log", "--format=%H%x1f%an%x1f%ae%x1f%cn%x1f%ce", f"{args.base}..{args.head}")
    findings = []
    for line in raw.splitlines():
        sha, an, ae, cn, ce = line.split("\x1f")
        if not allowed(an, ae, allow["author"]):
            findings.append(Finding("commits.identity", sha[:12], f"author {an} <{ae}> is not allowed"))
        if not allowed(cn, ce, allow["committer"]):
            findings.append(Finding("commits.identity", sha[:12], f"committer {cn} <{ce}> is not allowed"))
    return findings


# ---------------------------------------------------------------- models

def load_models(path: str) -> set[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return {line.split("#", 1)[0].strip() for line in lines if line.split("#", 1)[0].strip()}


MODEL_IN_CODE = re.compile(r"\bmodel\s*[:=]\s*[\"'`]([^\"'`]*)[\"'`]")


def cmd_models(args) -> list[Finding]:
    root = Path(args.root)
    allow = load_models(args.allow_file)
    findings = []

    def check(where: str, value: str, line: int = 0) -> None:
        if value and value not in allow:
            findings.append(Finding("models.allowlist", where, f"model {value!r} is not allowlisted", line))

    for path in sorted(root.glob("harness/profiles/*.toml")):
        rel = str(path.relative_to(root))
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for table in ("tiers", "opencode"):
            for tier, value in (data.get(table) or {}).items():
                check(f"{rel} [{table}].{tier}", str(value))
        for value in data.get("available") or []:
            check(f"{rel} available", str(value))
        for value in (data.get("efforts") or {}):
            check(f"{rel} [efforts]", str(value))
    for path in sorted(root.glob("harness/agents/*.md")):
        rel = str(path.relative_to(root))
        fm = front_matter(path.read_text(encoding="utf-8"))
        if "model" in fm:
            findings.append(Finding("models.agent-tier", rel, f"agent names model {fm['model']!r}; declare a tier"))
        if fm.get("tier") not in TIERS:
            findings.append(Finding("models.agent-tier", rel, f"unknown tier {fm.get('tier')!r}"))
    for pattern in ("workflows/*.md", "harness/workflows/*.js", ".claude/agents/*.md"):
        for path in sorted(root.glob(pattern)):
            rel = str(path.relative_to(root))
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".md":
                fm = front_matter(text)
                if "model" in fm and fm["model"] != "inherit":
                    check(rel, fm["model"])
                continue
            for m in MODEL_IN_CODE.finditer(text):
                check(rel, m.group(1), text.count("\n", 0, m.start()) + 1)
    return findings


# ---------------------------------------------------------------- ui

def viewports(config: dict) -> list[dict]:
    height = int(config.get("height", 800))
    ports = [{"label": f"w{w}", "width": int(w), "height": height, "scale": 1}
             for w in config.get("widths", [320, 768, 1280])]
    ports.append({"label": "zoom-400", "width": 320, "height": 256, "scale": 4})
    return ports


def circle_hits_rect(cx: float, cy: float, r: float, box: dict) -> bool:
    nx = min(max(cx, box["x"]), box["x"] + box["width"])
    ny = min(max(cy, box["y"]), box["y"] + box["height"])
    return math.hypot(cx - nx, cy - ny) < r


def undersized_without_spacing(targets: list[dict]) -> list[dict]:
    """WCAG 2.5.8: a target under 24x24 passes when a 24 px circle on its centre touches no other
    target and no other undersized target's circle. Inline targets in text are exempt."""
    def centre(t):
        return t["x"] + t["width"] / 2, t["y"] + t["height"] / 2

    small = [t for t in targets if not t.get("inline") and (t["width"] < 24 or t["height"] < 24)]
    bad = []
    for t in small:
        cx, cy = centre(t)
        for o in targets:
            if o is t:
                continue
            if circle_hits_rect(cx, cy, 12, o):
                bad.append(t)
                break
            if o in small and math.hypot(cx - centre(o)[0], cy - centre(o)[1]) < 24:
                bad.append(t)
                break
    return bad


def evaluate_ui(results: list[dict]) -> list[Finding]:
    findings = []
    for r in results:
        where = f"{r['url']} @{r['viewport']['label']}" + (f" {r['scheme']}" if r.get("scheme") else "")
        if r.get("error"):
            findings.append(Finding("ui.axe", where, f"page failed to load: {r['error']}"))
            continue
        for v in r.get("axe", []):
            findings.append(Finding("ui.axe", where, f"{v['id']} ({v.get('impact')}): {v.get('help')}, {v.get('nodes')} node(s)"))
        for t in undersized_without_spacing(r.get("targets", [])):
            findings.append(Finding("ui.target-size", where, f"{t['selector']} is {t['width']:.0f}x{t['height']:.0f} px"))
        if r["viewport"]["width"] <= 320 and r.get("scrollWidth", 0) > r.get("clientWidth", 0) + 1:
            findings.append(Finding("ui.reflow", where, f"page is {r['scrollWidth']} px wide in a {r['clientWidth']} px viewport"))
    return findings


def cmd_ui(args) -> list[Finding]:
    if args.from_json:
        return evaluate_ui(json.loads(Path(args.from_json).read_text(encoding="utf-8")))
    config = json.loads(Path(args.config).read_text(encoding="utf-8")) if args.config else {}
    if args.url:
        config["urls"] = args.url
    if not config.get("urls"):
        raise SystemExit("error: give --config with urls, or --url")
    node = shutil.which("node")
    if not node:
        raise SystemExit("error: node is not on PATH; the ui check needs Node, Playwright and axe-core")
    job = {"urls": config["urls"], "viewports": viewports(config),
           "schemes": config.get("color_schemes", ["light"])}
    out = subprocess.run([node, str(HERE / "ui_probe.cjs")], input=json.dumps(job),
                         capture_output=True, text=True, timeout=args.timeout)
    if out.returncode != 0:
        raise SystemExit(f"error: ui probe failed: {out.stderr.strip()}")
    results = json.loads(out.stdout)
    if args.save_json:
        Path(args.save_json).write_text(json.dumps(results, indent=2), encoding="utf-8")
    return evaluate_ui(results)


# ---------------------------------------------------------------- main

def report(findings: list[Finding], fmt: str, advisory_cap: int) -> int:
    gates = [f for f in findings if f.gate]
    advisories = [f for f in findings if not f.gate]
    for f in gates:
        loc = f"{f.where}:{f.line}" if f.line else f.where
        if fmt == "github":
            pos = f"file={f.where},line={f.line}," if f.line else ""
            print(f"::error {pos}title={f.checker}::{f.message}")
        print(f"GATE {f.checker} {loc} {f.message}")
    shown: dict[str, int] = {}
    for f in advisories:
        shown[f.where] = shown.get(f.where, 0) + 1
        if shown[f.where] <= advisory_cap:
            loc = f"{f.where}:{f.line}" if f.line else f.where
            print(f"ADVISORY {f.checker} {loc} {f.message}")
    hidden = len(advisories) - sum(min(n, advisory_cap) for n in shown.values())
    if hidden > 0:
        print(f"ADVISORY ({hidden} more not shown; raise --advisory-cap to list them)")
    print(f"summary: {len(gates)} gate finding(s), {len(advisories)} advisory finding(s)")
    return 1 if gates else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--registry", default=str(HERE / "rules.yaml"))
    parser.add_argument("--format", choices=["text", "github"], default="text")
    parser.add_argument("--advisory-cap", type=int, default=10, help="advisories shown per file")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("rules")

    def range_args(p, required=False):
        p.add_argument("--repo", default=".")
        p.add_argument("--base", required=required)
        p.add_argument("--head", default="HEAD")

    p = sub.add_parser("prose")
    range_args(p)
    p.add_argument("--exclude", action="append", default=[], help="extra glob to skip")
    p.add_argument("paths", nargs="*")

    p = sub.add_parser("attribution")
    range_args(p)
    p.add_argument("--pr-body-file")
    p.add_argument("--event", help="GitHub event JSON; defaults to $GITHUB_EVENT_PATH")

    p = sub.add_parser("commits")
    range_args(p, required=True)
    p.add_argument("--allow-file", required=True)

    p = sub.add_parser("models")
    p.add_argument("--root", default=".")
    p.add_argument("--allow-file", default=str(HERE / "allowed-models.txt"))

    p = sub.add_parser("ui")
    p.add_argument("--config", help="JSON: urls, widths, height, color_schemes")
    p.add_argument("--url", action="append")
    p.add_argument("--from-json", help="evaluate saved probe output instead of running a browser")
    p.add_argument("--save-json")
    p.add_argument("--timeout", type=int, default=600)

    args = parser.parse_args(argv)
    set_gates(Path(args.registry))
    handler = {"rules": cmd_rules, "prose": cmd_prose, "attribution": cmd_attribution,
               "commits": cmd_commits, "models": cmd_models, "ui": cmd_ui}[args.command]
    try:
        findings = handler(args)
    except SystemExit as stop:
        if isinstance(stop.code, str):
            print(stop.code, file=sys.stderr)
            return 2
        return int(stop.code or 0)
    if args.command == "rules":
        return 0
    return report(findings, args.format, args.advisory_cap)


if __name__ == "__main__":
    sys.exit(main())
