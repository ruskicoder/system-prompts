---
id: units.harness.tests
type: test
status: draft
owner: Do Dang Khoa
summary: "Harness self-tests and live checks."
---

# Tests

## Unit
`python3 -B -m unittest discover -s harness/tests -v` (20 tests) covers mode bands and boundaries,
stale data, Fable command detection with negation, the status line cache, the mode tag on change
only, the fallback and session profiles, the frontier gate (unauthorized, authorized, Pro without
credits), the verify gate (block, 3-block cap, pass, unchanged tree), rendering for every tool and
profile, Codex effort clamping, Claude install and uninstall round trip on a temporary HOME, Codex
install and uninstall, usage-tool parsing, and installer flags.

## Integration
`skills/validate_skills.py` checks agents (fields, tiers, efforts, description overlap), profiles
and the overlay length. `bash -n` checks every installer script. The native bash installer was run
end to end on a temporary HOME (install and uninstall).

## System
Live on the build machine: Codex app-server quota and model list read, harness installed for Claude
Code and Codex, status line cache, session-start tag, frontier gate block and verify gate block
checked by hand. PowerShell scripts were reviewed by reading only (no PowerShell on the build machine).
