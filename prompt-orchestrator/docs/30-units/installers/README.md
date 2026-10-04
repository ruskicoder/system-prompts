---
id: units.installers
type: section
status: draft
owner: unassigned
summary: "Per-tool installers and the Antigravity plugin installer."
kind: module
sources: [install/**]
verified: {commit: 3a00f10, date: 2026-10-04}
---

# installers

## Purpose
Copy the generated integrations into a project or into each tool's per-user configuration.

## Responsibilities
- `install/install-<tool>.sh` and `.ps1` per tool; `install-all.*` runs the global installers; `install-project.*` copies everything into one project.
- `install/antigravity_plugin.py` validates that the plugin package mirrors `.agents/skills/` exactly (including companion files), stages it, backs up an existing plugin, and replaces only `prompt-orchestrator`.
- `install/test_antigravity_plugin.py` covers the Antigravity installer.

## Code
`install/`
