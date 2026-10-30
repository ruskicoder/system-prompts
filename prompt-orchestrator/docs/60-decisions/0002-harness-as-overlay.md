---
id: decisions.harness-as-overlay
type: adr
status: approved
owner: Do Dang Khoa
summary: "The harness is an optional overlay that supersedes AGENT.md sections E, F and M while installed; the core text is unchanged."
superseded_by: none
---

# Decision

## Context
The core orchestrator routes work to workflows and power modes but never chooses models, reads no
plan quota, and lists subagent roles with no definitions. The user wanted a model-aware harness
(Claude Max first) that stays optional, so core-only installs keep working.

## Decision
Agreed in the 2026-10-30 grill (Q1 to Q3): the harness lives in `prompt-orchestrator/harness/` and
loads `harness/HARNESS.md` after the core. While installed it supersedes core sections E (Power
Mode), F (Token Budget) and M (Subagent catalog). Installers offer core only, harness only, or both,
through an interactive menu with flags for scripts.

## Alternatives
- Two generated `AGENTS.md` variants: rejected, duplicates the shared text.
- Conditionals inside `AGENT.md`: rejected, couples the layers and makes the harness hard to remove.
- A sibling top-level folder: rejected, would need its own generator and docs.

## Consequences
- Uninstalling the harness restores core behavior exactly.
- Tools that read one instructions file get the overlay as a marked block appended to it.
