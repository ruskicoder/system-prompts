#!/usr/bin/env python3
"""Install procable (the offline design skill) user-wide for every supported tool.

    python3 install/install_procable.py install [--tools claude,codex] [--bundle DIR] [--dry-run]
    python3 install/install_procable.py status
    python3 install/install_procable.py uninstall

procable runs fully offline once installed. This installer is the only part that may reach
the network: it downloads the release pinned in install/procable.lock.json (the skill bundle,
SHA256SUMS and the engine for this platform) once, checks every file against SHA256SUMS and
SHA256SUMS against the digest pinned in the lock file, then installs from the local copy.
`--bundle DIR` installs from a directory that already holds those files (air-gapped machines).

Standard library only. Works on Linux, macOS and Windows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = Path(__file__).resolve().parent / "procable.lock.json"
SKILL = "procable"
HOME = Path.home()
STATE = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local" / "share")) / "prompt-orchestrator" / "procable"
MANIFEST = STATE / "manifest.json"

# prompt-orchestrator tool id -> procable provider id. Tools procable does not support are absent.
PROVIDERS = {
    "claude": "claude",
    "codex": "codex",
    "cursor": "cursor",
    "gemini": "gemini",
    "opencode": "opencode",
    "antigravity": "antigravity",
    "copilot": "github",
    "kiro": "kiro",
}
DEFAULT_TOOLS = ["claude", "codex", "cursor", "gemini", "opencode", "antigravity"]


def skill_roots() -> list[Path]:
    """User-level folders where procable's installer puts the skill, per provider."""
    opencode = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "opencode"
    return [HOME / ".claude" / "skills", HOME / ".agents" / "skills", HOME / ".cursor" / "skills",
            HOME / ".gemini" / "skills", HOME / ".gemini" / "config" / "skills", opencode / "skills",
            HOME / ".github" / "skills", HOME / ".kiro" / "skills"]


def platform_tag() -> tuple[str, str]:
    system = {"Darwin": "darwin", "Linux": "linux", "Windows": "windows"}.get(platform.system(), "")
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64" if machine in ("x86_64", "amd64") else ""
    if not system or not arch:
        sys.exit(f"procable: unsupported platform {platform.system()} {platform.machine()}")
    if system == "windows" and arch == "arm64":
        arch = "x64"  # Windows on ARM runs the x64 engine
    return system, arch


def engine_asset(os_name: str, arch: str) -> str:
    return f"{SKILL}-{os_name}-{arch}" + (".exe" if os_name == "windows" else "")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_lock() -> dict:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    for key in ("version", "repo", "sha256sums"):
        if not lock.get(key):
            sys.exit(f"procable: {LOCK.name} has no {key}; the release is not pinned yet")
    return lock


def fetch(url: str, dest: Path, dry: bool) -> None:
    print(f"  get {url}")
    if dry:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as resp, tmp.open("wb") as out:
        shutil.copyfileobj(resp, out)
    tmp.replace(dest)


def stage_release(args, lock: dict, asset: str) -> Path:
    """A directory holding SHA256SUMS, universal.zip and the engine, all verified."""
    if args.bundle:
        src = Path(args.bundle).expanduser().resolve()
    else:
        src = STATE / lock["version"]
        src.mkdir(parents=True, exist_ok=True)
        base = f"https://github.com/{lock['repo']}/releases/download/procable-v{lock['version']}"
        for name in ("SHA256SUMS", "universal.zip", asset):
            if not (src / name).exists():
                fetch(f"{base}/{name}", src / name, args.dry_run)
    if args.dry_run:
        return src
    sums_path = src / "SHA256SUMS"
    if sha256(sums_path) != lock["sha256sums"]:
        sys.exit(f"procable: {sums_path} does not match the digest pinned in {LOCK.name}; refusing to install")
    sums = {}
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1].lstrip("*")] = parts[0].lower()
    for name in ("universal.zip", asset):
        if name not in sums:
            sys.exit(f"procable: SHA256SUMS lists no {name}")
        if sha256(src / name) != sums[name]:
            sys.exit(f"procable: {src / name} fails its checksum; refusing to install")
    return src


def install(args) -> int:
    lock = load_lock()
    os_name, arch = platform_tag()
    asset = engine_asset(os_name, arch)
    tools = [t for t in (args.tools.split(",") if args.tools else DEFAULT_TOOLS) if t]
    unknown = [t for t in tools if t not in PROVIDERS]
    if unknown:
        print(f"procable: skipping tools procable does not support: {', '.join(unknown)}")
    providers = sorted({PROVIDERS[t] for t in tools if t in PROVIDERS})
    print(f"=== procable {lock['version']} for {', '.join(providers)} ({os_name}-{arch})")
    src = stage_release(args, lock, asset)
    engine = src / asset
    if not args.dry_run and os_name != "windows":
        engine.chmod(engine.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    before = {p for root in skill_roots() for p in [root / SKILL] if p.exists()}
    cmd = [str(engine), "install", "--global", "--yes", f"--providers={','.join(providers)}"]
    if args.no_hooks:
        cmd.append("--no-hooks")
    env = dict(os.environ, PROCABLE_BUNDLE_PATH=str(src / "universal.zip"))
    print("  $ " + " ".join(cmd))
    if args.dry_run:
        return 0
    rc = subprocess.call(cmd, env=env)
    if rc != 0:
        print(f"procable: the engine's installer exited {rc}")
        return rc
    installed = [root / SKILL for root in skill_roots() if (root / SKILL / "SKILL.md").exists()]
    if not installed:
        print("procable: install reported success but no skill folder was found")
        return 1
    bin_name = SKILL + (".exe" if os_name == "windows" else "")
    for skill_dir in installed:
        dest = skill_dir / "scripts" / "bin" / f"{os_name}-{arch}" / bin_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(engine, dest)
        if os_name != "windows":
            dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"  engine -> {dest}")
    STATE.mkdir(parents=True, exist_ok=True)
    previous = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    created = sorted({str(p) for p in installed if p not in before} | set(previous.get("created", [])))
    MANIFEST.write_text(json.dumps({"version": lock["version"], "providers": providers,
                                    "skill_dirs": [str(p) for p in installed], "created": created},
                                   indent=2) + "\n", encoding="utf-8")
    print(f"==> procable {lock['version']} installed in {len(installed)} skill folders; it runs offline.")
    return 0


def hook_files() -> list[Path]:
    return [HOME / ".claude" / "settings.json", HOME / ".codex" / "hooks.json"]


def strip_procable_hooks(path: Path) -> int:
    """Remove hook entries whose command runs procable. Returns how many were removed."""
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return 0
    removed = 0
    for event, groups in list(hooks.items()):
        kept_groups = []
        for group in groups if isinstance(groups, list) else []:
            entries = group.get("hooks", []) if isinstance(group, dict) else []
            kept = [h for h in entries if f"{SKILL}/scripts/{SKILL}" not in str(h.get("command", "")).replace("\\", "/")]
            removed += len(entries) - len(kept)
            if kept:
                kept_groups.append(dict(group, hooks=kept))
        if kept_groups:
            hooks[event] = kept_groups
        else:
            del hooks[event]
    if removed:
        backup = path.with_suffix(path.suffix + ".procable-backup")
        shutil.copy2(path, backup)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return removed


def uninstall(args) -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    dirs = [Path(p) for p in manifest.get("skill_dirs", [])] or [r / SKILL for r in skill_roots() if (r / SKILL).exists()]
    for d in dirs:
        print(f"  remove {d}")
        if not args.dry_run and d.exists():
            shutil.rmtree(d)
    for f in hook_files():
        n = 0 if args.dry_run else strip_procable_hooks(f)
        if n:
            print(f"  removed {n} procable hook entries from {f} (backup next to it)")
    if not args.dry_run and MANIFEST.exists():
        MANIFEST.unlink()
    print("==> procable uninstalled")
    return 0


def status(_args) -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    print(f"pinned: {json.loads(LOCK.read_text(encoding='utf-8')).get('version') or 'none'}")
    print(f"installed: {manifest.get('version', 'none')}")
    os_name, arch = platform_tag()
    for root in skill_roots():
        d = root / SKILL
        if d.exists():
            engine = d / "scripts" / "bin" / f"{os_name}-{arch}" / (SKILL + (".exe" if os_name == "windows" else ""))
            print(f"  {d}  engine: {'yes' if engine.exists() else 'MISSING'}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("action", choices=["install", "uninstall", "status"])
    p.add_argument("--tools", default=None, help="comma-separated prompt-orchestrator tool ids")
    p.add_argument("--bundle", default=None, help="directory holding SHA256SUMS, universal.zip and the engine")
    p.add_argument("--no-hooks", action="store_true", help="install the skill without its hooks")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    return {"install": install, "uninstall": uninstall, "status": status}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
