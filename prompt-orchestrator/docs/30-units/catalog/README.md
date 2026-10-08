---
id: units.catalog
type: section
status: draft
owner: unassigned
summary: "Canonical skills and workflows."
kind: module
sources: [skills/*.md, workflows/*.md]
verified: {commit: 748f69e, date: 2026-10-08}
---

# catalog

## Purpose
The single source of every skill (`skills/*.md`) and workflow (`workflows/*.md`) that the generator distributes to each supported agent.

## Responsibilities
- One markdown file per entry, with frontmatter `name`, `description` (at most 1024 characters), optional `argument-hint` and `license`, optional vetting fields `origin` (`in-house` or `third-party`), `vetting` (`pending`, `passed` or `rejected`) and `vetted` (date), a `# ` title and at least one `## ` section.
- Optional companion files (scripts, templates) live in a sibling folder named after the skill, for example `skills/docs-scaffold/`; the generator copies them next to each generated `SKILL.md`.
- `skills/communication-tone.md` is the single communication rule (status block, settle scope then execute in one pass, hard stops, report every change, interrupt and resume); `skills/build-discipline.md` holds build and task-type rules; `workflows/third-party-vetting.md` gates outside content.
- Entries are listed in `INTEGRATIONS.md` and `tools/registry.json` (both generated).
- Keep each generated `SKILL.md` at or under 8,000 bytes: Codex truncates a skill's main prompt there (`MAX_SKILL_PROMPT_BYTES` in `codex-rs/ext/skills/src/render.rs`), and M365 Copilot declarative-agent skills cap instructions at 20,000 characters. Put detail in `references/*.md` inside the companion folder and tell the agent when to read each file.

## Code
`skills/*.md`, `workflows/*.md`

## Entries with embedded tooling

| Entry | Tooling | Verification |
|---|---|---|
| `skills/docs-scaffold.md` | Companion folder `skills/docs-scaffold/scripts/` (CLI and self-tests) | `python3 -B -m unittest discover -s skills/docs-scaffold/scripts -v` |
| `skills/human.md` | Companion folder `skills/human/`: `scripts/human_tool.py` dispatcher over the scanner, preservation, suggestion, harvest, voice and loop modules, plus `references/*.md` (contract, catalog, structure, workflows, voice, style, tools) | `python3 -B -m unittest discover -s skills/human/scripts -v` |

