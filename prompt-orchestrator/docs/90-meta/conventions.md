---
id: meta.conventions
type: conventions
status: approved
owner: unassigned
summary: "Rules for this documentation tree."
---

# Documentation Conventions

## Rules
1. One fact, one home. Link instead of copying.
2. Docs and specs are tracked by version control. The ignore dir holds only temporary, local material: session journals and health reports.
3. `10-context/` to `50-operations/` describe the system as it is now. `60-decisions/` and `70-work/` are history and are locked once approved or closed.
4. Code-derived reference material is generated into `_generated/`, never written by hand.
5. Every live document starts with frontmatter: `id`, `type`, `status`, `owner`, `summary` (one line). Add `traces: [REQ-1]` when a document satisfies requirements.
6. A section is a folder of 2 to 10 related documents whose `README.md` has `type: section`, `sources` (code globs) and `verified` (commit and date). A section is stale when its sources change after the verified commit.
7. Wrong, mistaken, or substantively changed specs are preserved with `deprecate`, never deleted. Minor edits (typography, spelling, formatting, link repair) rely on version control history.
8. Every change to the codebase is appended to the session journal. Journal entries are never edited or deleted.

## Frontmatter syntax
Flat `key: value` lines. Values: plain scalars, quoted strings, inline lists `[a, b]`, inline maps `{k: v}`.

## Types
readme, section, glossary, conventions, overview, requirements, nfr, constraints, architecture, data-model, interface, cross-cutting, design, detail, test, ops, strategy, environment, deploy, configuration, runbook, adr, status, investigation, test-run, review, release, guide.

## Statuses
draft, approved, todo, n/a (requires `na_reason`), closed.

## Naming
- Work records: `YYYY-MM-DD-<slug>.md`; test runs: `YYYY-MM-DD-<unit|integration|system>-r<N>.md`.
- Decisions: `NNNN-<slug>.md`.
- Deprecated material: `.deprecated/YYYY-MM-DD-<slug>/`.
