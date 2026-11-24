"""Validate the generated Antigravity skill plugin (standard library only).

install/install.sh and install/install.ps1 install the plugin; skills/validate_skills.py and the
tests call validate_package() to check that the package mirrors .agents/skills/ exactly.
"""

import json
import re
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
