#!/usr/bin/env python3
"""prompt-orchestrator installer: an interactive menu, or flags for scripts and CI.

    python3 install/install.py                       menu (core + harness selected)
    python3 install/install.py --yes                 install everything, no menu
    python3 install/install.py --core --yes          core skills and workflows only
    python3 install/install.py --tools claude,codex --profile-claude claude-max --yes
    python3 install/install.py --uninstall-harness [--tools claude]

Works on Windows, macOS and Linux with the Python standard library. The core installers are the
existing per-tool scripts (bash, or PowerShell on Windows). The harness needs Python 3.11 or later.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

INSTALL_DIR = Path(__file__).resolve().parent
ROOT = INSTALL_DIR.parent
HARNESS_INSTALLER = ROOT / "harness" / "scripts" / "install_harness.py"
WINDOWS = os.name == "nt"

# tool id: (label, core script stem or None when the harness is the only part)
TOOLS = {
    "claude": ("Claude Code", "install-claude"),
    "codex": ("OpenAI Codex", "install-codex"),
    "opencode": ("OpenCode", "install-opencode"),
    "cursor": ("Cursor", "install-cursor"),
    "gemini": ("Gemini CLI", "install-gemini"),
    "antigravity": ("Antigravity", "install-antigravity"),
    "openclaw": ("OpenClaw", "install-openclaw"),
    "copilot": ("GitHub Copilot (harness agents only)", None),
    "kiro": ("Kiro (harness agents only)", None),
}
DEFAULT_TOOLS = ["claude", "codex", "opencode", "cursor", "gemini", "antigravity", "openclaw"]
GLOBAL_ITEMS = {
    "subagent_model": "Claude: run unnamed subagents on Sonnet (CLAUDE_CODE_SUBAGENT_MODEL=sonnet)",
    "statusline": "Claude: harness status line (quota cache and display; wraps an existing one)",
    "hooks": "Hooks: mode tag, frontier gate, verify gate (Claude and Codex)",
    "legacy_move": "Claude: move the legacy Kiro rules file ~/.claude/rules/instructions.instructions.md to a backup",
}
PROFILES = {"claude": ["", "claude-max", "claude-pro", "api", "free"], "codex": ["", "codex-plus", "api", "free"]}


def harness_python_ok() -> bool:
    return sys.version_info >= (3, 11)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--core", action="store_true", help="install core only, no harness")
    p.add_argument("--with-harness", action="store_true", help="install core and harness (the default)")
    p.add_argument("--harness-only", action="store_true", help="add the harness to an existing core install")
    p.add_argument("--yes", "-y", action="store_true", help="no menu; use defaults and flags")
    p.add_argument("--tools", default=None, help="comma-separated tool ids: " + ",".join(TOOLS))
    p.add_argument("--profile-claude", default=None, choices=[x for x in PROFILES["claude"] if x])
    p.add_argument("--profile-codex", default=None, choices=[x for x in PROFILES["codex"] if x])
    for item in GLOBAL_ITEMS:
        p.add_argument(f"--no-{item.replace('_', '-')}", action="store_true")
    p.add_argument("--no-regenerate", action="store_true", help="skip tools/generate_integrations.py")
    p.add_argument("--uninstall-harness", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    args = p.parse_args(argv)
    if args.tools:
        unknown = [t for t in args.tools.split(",") if t not in TOOLS]
        if unknown:
            p.error(f"unknown tool(s): {', '.join(unknown)}")
    return args


def initial_plan(args) -> dict:
    tools = args.tools.split(",") if args.tools else list(DEFAULT_TOOLS)
    return {
        "tools": tools,
        "core": not args.harness_only,
        "harness": not args.core,
        "globals": {item: not getattr(args, f"no_{item}") for item in GLOBAL_ITEMS},
        "profile_claude": args.profile_claude or "",
        "profile_codex": args.profile_codex or "",
    }


def show(plan: dict) -> None:
    print("\nprompt-orchestrator installer\n")
    print(f"  [c] core skills and workflows: {'yes' if plan['core'] else 'no'}")
    print(f"  [h] harness (model tiers, plan modes, agents): {'yes' if plan['harness'] else 'no'}"
          + ("" if harness_python_ok() else "  (needs Python 3.11+, will be skipped)"))
    print("\n  Tools:")
    for i, (tool, (label, _)) in enumerate(TOOLS.items(), 1):
        print(f"   {i}. [{'x' if tool in plan['tools'] else ' '}] {label}")
    print("\n  Global machine changes (backed up, reversed by uninstall):")
    for i, (item, label) in enumerate(GLOBAL_ITEMS.items(), 1):
        print(f"   g{i}. [{'x' if plan['globals'][item] else ' '}] {label}")
    print(f"\n  [pc] Claude plan profile: {plan['profile_claude'] or 'not set (run /autosetup later)'}")
    print(f"  [px] Codex plan profile:  {plan['profile_codex'] or 'not set (discovered at install)'}")
    print("\n  Number or g# toggles, a = all tools, n = no tools, c/h toggle parts, pc/px cycle profiles,")
    print("  Enter = install, q = quit")


def menu(plan: dict) -> dict | None:
    names = list(TOOLS)
    items = list(GLOBAL_ITEMS)
    while True:
        show(plan)
        try:
            choice = input("\n> ").strip().lower()
        except EOFError:
            return plan
        if choice == "":
            return plan
        if choice == "q":
            return None
        if choice == "a":
            plan["tools"] = list(names)
        elif choice == "n":
            plan["tools"] = []
        elif choice == "c":
            plan["core"] = not plan["core"]
        elif choice == "h":
            plan["harness"] = not plan["harness"]
        elif choice in ("pc", "px"):
            key, options = ("profile_claude", PROFILES["claude"]) if choice == "pc" else ("profile_codex", PROFILES["codex"])
            plan[key] = options[(options.index(plan[key]) + 1) % len(options)]
        elif choice.startswith("g") and choice[1:].isdigit() and 1 <= int(choice[1:]) <= len(items):
            item = items[int(choice[1:]) - 1]
            plan["globals"][item] = not plan["globals"][item]
        elif choice.isdigit() and 1 <= int(choice) <= len(names):
            tool = names[int(choice) - 1]
            plan["tools"] = [t for t in plan["tools"] if t != tool] if tool in plan["tools"] else plan["tools"] + [tool]
        else:
            print("  unknown choice")


def run(cmd: list[str], dry: bool) -> int:
    print("  $ " + " ".join(cmd))
    if dry:
        return 0
    return subprocess.call(cmd)


def core_command(stem: str) -> list[str] | None:
    if WINDOWS:
        shell = shutil.which("pwsh") or shutil.which("powershell")
        script = INSTALL_DIR / f"{stem}.ps1"
        return [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)] if shell else None
    return [shutil.which("bash") or "bash", str(INSTALL_DIR / f"{stem}.sh")]


def regenerate(dry: bool) -> None:
    try:
        import yaml  # noqa: F401
    except ImportError:
        print("--- Skipping regeneration (PyYAML not available); using files already in the repo")
        return
    print("--- Regenerating integrations")
    run([sys.executable, str(ROOT / "tools" / "generate_integrations.py")], dry)


def harness_args(plan: dict, tool: str) -> list[str]:
    args = [sys.executable, str(HARNESS_INSTALLER), "install", "--tool", tool]
    profile = plan["profile_claude"] if tool in ("claude", "opencode") else plan["profile_codex"] if tool == "codex" else ""
    if profile:
        args += ["--profile", profile]
    for item, enabled in plan["globals"].items():
        if not enabled:
            args.append(f"--no-{item.replace('_', '-')}")
    return args


def execute(plan: dict, args) -> int:
    failures = []
    if plan["core"] and not args.no_regenerate:
        regenerate(args.dry_run)
    for tool in plan["tools"]:
        label, stem = TOOLS[tool]
        print(f"\n=== {label}")
        if plan["core"] and stem:
            cmd = core_command(stem)
            if cmd is None or run(cmd, args.dry_run) != 0:
                failures.append(f"{tool} core")
                continue
        if plan["harness"]:
            if not harness_python_ok():
                print("  harness skipped: needs Python 3.11 or later")
                continue
            if run(harness_args(plan, tool), args.dry_run) != 0:
                failures.append(f"{tool} harness")
    print("\n==> " + ("done" if not failures else "finished with failures: " + ", ".join(failures)))
    if plan["harness"] and "claude" in plan["tools"] and not plan["profile_claude"]:
        print("    Claude plan profile not set: run /autosetup in a Claude Code session.")
    print("    Project-scoped installs stay separate: install-project and install-windsurf.")
    return 1 if failures else 0


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.uninstall_harness:
        cmd = [sys.executable, str(HARNESS_INSTALLER), "uninstall"]
        for tool in (args.tools.split(",") if args.tools else []):
            cmd += ["--tool", tool]
        return run(cmd, args.dry_run)
    plan = initial_plan(args)
    if not args.yes and sys.stdin.isatty() and not args.dry_run:
        plan = menu(plan)
        if plan is None:
            print("cancelled")
            return 1
    elif args.dry_run:
        print(f"plan: {plan}")
    return execute(plan, args)


if __name__ == "__main__":
    sys.exit(main())
