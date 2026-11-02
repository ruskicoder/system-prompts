---
id: units.installers
type: section
status: draft
owner: unassigned
summary: "Per-tool installers and the Antigravity plugin installer."
kind: module
sources: [install/**]
verified: {commit: eefac58, date: 2026-10-30}
---

# installers

## Purpose
Copy the generated integrations into a project or into each tool's per-user configuration.

## Responsibilities
- `install/install.py`: interactive menu (standard library) for every global tool, with flags for scripts: `--core`, `--harness-only`, `--yes`, `--tools`, `--profile-claude`, `--profile-codex`, `--no-<global item>`, `--uninstall-harness`, `--no-procable`, `--procable-bundle`, `--uninstall-procable`, `--dry-run`. Core and harness are both selected by default.
- `install-all.sh` and `install-all.ps1` (and `install-all.bat`) run `install.py` when Python exists, otherwise the native menus `install-tui.sh` or `install-tui.ps1`, which install the core and the harness's pre-rendered agents and overlay without hooks.
- `install/install-<tool>.sh` and `.ps1` per tool accept `--with-harness` (`-WithHarness`); `install-harness.sh` and `.ps1` add the harness to an existing core install; `install-project.*` copies everything into one project.
- `install/antigravity_plugin.py` validates that the plugin package mirrors `.agents/skills/` exactly (including companion files), stages it, backs up an existing plugin, and replaces only `prompt-orchestrator`.
- `install/install-claude.sh` and `.ps1` then run the installed `skills/no-ai-trailer/scripts/ensure_attribution_off.py`, which turns AI attribution off in Claude Code, VS Code and Cursor CLI, sets a global git `core.hooksPath` that strips AI trailers and hands over to each repository's own hooks, and registers the Claude Code SessionStart hook and PreToolUse guard.
- `install/install_procable.py` installs procable, the offline design skill, user-wide: it downloads the release pinned in `install/procable.lock.json` once (or uses `--bundle DIR`), checks `SHA256SUMS` against the pinned digest and every file against `SHA256SUMS`, runs the engine's own `install --global` for the selected tools, copies the engine next to each installed skill, adds procable's per-edit and Stop hooks to `~/.codex/hooks.json` for Codex (procable's own installer writes Codex hooks only at project scope), and records a manifest for `uninstall`, which also strips procable's hook entries from `~/.claude/settings.json` and `~/.codex/hooks.json` (backups kept). `install.py` runs it by default; `--no-procable`, `--procable-bundle` and `--uninstall-procable` control it.
- `install/test_antigravity_plugin.py` covers the Antigravity installer.

## Code
`install/`
