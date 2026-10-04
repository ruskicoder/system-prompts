#!/usr/bin/env python3
"""Install the generated Antigravity skill plugin using only Python's stdlib."""

import argparse
import json
import re
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

PLUGIN_NAME = "prompt-orchestrator"
PACKAGE_PATH = Path("integrations/antigravity") / PLUGIN_NAME
ROOT = Path(__file__).resolve().parent.parent


def validate_package(package, root):
    """Require exact registry membership and byte-identical generated skills."""
    manifest = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("name") != PLUGIN_NAME:
        raise ValueError("plugin.json must identify prompt-orchestrator")
    registry = json.loads((root / "tools/registry.json").read_text(encoding="utf-8"))
    names = [entry["id"] for entry in registry]
    if not names or any(
        not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name)
        for name in names
    ) or len(set(names)) != len(names):
        raise ValueError("Invalid or empty skill registry")
    # Each skill folder must mirror its generated .agents/skills/<name>/ folder
    # exactly: SKILL.md plus any companion files (scripts, templates).
    expected = {Path("plugin.json"), Path("skills")}
    references = {}
    for name in names:
        source = root / ".agents/skills" / name
        expected.update({Path("skills") / name, Path("skills") / name / "SKILL.md"})
        for ref in source.rglob("*") if source.is_dir() else []:
            target = Path("skills") / name / ref.relative_to(source)
            expected.add(target)
            if ref.is_file():
                references[target] = ref
    actual = {p.relative_to(package) for p in package.rglob("*")}
    if actual != expected or any(p.is_symlink() for p in package.rglob("*")):
        raise ValueError("Plugin contents do not match the registry (missing, extra, or linked files)")
    for name in names:
        if not (package / "skills" / name / "SKILL.md").is_file():
            raise ValueError(f"Skill differs from generated source: {name}")
    for target, ref in references.items():
        if (package / target).read_bytes() != ref.read_bytes():
            raise ValueError(f"Skill differs from generated source: {target.parts[1]}")
    return len(names)


def install(root, config):
    source = root / PACKAGE_PATH
    count = validate_package(source, root)  # Fail before any destination writes.
    config = config.expanduser().absolute()
    plugins = config / "plugins"
    target = plugins / PLUGIN_NAME
    if target.is_symlink() or (target.exists() and not target.is_dir()):
        raise ValueError(f"Refusing to replace a link or non-directory: {target}")
    if target.resolve() == source.resolve() or source.resolve() in target.resolve().parents:
        raise ValueError("Installation destination must be outside the generated package")

    # Staging and backups stay outside discovery to avoid duplicate plugins.
    config.mkdir(parents=True, exist_ok=True)
    backup = None
    with tempfile.TemporaryDirectory(prefix=".orchestrator-stage-", dir=config) as temporary:
        staged = Path(temporary) / PLUGIN_NAME
        shutil.copytree(source, staged)
        validate_package(staged, root)
        plugins.mkdir(parents=True, exist_ok=True)
        if target.exists():
            backups = config / "plugin-backups"
            backups.mkdir(parents=True, exist_ok=True)
            backup = backups / (PLUGIN_NAME + "-" + uuid.uuid4().hex)
            target.rename(backup)
        try:
            staged.rename(target)
        except OSError:
            if backup is not None:
                backup.rename(target)
            raise
    print(f"Installed {count} skills/workflows: {target}")
    if backup is not None:
        print(f"Previous plugin preserved at: {backup}")
        print("Rollback: close Antigravity, move the installed plugin aside, then move")
        print(f"  {backup}")
        print(f"to {target}")
    print("Open a fresh Antigravity session; check Customizations and browse '/' for skills.")
    print("File installation verified; runtime discovery still needs an Antigravity check.")
    return target, backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config-dir", type=Path, default=Path.home() / ".gemini/config",
                        help="Antigravity config directory (override for isolated tests)")
    args = parser.parse_args()
    try:
        install(ROOT, args.config_dir)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Antigravity installation failed: {error}", file=sys.stderr)
        print("Regenerate/validate the package if incomplete: python3 tools/generate_integrations.py",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
