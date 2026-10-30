---
id: decisions.harness-toml-config
type: adr
status: approved
owner: Do Dang Khoa
summary: "Harness config and profiles use TOML read with the standard library; harness scripts need Python 3.11+; the plan is set by /autosetup, never detected by hooks."
superseded_by: none
---

# Decision

## Context
Hooks run on users' machines on every prompt, so they must not need third-party packages. The plan
(Max, Pro, Plus) changes over time and no local file names it.

## Decision
- Config files are TOML (`harness.toml`, `.harness.toml`, `profiles/*.toml`) read with `tomllib`,
  so harness scripts need Python 3.11 or later and nothing else.
- Hooks never detect the plan. `/autosetup` reads it from the Claude desktop usage tool or the Codex
  app-server when available, otherwise asks the user, and writes it to the user config. A prompt
  containing `harness profile: <name>` switches the profile for one session.
- No undocumented quota endpoints are called.

## Alternatives
- YAML: rejected, needs PyYAML at runtime.
- Detecting the plan in hooks: rejected, nothing on disk names the plan.

## Consequences
- Without Python 3.11, the native installers install agents and the overlay only.
- An unset profile falls back to `claude-pro` or `codex-plus`, and the tag asks for `/autosetup`.
