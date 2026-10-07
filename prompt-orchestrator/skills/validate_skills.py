#!/usr/bin/env python3
"""
Contract Validator for prompt-orchestrator skills and workflows.
Validates YAML frontmatter (name, description, optional argument-hint/license),
title headers, and operational sections across all markdown files in skills/ and workflows/.

Also validates the *generated* multi-agent integration output (see
tools/generate_integrations.py) so a stale or hand-edited copy under
.agents/skills/, .claude/skills/, or .opencode/skills/ is caught in CI:
the directory name must match the SKILL.md `name` field, the name must be
lowercase-hyphenated, and the description must be <= 1024 chars, per the
open Agent Skills specification (https://agentskills.io).

Third-party vetting fields (optional, canonical sources only):
origin: in-house | third-party (absent means in-house), vetting: pending | passed |
rejected, vetted: YYYY-MM-DD. third-party needs vetting; passed needs a valid vetted date
not in the future; rejected and unknown values fail; pending prints a warning only.

Run with no arguments to validate everything, or pass explicit paths.
Pass --skip-generated to validate only skills/ and workflows/.
Pass --vetting-report [--format md|json] [--out PATH] to also export the vetting status of
every skill and workflow. Export is opt-in; a default run exports nothing.
"""

import argparse
import datetime
import json
import re
import importlib.util
import sys
import yaml
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
GENERATED_SKILL_DIRS = [".agents/skills", ".claude/skills", ".opencode/skills"]
ORIGINS = {"in-house", "third-party"}
VETTING = {"pending", "passed", "rejected"}
WARNINGS = []


def check_vetting(data: dict, name: str) -> list:
    """Validate origin/vetting/vetted fields. Returns errors; appends warnings to WARNINGS."""
    errors = []
    origin = data.get("origin", "in-house")
    vetting = data.get("vetting")
    vetted = data.get("vetted")
    if origin not in ORIGINS:
        errors.append(f"'origin' must be one of {sorted(ORIGINS)}, got {origin!r}")
    if vetting is not None and vetting not in VETTING:
        errors.append(f"'vetting' must be one of {sorted(VETTING)}, got {vetting!r}")
    if origin == "third-party" and vetting is None:
        errors.append("origin 'third-party' requires a 'vetting' field")
    if vetting == "rejected":
        errors.append("vetting 'rejected': remove the file or re-author it in-house")
    if vetting == "pending":
        WARNINGS.append(f"{name}: vetting pending (run workflows/third-party-vetting.md)")
    if vetting == "passed" or vetted is not None:
        if vetted is None:
            errors.append("vetting 'passed' requires a 'vetted: YYYY-MM-DD' date")
        else:
            try:
                day = vetted if isinstance(vetted, datetime.date) else datetime.date.fromisoformat(str(vetted))
                if day > datetime.date.today():
                    errors.append(f"'vetted' date {day} is in the future")
            except ValueError:
                errors.append(f"'vetted' must be YYYY-MM-DD, got {vetted!r}")
    return errors


def read_frontmatter(filepath: Path) -> dict:
    lines = filepath.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), -1)
    if end == -1:
        return {}
    try:
        data = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def vetting_report(root_dir: Path, fmt: str, out=None) -> None:
    rows = []
    for sub in ("skills", "workflows"):
        for f in sorted((root_dir / sub).glob("*.md")):
            data = read_frontmatter(f)
            rows.append({
                "file": f"{sub}/{f.name}",
                "origin": data.get("origin", "in-house"),
                "vetting": data.get("vetting") or "",
                "vetted": str(data.get("vetted") or ""),
            })
    if fmt == "json":
        text = json.dumps(rows, indent=2) + "\n"
    else:
        text = "| File | Origin | Vetting | Vetted |\n|------|--------|---------|--------|\n"
        text += "".join(f"| {r['file']} | {r['origin']} | {r['vetting']} | {r['vetted']} |\n" for r in rows)
    if out:
        Path(out).write_text(text, encoding="utf-8")
        print(f"Vetting report written to {out}")
    else:
        print(text, end="")

def validate_markdown_file(filepath: Path) -> list:
    errors = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Failed to read file: {e}"]

    if not content.strip():
        return ["File is empty"]

    lines = content.splitlines()

    # 1. Frontmatter check
    if not content.startswith("---"):
        errors.append("Missing opening frontmatter delimiter '---'")
        return errors

    # Find closing frontmatter delimiter
    closing_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_idx = i
            break

    if closing_idx == -1:
        errors.append("Missing closing frontmatter delimiter '---'")
        return errors

    frontmatter_raw = "\n".join(lines[1:closing_idx])
    try:
        data = yaml.safe_load(frontmatter_raw)
        if not isinstance(data, dict):
            errors.append("Frontmatter is not a valid YAML dictionary mapping")
            return errors
    except yaml.YAMLError as ye:
        errors.append(f"Invalid YAML frontmatter: {ye}")
        return errors

    # Validate required fields
    if "name" not in data or not str(data["name"]).strip():
        errors.append("Frontmatter missing required 'name' field")

    if "description" not in data or not str(data["description"]).strip():
        errors.append("Frontmatter missing required 'description' field")

    # Optional fields check if present
    if "argument-hint" in data and data["argument-hint"] is not None and not isinstance(data["argument-hint"], str):
        errors.append("Frontmatter 'argument-hint' must be a string")

    errors.extend(check_vetting(data, filepath.name))

    # 2. Markdown Body Check
    body_lines = lines[closing_idx + 1:]
    # Strip empty lines from start of body
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    if not body_lines:
        errors.append("Missing content body after frontmatter")
        return errors

    # Check for primary title header (# ...)
    has_primary_title = False
    for line in body_lines[:10]:  # Primary title should appear near the top of the body
        if line.startswith("# "):
            has_primary_title = True
            break

    if not has_primary_title:
        errors.append("Missing primary title header '# ...' in markdown body")

    # Check for operational sections (## ...)
    has_operational_section = any(
        line.startswith("## ")
        for line in body_lines
    )

    if not has_operational_section:
        errors.append("Missing operational section header (## ...)")

    return errors


def validate_agent_skill_dir(skill_dir: Path) -> list:
    """Validate a generated Agent-Skills-standard folder (dir/SKILL.md)."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{skill_dir.name}/: missing SKILL.md"]

    errors = validate_markdown_file(skill_md)

    content = skill_md.read_text(encoding="utf-8")
    lines = content.splitlines()
    closing_idx = next(
        (i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        -1,
    )
    if closing_idx != -1:
        try:
            data = yaml.safe_load("\n".join(lines[1:closing_idx])) or {}
        except yaml.YAMLError:
            data = {}

        name = str(data.get("name", "")).strip()
        if name and name != skill_dir.name:
            errors.append(
                f"SKILL.md name '{name}' does not match directory name "
                f"'{skill_dir.name}' (required by the Agent Skills spec)"
            )
        if name and not NAME_RE.match(name):
            errors.append(
                f"name '{name}' must be lowercase alphanumeric with hyphens only"
            )
        description = str(data.get("description", "")).strip()
        if len(description) > 1024:
            errors.append(
                f"description is {len(description)} chars; spec caps this at 1024"
            )

    return errors


def validate_generated_dir(base_dir: Path) -> tuple[int, int]:
    skill_dirs = sorted(p for p in base_dir.glob("*") if p.is_dir())
    if not skill_dirs:
        print(f"No skill folders found in {base_dir}")
        return 0, 0

    passed = 0
    failed = 0
    print(f"\n==> Validating {len(skill_dirs)} generated skill folders in {base_dir}...")
    for skill_dir in skill_dirs:
        errs = validate_agent_skill_dir(skill_dir)
        if errs:
            failed += 1
            print(f"❌ [FAIL] {skill_dir.name}/")
            for err in errs:
                print(f"   - {err}")
        else:
            passed += 1
            print(f"✅ [PASS] {skill_dir.name}/")
    return passed, failed


def validate_directory(dir_path: Path) -> tuple[int, int]:
    md_files = sorted(dir_path.glob("*.md"))
    if not md_files:
        print(f"No markdown files found in {dir_path}")
        return 0, 0

    passed = 0
    failed = 0

    print(f"\n==> Validating {len(md_files)} files in {dir_path}...")
    for file in md_files:
        errs = validate_markdown_file(file)
        if errs:
            failed += 1
            print(f"❌ [FAIL] {file.name}")
            for err in errs:
                print(f"   - {err}")
        else:
            passed += 1
            print(f"✅ [PASS] {file.name}")

    return passed, failed

def main():
    root_dir = Path(__file__).resolve().parent.parent
    skills_dir = root_dir / "skills"
    workflows_dir = root_dir / "workflows"

    total_passed = 0
    total_failed = 0

    parser = argparse.ArgumentParser(description="Validate skills and workflows.")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--skip-generated", action="store_true")
    parser.add_argument("--vetting-report", action="store_true")
    parser.add_argument("--format", choices=["md", "json"], default="md")
    parser.add_argument("--out")
    args = parser.parse_args()
    positional_args = args.paths

    if args.vetting_report:
        vetting_report(root_dir, args.format, args.out)

    if positional_args:
        # Custom paths provided
        for arg in positional_args:
            target = Path(arg)
            if target.is_dir():
                p, f = validate_directory(target)
                total_passed += p
                total_failed += f
            elif target.is_file():
                errs = validate_markdown_file(target)
                if errs:
                    total_failed += 1
                    print(f"❌ [FAIL] {target.name}")
                    for err in errs:
                        print(f"   - {err}")
                else:
                    total_passed += 1
                    print(f"✅ [PASS] {target.name}")
    else:
        skip_generated = args.skip_generated

        # Default: validate both skills and workflows directories
        if skills_dir.exists():
            p, f = validate_directory(skills_dir)
            total_passed += p
            total_failed += f
        if workflows_dir.exists():
            p, f = validate_directory(workflows_dir)
            total_passed += p
            total_failed += f

        if not skip_generated:
            helper_path = root_dir / "install/antigravity_plugin.py"
            spec = importlib.util.spec_from_file_location("antigravity_plugin", helper_path)
            helper = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(helper)
            try:
                helper.validate_package(root_dir / helper.PACKAGE_PATH, root_dir)
                p, f = validate_generated_dir(root_dir / helper.PACKAGE_PATH / "skills")
                total_passed += p + 1
                total_failed += f
            except (OSError, ValueError, KeyError, TypeError) as error:
                print(f"[FAIL] Antigravity plugin: {error}")
                total_failed += 1
            for rel in GENERATED_SKILL_DIRS:
                generated_dir = root_dir / rel
                if generated_dir.exists():
                    p, f = validate_generated_dir(generated_dir)
                    total_passed += p
                    total_failed += f

    if WARNINGS:
        print(f"\nWarnings ({len(WARNINGS)}):")
        for warning in WARNINGS:
            print(f"   - {warning}")

    print(f"\n==================================================")
    print(f"Overall Results: {total_passed} passed, {total_failed} failed out of {total_passed + total_failed} total.")
    print(f"==================================================")

    if total_failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
