#!/usr/bin/env python3
"""Install or remove the prompt-orchestrator harness for one or more tools (standard library only).

    install_harness.py install --tool claude [--profile claude-max] [--no-hooks] [--no-statusline]
                               [--no-subagent-model] [--no-legacy-move]
    install_harness.py uninstall [--tool claude]
    install_harness.py status

The core orchestrator must already be installed for the tool. Every change is recorded in an
install manifest; global files are backed up before the first change and uninstall removes only
what the harness added. Files at a target that lack the harness marker are never overwritten.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent  # harness/ in the repo, or the installed harness home
sys.path.insert(0, str(SRC / "scripts"))
import harness_lib as h  # noqa: E402
import render  # noqa: E402

TOOLS = ("claude", "codex", "opencode", "cursor", "copilot", "gemini", "antigravity", "kiro", "openclaw")
BLOCK_START = f"<!-- {h.MARKER}:start -->"
BLOCK_END = f"<!-- {h.MARKER}:end -->"
HOOK_TAG = "harness:"
LEGACY_KIRO = Path.home() / ".claude" / "rules" / "instructions.instructions.md"


# ---------------------------------------------------------------- locations

def data_home() -> Path:
    root = os.environ.get("PO_HARNESS_HOME")
    if root:
        return Path(root) / "data" / "harness"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "prompt-orchestrator" / "harness"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "prompt-orchestrator" / "harness"


def manifest_path() -> Path:
    return h.state_dir() / "install-manifest.json"


def backup_dir() -> Path:
    return h.state_dir() / "backups"


def load_manifest() -> dict:
    return h.read_json(manifest_path(), {}) or {}


def save_manifest(data: dict) -> None:
    h.write_json(manifest_path(), data)


def python_cmd() -> str:
    exe = sys.executable or ("py" if os.name == "nt" else "python3")
    return f'"{exe}"' if " " in exe else exe


def hook_cmd(script: str, *args: str) -> str:
    path = data_home() / "scripts" / script
    quoted = f'"{path}"' if " " in str(path) else str(path)
    return " ".join([python_cmd(), quoted, *args])


def backup(path: Path) -> str | None:
    """Copy a global file once per install run before its first change."""
    if not path.exists():
        return None
    target = backup_dir() / time.strftime("%Y%m%d-%H%M%S") / path.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return str(target)


# ---------------------------------------------------------------- primitives

class Recorder:
    def __init__(self, tool: str):
        self.tool = tool
        self.manifest = load_manifest()
        self.actions = self.manifest.setdefault("tools", {}).setdefault(tool, [])
        self.notes: list[str] = []

    def add(self, action: dict) -> None:
        if action not in self.actions:
            self.actions.append(action)

    def save(self) -> None:
        self.manifest["harness_home"] = str(data_home())
        save_manifest(self.manifest)


def write_marked(rec: Recorder, path: Path, text: str) -> bool:
    if path.exists() and h.MARKER not in path.read_text(encoding="utf-8", errors="replace"):
        rec.notes.append(f"skipped {path}: exists without the harness marker")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    rec.add({"type": "file", "path": str(path)})
    return True


def set_block(rec: Recorder, path: Path, content: str) -> None:
    """Replace or append the harness block in a shared text file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    text = strip_block(text)
    block = f"{BLOCK_START}\n{content.rstrip()}\n{BLOCK_END}\n"
    path.write_text((text.rstrip() + "\n\n" if text.strip() else "") + block, encoding="utf-8")
    rec.add({"type": "block", "path": str(path)})


def strip_block(text: str) -> str:
    start, end = text.find(BLOCK_START), text.find(BLOCK_END)
    if start == -1 or end == -1:
        return text
    return (text[:start].rstrip() + "\n" + text[end + len(BLOCK_END):].lstrip("\n")).rstrip() + "\n"


def install_tree(rec: Recorder, files: list[Path], src_root: Path, dest_root: Path, suffix_map=None) -> int:
    count = 0
    for src in files:
        rel = src.relative_to(src_root)
        if write_marked(rec, dest_root / rel, src.read_text(encoding="utf-8")):
            count += 1
    return count


def installed_profile(name: str) -> dict:
    """Profiles are read from the harness home, where discovery may have filled them."""
    if name == "generic":
        return {}
    data = h.read_toml(data_home() / "profiles" / f"{name}.toml")
    if not data:
        return h.load_profile(name)
    data.setdefault("name", name)
    data["modes"] = {**h.DEFAULT_MODES, **data.get("modes", {})}
    data["fanout"] = {**h.DEFAULT_FANOUT, **data.get("fanout", {})}
    return data


def render_into(rec: Recorder, tool: str, profile: str, dest_root: Path) -> int:
    tmp = h.state_dir() / "render-tmp" / tool
    if tmp.exists():
        shutil.rmtree(tmp)
    files = render.render_tool(tool, profile, tmp, profile=installed_profile(profile))
    count = install_tree(rec, files, tmp, dest_root)
    shutil.rmtree(tmp, ignore_errors=True)
    return count


def install_skill(rec: Recorder, dest_skills: Path) -> None:
    for skill in sorted((SRC / "skills").glob("*.md")):
        text = skill.read_text(encoding="utf-8")
        if h.MARKER not in text:
            text = text.replace("\n---\n", f"\n---\n<!-- {h.MARKER} -->\n", 1)
        write_marked(rec, dest_skills / skill.stem / "SKILL.md", text)


def install_home(rec: Recorder) -> None:
    """Copy scripts, profiles, agents and skills to the harness home the hooks run from."""
    home = data_home()
    if SRC.resolve() == home.resolve():
        return
    for folder in ("scripts", "profiles", "agents", "skills"):
        target = home / folder
        target.mkdir(parents=True, exist_ok=True)
        for src in (SRC / folder).glob("*"):
            if src.is_file() and not src.name.startswith("test_") and src.suffix in (".py", ".toml", ".md"):
                dest = target / src.name
                # Keep a codex-plus profile that discovery already filled on this machine.
                if folder == "profiles" and dest.exists() and src.name == "codex-plus.toml" \
                        and "available = [\"" in dest.read_text(encoding="utf-8"):
                    continue
                shutil.copy2(src, dest)
    for name in ("critical.toml", "HARNESS.md"):
        shutil.copy2(SRC / name, home / name)
    rec.manifest["harness_home"] = str(home)


def active_profile(provider: str, requested: str | None) -> str:
    if requested:
        if provider in ("claude", "codex") and installed_profile(requested).get("provider") in (provider, "any"):
            cfg = h.user_config()
            if cfg.get("profiles", {}).get(provider) != requested:
                cfg.setdefault("profiles", {})[provider] = requested
                cfg["plan_source"] = "installer"
                cfg["plan_set_at"] = time.strftime("%Y-%m-%d")
                h.write_user_config(cfg)
        return requested
    configured = h.user_config().get("profiles", {}).get(provider)
    return configured or h.FALLBACK_PROFILE.get(provider, "api")


def overlay_text() -> str:
    return (SRC / "HARNESS.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------- JSON settings merges

def merge_hooks(settings: dict, entries: dict) -> None:
    hooks = settings.setdefault("hooks", {})
    for event, groups in list(hooks.items()):
        kept = []
        for group in groups:
            inner = [x for x in group.get("hooks", []) if not str(x.get("statusMessage", "")).startswith(HOOK_TAG)
                     and h.MARKER not in str(x.get("command", ""))]
            if inner:
                kept.append({**group, "hooks": inner})
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    for event, (matcher, command, timeout, label) in entries.items():
        group = {"hooks": [{"type": "command", "command": command, "timeout": timeout,
                            "statusMessage": f"{HOOK_TAG} {label}"}]}
        if matcher:
            group["matcher"] = matcher
        hooks.setdefault(event, []).append(group)


def strip_hooks(settings: dict) -> None:
    merge_hooks(settings, {})
    if not settings.get("hooks"):
        settings.pop("hooks", None)


def edit_json(rec: Recorder, path: Path, editor) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else "{}"
    try:
        data = json.loads(text or "{}")
    except ValueError:
        raise SystemExit(f"refusing to edit {path}: it is not valid JSON")
    saved = backup(path)
    editor(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    rec.add({"type": "json", "path": str(path), "backup": saved})


# ---------------------------------------------------------------- per-tool installers

def install_claude(rec: Recorder, args) -> None:
    root = Path.home() / ".claude"
    profile = active_profile("claude", args.profile)
    n = render_into(rec, "claude", profile, root)
    install_skill(rec, root / "skills")
    write_marked(rec, root / "HARNESS.md", f"<!-- {h.MARKER} -->\n" + overlay_text())
    set_block(rec, root / "CLAUDE.md", "@HARNESS.md")
    wf = 0
    for src in sorted((SRC / "workflows").glob("*.js")):
        wf += write_marked(rec, root / "workflows" / src.name, f"// {h.MARKER}\n" + src.read_text(encoding="utf-8"))
    rec.notes.append(f"claude: {n} agents ({profile}), autosetup skill, HARNESS.md, {wf} workflows")

    state = rec.manifest.setdefault("claude_previous", {})

    def edit(settings: dict) -> None:
        if not args.no_subagent_model:
            env = settings.setdefault("env", {})
            if env.get("CLAUDE_CODE_SUBAGENT_MODEL") not in (None, "sonnet") and "subagent_model" not in state:
                state["subagent_model"] = env["CLAUDE_CODE_SUBAGENT_MODEL"]
            env["CLAUDE_CODE_SUBAGENT_MODEL"] = "sonnet"
            state.setdefault("subagent_model", None)
        if not args.no_statusline:
            current = settings.get("statusLine") or {}
            command = str(current.get("command", ""))
            if command and "statusline.py" not in command and "statusline" not in state:
                state["statusline"] = current
                cfg = h.user_config()
                cfg["statusline_wrap"] = command
                h.write_user_config(cfg)
            state.setdefault("statusline", None)
            settings["statusLine"] = {"type": "command", "command": hook_cmd("statusline.py"), "padding": 0}
        if not args.no_hooks:
            merge_hooks(settings, {
                "SessionStart": (None, hook_cmd("mode_hook.py", "start"), 10, "plan mode"),
                "UserPromptSubmit": (None, hook_cmd("mode_hook.py", "prompt"), 10, "plan mode"),
                "PreToolUse": ("Agent|Task", hook_cmd("fable_gate.py"), 10, "frontier gate"),
                "Stop": (None, hook_cmd("verify_gate.py"), 900, "verify gate"),
                "SubagentStop": (None, hook_cmd("verify_gate.py"), 900, "verify gate"),
            })
    edit_json(rec, root / "settings.json", edit)

    if not args.no_legacy_move and LEGACY_KIRO.exists():
        saved = backup(LEGACY_KIRO)
        LEGACY_KIRO.unlink()
        rec.add({"type": "moved", "path": str(LEGACY_KIRO), "backup": saved})
        rec.notes.append(f"moved legacy Kiro rules file to {saved}")


def install_codex(rec: Recorder, args) -> None:
    root = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    if args.discover and shutil.which("codex"):
        import subprocess
        proc = subprocess.run([sys.executable, str(data_home() / "scripts" / "harnessctl.py"), "codex-discover"],
                              capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            rec.notes.append("codex model discovery failed, fallback mapping kept: "
                             + (proc.stderr.strip().splitlines() or ["no output"])[-1])
    profile = active_profile("codex", args.profile)
    n = render_into(rec, "codex", profile, root)
    install_skill(rec, Path.home() / ".agents" / "skills")
    set_block(rec, root / "AGENTS.md", overlay_text())
    if not args.no_hooks:
        def edit(settings: dict) -> None:
            merge_hooks(settings, {
                "SessionStart": (None, hook_cmd("mode_hook.py", "start", "--provider", "codex"), 30, "plan mode"),
                "Stop": (None, hook_cmd("verify_gate.py"), 900, "verify gate"),
            })
        edit_json(rec, root / "hooks.json", edit)
    rec.notes.append(f"codex: {n} agents ({profile}), overlay in AGENTS.md, hooks.json")


def install_simple(rec: Recorder, tool: str, agent_root: Path, overlay: Path | None, skills: Path | None,
                   profile: str = "generic") -> None:
    n = render_into(rec, tool, profile, agent_root)
    if skills:
        install_skill(rec, skills)
    if overlay:
        if overlay.suffix == ".mdc":
            write_marked(rec, overlay, f"---\ndescription: prompt-orchestrator harness overlay\nalwaysApply: true\n---\n"
                                       f"<!-- {h.MARKER} -->\n" + overlay_text())
        elif overlay.name.endswith("-harness.md"):
            write_marked(rec, overlay, f"<!-- {h.MARKER} -->\n" + overlay_text())
        else:
            set_block(rec, overlay, overlay_text())
    rec.notes.append(f"{tool}: {n} agents ({profile})" + (f", overlay {overlay}" if overlay else ""))


def install_tool(tool: str, args) -> list[str]:
    rec = Recorder(tool)
    install_home(rec)
    home = Path.home()
    if tool == "claude":
        install_claude(rec, args)
    elif tool == "codex":
        install_codex(rec, args)
    elif tool == "opencode":
        install_simple(rec, tool, home / ".config" / "opencode", home / ".config" / "opencode" / "AGENTS.md",
                       home / ".config" / "opencode" / "skills", active_profile("claude", args.profile)
                       if args.profile in (None, "claude-max", "claude-pro", "api", "free") else "api")
    elif tool == "cursor":
        if any(h.MARKER in p.read_text(encoding="utf-8", errors="replace")
               for p in (home / ".claude" / "agents").glob("*.md")) and not args.force_cursor_agents:
            rec.notes.append("cursor: agents skipped because Cursor also loads ~/.claude/agents, where the "
                             "harness agents are installed (use --force-cursor-agents to install both)")
            write_marked(rec, home / ".cursor" / "rules" / "prompt-orchestrator-harness.mdc",
                         "---\ndescription: prompt-orchestrator harness overlay\nalwaysApply: true\n---\n"
                         f"<!-- {h.MARKER} -->\n" + overlay_text())
        else:
            install_simple(rec, tool, home / ".cursor", home / ".cursor" / "rules" / "prompt-orchestrator-harness.mdc", None)
    elif tool == "copilot":
        install_simple(rec, tool, home / ".copilot", None, None)
        rec.notes.append("copilot: no user-level overlay location is documented; agents only")
    elif tool == "gemini":
        install_simple(rec, tool, home / ".gemini", home / ".gemini" / "GEMINI.md", None)
        rec.notes.append("gemini: subagents need experimental.enableAgents = true in ~/.gemini/settings.json")
    elif tool == "antigravity":
        install_simple(rec, tool, home / ".gemini" / "config", None, None)
    elif tool == "kiro":
        install_simple(rec, tool, home / ".kiro", home / ".kiro" / "steering" / "prompt-orchestrator-harness.md", None)
    elif tool == "openclaw":
        rec.notes.append("openclaw: no subagent mechanism; see docs/30-units/harness for the model block")
    rec.save()
    return rec.notes


# ---------------------------------------------------------------- uninstall and status

def uninstall_tool(tool: str) -> list[str]:
    manifest = load_manifest()
    actions = manifest.get("tools", {}).pop(tool, [])
    notes = []
    for action in reversed(actions):
        path = Path(action["path"])
        kind = action["type"]
        if kind == "file" and path.exists() and h.MARKER in path.read_text(encoding="utf-8", errors="replace"):
            path.unlink()
            notes.append(f"removed {path}")
        elif kind == "block" and path.exists():
            path.write_text(strip_block(path.read_text(encoding="utf-8")), encoding="utf-8")
            notes.append(f"removed harness block from {path}")
        elif kind == "json" and path.exists():
            data = json.loads(path.read_text(encoding="utf-8") or "{}")
            strip_hooks(data)
            if tool == "claude":
                prev = manifest.get("claude_previous", {})
                env = data.get("env", {})
                if prev.get("subagent_model"):
                    env["CLAUDE_CODE_SUBAGENT_MODEL"] = prev["subagent_model"]
                else:
                    env.pop("CLAUDE_CODE_SUBAGENT_MODEL", None)
                if "statusline.py" in str((data.get("statusLine") or {}).get("command", "")):
                    if prev.get("statusline"):
                        data["statusLine"] = prev["statusline"]
                    else:
                        data.pop("statusLine", None)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            notes.append(f"removed harness entries from {path}")
        elif kind == "moved" and action.get("backup") and not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action["backup"], path)
            notes.append(f"restored {path}")
    if tool == "claude":
        manifest.pop("claude_previous", None)
    if not manifest.get("tools"):
        home = Path(manifest.get("harness_home") or data_home())
        if home.is_dir() and (home / "scripts" / "harness_lib.py").exists() and home.resolve() != SRC.resolve():
            shutil.rmtree(home)
            notes.append(f"removed harness home {home}")
    save_manifest(manifest)
    return notes


def status() -> int:
    manifest = load_manifest()
    print(f"harness home: {manifest.get('harness_home', data_home())}")
    for tool, actions in manifest.get("tools", {}).items():
        print(f"{tool}: {len(actions)} recorded change(s)")
    if not manifest.get("tools"):
        print("harness not installed for any tool")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("install")
    p.add_argument("--tool", action="append", choices=TOOLS, required=True)
    p.add_argument("--profile", default=None)
    p.add_argument("--no-hooks", action="store_true")
    p.add_argument("--no-statusline", action="store_true")
    p.add_argument("--no-subagent-model", action="store_true")
    p.add_argument("--no-legacy-move", action="store_true")
    p.add_argument("--no-discover", dest="discover", action="store_false")
    p.add_argument("--force-cursor-agents", action="store_true")
    p = sub.add_parser("uninstall")
    p.add_argument("--tool", action="append", choices=TOOLS)
    sub.add_parser("status")
    args = parser.parse_args(argv)
    if args.cmd == "status":
        return status()
    if args.cmd == "uninstall":
        tools = args.tool or list(load_manifest().get("tools", {}))
        for tool in tools:
            for note in uninstall_tool(tool) or [f"{tool}: nothing recorded"]:
                print(f"  {note}")
        return 0
    for tool in args.tool:
        print(f"==> harness for {tool}")
        for note in install_tool(tool, args):
            print(f"  {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
