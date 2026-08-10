#!/usr/bin/env python3
"""
Skill Contract Validator for prompt-orchestrator
Validates structural integrity, title headers, and section markers across all markdown skills in skills/.
"""

import sys
from pathlib import Path

def validate_skill(filepath: Path) -> list:
    errors = []
    content = filepath.read_text(encoding="utf-8")

    if not content.strip():
        errors.append("File is empty")
        return errors

    # Check header
    if not content.startswith("# "):
        errors.append("Missing primary title header '# ...'")

    # Check essential section markers (at least one valid operational header)
    lines = content.splitlines()
    has_operational_section = any(
        line.startswith("## ") and any(
            h in line for h in ["Purpose", "When to Use", "Overview", "Usage", "Parameters", "Rules", "Safety Levels", "Workflows", "General Principles"]
        )
        for line in lines
    )
    
    if not has_operational_section:
        errors.append("Missing standard operational section header (## Purpose, ## Overview, ## Rules, etc.)")

    return errors

def main():
    skills_dir = Path(__file__).parent
    skill_files = list(skills_dir.glob("*.md"))

    if not skill_files:
        print("No skill files found to validate.")
        sys.exit(1)

    passed = 0
    failed = 0

    print(f"==> Validating {len(skill_files)} skill files in {skills_dir}...")
    for sf in sorted(skill_files):
        errs = validate_skill(sf)
        if errs:
            failed += 1
            print(f"❌ [FAIL] {sf.name}")
            for err in errs:
                print(f"   - {err}")
        else:
            passed += 1
            print(f"✅ [PASS] {sf.name}")

    print(f"\nResults: {passed} passed, {failed} failed out of {len(skill_files)} total.")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
