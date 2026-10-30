# Implementation Plan

- [x] 1. Harness foundation
- [x] 1.1 Create `harness/` layout, `harness_lib.py` (config and profile loading with `tomllib`, platform paths, quota cache read and write, pace and mode computation, session state) and unit tests for mode boundaries and staleness
  - _Requirements: 1.1, 4.7, 5.3, 5.8, 5.9, 12.2_
- [x] 1.2 Write profiles `claude-max`, `claude-pro`, `codex-plus`, `api`, `free` and `critical.toml`
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 6.4_

- [x] 2. Agents and overlay
- [x] 2.1 Write the 16 canonical agent files with tiers, efforts, access, return contract and non-overlapping descriptions
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 7.4_
- [x] 2.2 Write `HARNESS.md` (precedence, tiers, modes, delegation, Fable protocol, roster, verification, token diet), 160 lines max
  - _Requirements: 1.2, 1.4, 5.4, 5.5, 5.6, 6.1, 6.3, 6.5, 6.6, 6.7, 6.8, 7.1, 7.2, 9.4_
- [x] 2.3 Write the `/autosetup` skill (detection through the usage tool and Codex app-server, user choice fallback, explicit profile argument, config write, mapping report)
  - _Requirements: 4.7, 4.8, 4.9, 4.11, 4.12_

- [x] 3. Claude Code runtime
- [x] 3.1 `statusline.py` (cache, display, wrap) with tests
  - _Requirements: 5.1, 5.2_
- [x] 3.2 `mode_hook.py` (start and prompt; tag on change; Fable command record and quota line; session profile override; `/autosetup` suggestion) with tests
  - _Requirements: 4.7, 4.10, 4.11, 5.7, 5.8, 6.5, 6.6, 6.9_
- [x] 3.3 `fable_gate.py` (block unauthorized frontier spawns, count runs) with tests
  - _Requirements: 6.1, 6.2, 6.9, 6.10_
- [x] 3.4 `verify_gate.py` (changed-files check, run, trim, 3-block cap, timeout; Claude and Codex inputs) with tests
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
- [x] 3.5 Workflows `pr-sweep.js` and `refactor-fanout.js`
  - _Requirements: 9.1, 9.2, 9.3, 9.5_

- [x] 4. Codex runtime
- [x] 4.1 `codex_bridge.py` (app-server rate limits, model discovery checked against the generated schema, fallback mapping) with tests using a fake app-server
  - _Requirements: 4.4, 4.8, 5.10, 5.11_

- [x] 5. Rendering and generator
- [x] 5.1 `render.py` renderers for Claude, Codex, OpenCode, Cursor, Copilot, Gemini, Antigravity and Kiro, fields checked against current docs, marker on every file, golden-file tests
  - _Requirements: 3.6, 11.1, 11.2, 11.3, 11.4_
- [x] 5.2 Wire `tools/generate_integrations.py` to render `harness/dist/<tool>/<profile>/` and include the overlay; extend `skills/validate_skills.py` with agent and profile checks
  - _Requirements: 11.1, 12.1_

- [x] 6. Installers
- [x] 6.1 `install_harness.py` per tool: copy agents with conflict skip, overlay import, settings merge (env, status line, hooks), Codex agents, hooks and AGENTS.md overlay, workflows, legacy Kiro file move, install manifest, uninstall; tests on a temp HOME
  - _Requirements: 1.3, 2.8, 2.9, 7.3, 7.5, 11.5, 11.6, 11.7_
- [x] 6.2 `install/install.py` TUI and flags; launchers `install.sh`, `install-all.sh`, `install.ps1`, `install-all.ps1`, `install-all.bat`; per-tool scripts gain `--core` and `--with-harness`; `install-harness` entry; tests for flag parsing and non-TTY defaults
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.7_
- [x] 6.3 Native fallback TUIs `install-tui.sh` and `install-tui.ps1` copying `harness/dist`; `bash -n` check
  - _Requirements: 2.5, 2.6, 12.4_

- [x] 7. Session journal archive
- [x] 7.1 docs-scaffold `session archive` with digest and history-aware chain verification; tests; update `skills/docs-scaffold.md`
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 8. Documentation
- [x] 8.1 Docs unit `docs/30-units/harness/` (README, design, tests), decision records 0002 and 0003, updates to system flow, installers unit, catalog, INDEX, README, INTEGRATIONS.md, STATUS.md; per-tool gap table
  - _Requirements: 11.6, 12.5_

- [x] 9. Wire, verify and install
- [x] 9.1 Regenerate, run validator, all unit tests, docs check; run the installer on this machine with the harness; live checks (cache, tag, Fable block, verify block and cap); fix and rerun until green
  - _Requirements: 12.3, 12.4, 1.3_
- [x] 9.2 Report every change; ask approval for commit, push and release v1.1.0
  - _Requirements: 12.6_
