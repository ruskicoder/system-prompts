---
id: units.generator.tests
type: test
status: draft
owner: unassigned
summary: "How the generator and its output are checked."
---

# Tests

## Unit
None dedicated.

## Integration
- `python3 -B skills/validate_skills.py` validates canonical and generated skill folders.
- `install/test_antigravity_plugin.py` `test_generator_reproduces_package` checks the generator reproduces the Antigravity package.

## System
Not automated.
