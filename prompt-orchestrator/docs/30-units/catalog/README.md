---
id: units.catalog
type: section
status: draft
owner: unassigned
summary: "Canonical skills and workflows."
kind: module
sources: [skills/*.md, workflows/*.md]
verified: {commit: 6e06f92, date: 2026-10-17}
---

# catalog

## Purpose
The single source of every skill (`skills/*.md`) and workflow (`workflows/*.md`) that the generator distributes to each supported agent.

## Responsibilities
- One markdown file per entry, with frontmatter `name`, `description` (at most 1024 characters), optional `argument-hint` and `license`, optional vetting fields `origin` (`in-house` or `third-party`), `vetting` (`pending`, `passed` or `rejected`) and `vetted` (date), a `# ` title and at least one `## ` section.
- Optional companion files (scripts, templates) live in a sibling folder named after the skill, for example `skills/docs-scaffold/`; the generator copies them next to each generated `SKILL.md`.
- `skills/communication-tone.md` is the single communication rule (status block, settle scope then execute in one pass, hard stops, report every change, interrupt and resume); `skills/build-discipline.md` holds build and task-type rules; `workflows/third-party-vetting.md` gates outside content; `skills/brainstorming.md` and `skills/grill-me.md` clarify new work before building (question rounds with options, play-back, proceed gate, review mode).
- Entries are listed in `INTEGRATIONS.md` and `tools/registry.json` (both generated).
- Platform prompt-size caps (an 8,000-byte main-prompt limit in Codex, `MAX_SKILL_PROMPT_BYTES` in `codex-rs/ext/skills/src/render.rs`; 20,000 characters for M365 Copilot declarative-agent skills) are platform limits, not repo rules. Skills keep the content they need; never compact or truncate necessary instructions to fit a cap ([decision 0001](../../60-decisions/0001-platform-prompt-size-caps.md)). `references/*.md` in the companion folder remains an option for optional detail.

## Code
`skills/*.md`, `workflows/*.md`

## Entries with embedded tooling

| Entry | Tooling | Verification |
|---|---|---|
| `skills/docs-scaffold.md` | Companion folder `skills/docs-scaffold/scripts/` (CLI and self-tests) | `python3 -B -m unittest discover -s skills/docs-scaffold/scripts -v` |
| `skills/human.md` | Companion folder `skills/human/`: `scripts/human_tool.py` dispatcher over the scanner, preservation, suggestion, harvest, voice and loop modules, plus `references/*.md` (contract, catalog, structure, workflows, voice, style, tools) | `python3 -B -m unittest discover -s skills/human/scripts -v` |

