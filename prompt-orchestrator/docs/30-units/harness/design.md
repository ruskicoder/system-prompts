---
id: units.harness.design
type: design
status: draft
owner: Do Dang Khoa
summary: "Install layout, runtime state, hook contracts and session flow."
---

## Structure
- Source: `harness/` in the repo. Installed home: `~/.local/share/prompt-orchestrator/harness/` (`%LOCALAPPDATA%\prompt-orchestrator\harness\` on Windows) holds `scripts/`, `profiles/`, `agents/`, `skills/`, `critical.toml` and `HARNESS.md`. Hooks run from there.
- User config: `~/.config/prompt-orchestrator/harness.toml` (`[profiles] claude`, `codex`, `plan_source`, `plan_set_at`, `statusline_wrap`). Repo config: `.harness.toml` (`verify`, `verify_timeout`, `profile`, `[critical]`).
- State: quota cache `~/.cache/prompt-orchestrator/quota-<provider>.json`; sessions, Fable run count, install manifest and backups under `~/.local/state/prompt-orchestrator/`. `PO_HARNESS_HOME` relocates all of them (tests use it).
- Profile order: session override, repo `.harness.toml`, user config, fallback (`claude-pro` or `codex-plus`) with a tag asking for `/autosetup`.

## Sequences
1. SessionStart: `mode_hook.py start` reads the cache and profile and prints the tag (Codex: refreshes quota from the app-server first, at most every 5 minutes).
2. Each response: the status line writes `rate_limits` to the cache.
3. UserPromptSubmit: `mode_hook.py prompt` records a Fable command or a session profile, and prints a tag only on change.
4. PreToolUse `Agent|Task`: `fable_gate.py` denies unauthorized frontier spawns and counts allowed ones.
5. Stop and SubagentStop: `verify_gate.py` fingerprints the git tree and runs `verify` when it changed since the last pass.

## States
Mode is computed per call from the cache; nothing persists except `last_mode` per session, so a
stale cache degrades to Normal. Hook scripts exit 0 on internal errors so a broken harness never
blocks work; the only deliberate blocks are the frontier gate and a failed verify.

## Install
`install_harness.py` writes only files that carry the marker `prompt-orchestrator-harness`, skips
existing files without it, backs up `settings.json` and `hooks.json` before editing, and records
every change in the manifest. Uninstall removes marked files and blocks, removes only harness hook
entries, restores the previous `CLAUDE_CODE_SUBAGENT_MODEL` and status line, restores the legacy
Kiro rules file, and removes the harness home when no tool remains.
