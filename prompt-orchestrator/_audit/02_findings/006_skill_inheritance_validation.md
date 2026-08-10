# Finding 006 — Skill Inheritance & Skill Validation (`AGENT.md` Section L vs `SKILL_INHERITANCE.md` & `validate_skill.py`)

## Status
matched

## Folder1 Content Summary
Section L of [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) details Skill Composer rules (Compose, Deduplicate, Pass Scoped Context). [skills/](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/skills) contains 14 markdown skill files.

## Folder2 Content Summary
`Reference/SKILL_INHERITANCE.md` specifies skill composition rules with base OS inheritance (`base_os: "first-principle-codex-os"`). `tools/validate_skill.py` provides an automated Python script to validate skill frontmatter structure, required fields, and section headers.

## Comparison
- **Pros of folder1**: 14 modular, production-ready skill prompts for diverse tasks.
- **Cons of folder1**: Lacks an automated validator script to lint markdown skill files for syntax or structural completeness.
- **Pros of folder2**: Automated Python skill validator script (`tools/validate_skill.py`) ensuring YAML frontmatter integrity.
- **Cons of folder2**: Skill inheritance contract is tied to FPCOS specific YAML schema.

## Web Verification
- **Question checked**: Best practice for validating markdown prompt skills in agent repos.
- **Result**: Including automated linting/validation scripts for skill markdown files prevents syntax errors and missing frontmatter.
- **Source**: AI Skill Catalog Maintenance Guidelines (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**: 
1. Create `skills/validate_skills.py` in folder1 to automatically validate YAML frontmatter and required sections of all 14 skill files.
2. Add **Skill Inheritance & Overrides** rule to `AGENT.md` Section L.

**Confidence**: high
**Status of implementation**: applied
