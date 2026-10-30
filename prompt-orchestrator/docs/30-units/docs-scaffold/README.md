---
id: units.docs-scaffold
type: section
status: draft
owner: unassigned
summary: "The docs-scaffold skill and its CLI."
kind: module
sources: [skills/docs-scaffold.md, skills/docs-scaffold/**]
verified: {commit: 6df7f7d, date: 2026-10-26}
---

# docs-scaffold

## Purpose
Scaffold and maintain documentation as a single source of truth for humans and agents, in embedded or standalone layouts. This repository uses it on itself (embedded mode).

## Responsibilities
- `skills/docs-scaffold.md`: agent instructions.
- `skills/docs-scaffold/scripts/docs_scaffold.py`: warn-only CLI (init, check, index, new, verify, deprecate, session including `session archive`), Python 3.8+ standard library only.
- `skills/docs-scaffold/scripts/test_docs_scaffold.py`: self-test.

## Code
`skills/docs-scaffold.md`, `skills/docs-scaffold/`
