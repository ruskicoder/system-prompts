---
id: units.catalog
type: section
status: draft
owner: unassigned
summary: "Canonical skills and workflows."
kind: module
sources: [skills/*.md, workflows/*.md]
verified: {commit: 23b1f70, date: 2026-10-07}
---

# catalog

## Purpose
The single source of every skill (`skills/*.md`) and workflow (`workflows/*.md`) that the generator distributes to each supported agent.

## Responsibilities
- One markdown file per entry, with frontmatter `name`, `description` (at most 1024 characters), optional `argument-hint` and `license`, a `# ` title and at least one `## ` section.
- Optional companion files (scripts, templates) live in a sibling folder named after the skill, for example `skills/docs-scaffold/`; the generator copies them next to each generated `SKILL.md`.
- Entries are listed in `INTEGRATIONS.md` and `tools/registry.json` (both generated).
- A skill may instead embed its tooling in the markdown body. `skills/human.md` carries a standard-library Python tool as one fenced ` ````python ` block, which the agent extracts to a scratch path at run time, so the skill needs no companion folder.

## Code
`skills/*.md`, `workflows/*.md`

## Entries with embedded tooling

| Entry | Tooling | Verification |
|---|---|---|
| `skills/docs-scaffold.md` | Companion folder `skills/docs-scaffold/scripts/` (CLI and self-tests) | `python3 -B -m unittest discover -s skills/docs-scaffold/scripts -v` |
| `skills/human.md` | Embedded `human_tool.py`: phrase, structure and silhouette scanners, preservation validator, readability, co-writer suggestion gates, transcript harvest, voice profile, card and scoring, calibration game, refine and structure-repair loops | Extract with the `awk` command in the skill's setup section, then `python3 /tmp/human_tool.py --help` |

