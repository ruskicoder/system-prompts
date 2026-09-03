#!/usr/bin/env python3
"""
Contract Validator for prompt-orchestrator skills and workflows.
Validates YAML frontmatter (name, description, optional argument-hint/license),
title headers, and operational sections across all markdown files in skills/ and workflows/.
"""

import sys
import yaml
from pathlib import Path

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

    if len(sys.argv) > 1:
        # Custom paths provided
        for arg in sys.argv[1:]:
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
        # Default: validate both skills and workflows directories
        if skills_dir.exists():
            p, f = validate_directory(skills_dir)
            total_passed += p
            total_failed += f
        if workflows_dir.exists():
            p, f = validate_directory(workflows_dir)
            total_passed += p
            total_failed += f

    print(f"\n==================================================")
    print(f"Overall Results: {total_passed} passed, {total_failed} failed out of {total_passed + total_failed} total.")
    print(f"==================================================")

    if total_failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
