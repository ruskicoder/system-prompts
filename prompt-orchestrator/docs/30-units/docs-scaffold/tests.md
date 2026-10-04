---
id: units.docs-scaffold.tests
type: test
status: draft
owner: unassigned
summary: "Self-test coverage for the CLI."
---

# Tests

## Unit
`python3 -B -m unittest discover -s skills/docs-scaffold/scripts -v` runs 14 tests in temporary git repositories: frontmatter round trip, both scaffold types (including a standalone tree at the repository root), warn-only exit code, staleness and verify, unverifiable standalone repos, gaps, coverage, traces, links, duplicate IDs, generated files, locks, deprecation (move, keep, relink, live links into `.deprecated/`), and journal tamper detection.

## Integration
`python3 -B -m unittest discover -s install -p 'test_*.py' -v` checks that the Antigravity package carries the CLI as a companion file and rejects altered copies.

## System
Not automated.
