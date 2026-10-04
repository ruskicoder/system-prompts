---
id: units.docs-scaffold.design
type: design
status: draft
owner: unassigned
summary: "CLI structure, staleness, locks, and journal chain."
traces: []
---

# Design

## Structure
One standard-library module. `Project` loads `90-meta/manifest.json` (type, docs_root, changes_dir, ignore_dir, repos, section_size, unit_kinds). Live documents are the markdown files under the docs root top-level files and numbered folders, excluding the changes dir.

## Staleness
A section README lists `sources` (git pathspec globs, `repo:path` in standalone mode) and `verified` (commit per repo, date). A section is stale when `git diff --name-only <commit>` or untracked files match its sources.

## Immutability
`90-meta/locks.json` stores SHA-256 hashes of deprecated files, closed work records and approved decisions (ignoring `superseded_by` lines). `index` adds new locks; `check` reports changed or deleted locked files.

## Session journal
Entries in `<ignore>/sessions/*.md` end with `<!-- chain prev=… hash=… -->`; each hash covers the previous hash and the entry text, across all session files in creation order. `session sync` records the latest hash in `70-work/STATUS.md`, so a truncated journal is detected.

## Frontmatter
Flat `key: value` lines with inline lists and maps; quoted strings use JSON escaping.
