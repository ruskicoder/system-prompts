---
id: units.generator
type: section
status: draft
owner: unassigned
summary: "Build step that turns the catalog into every tool-specific format, plus its validator."
kind: module
sources: [tools/generate_integrations.py, skills/validate_skills.py]
verified: {commit: a587916, date: 2026-10-08}
---

# generator

## Purpose
Keeps every agent integration derived from one canonical source so copies cannot drift.

## Responsibilities
- `tools/generate_integrations.py` deletes and rebuilds the generated folders, then writes `AGENTS.md`, `CLAUDE.md`, the Cursor and Windsurf rules, `.claude-plugin/`, `tools/registry.json` and `INTEGRATIONS.md`.
- `skills/validate_skills.py` validates canonical files and the generated Agent Skills folders. It checks the vetting fields (pending warns, rejected or a bad date fails) and exports a status table with `--vetting-report [--format md|json] [--out PATH]`. The generator does not copy vetting fields into generated output.

## Code
`tools/generate_integrations.py`, `skills/validate_skills.py`
