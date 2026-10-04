---
id: units.installers.tests
type: test
status: draft
owner: unassigned
summary: "Installer test coverage."
---

# Tests

## Unit
`python3 -B -m unittest discover -s install -p 'test_*.py' -v` covers fresh install, update with backup and rollback, invalid and altered packages (including companion files), failed staging and publish, and the Bash and PowerShell entrypoints (PowerShell is skipped when unavailable).

## Integration
Not automated.

## System
Not automated.
