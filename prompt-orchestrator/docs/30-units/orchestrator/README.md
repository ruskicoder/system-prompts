---
id: units.orchestrator
type: section
status: draft
owner: unassigned
summary: "Central orchestrator system prompt and the files that load it."
kind: module
sources: [AGENT.md, .kiro/steering/**]
verified: {commit: a587916, date: 2026-10-08}
---

# orchestrator

## Purpose
The Central AI Agent Orchestrator prompt: operating principles, pre-action protocol, power modes, routing, safety engine, and session continuation.

## Responsibilities
- `AGENT.md` is the canonical, hand-edited prompt. It defers communication rules to `skills/communication-tone.md` and build rules to `skills/build-discipline.md`, and routes outside content to `workflows/third-party-vetting.md`.
- `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/orchestrator.mdc` and `.windsurf/rules/orchestrator.md` are generated from it by the [generator](../generator/README.md); never edit them by hand.
- `.kiro/steering/orchestrator-steering.md` is hand-maintained and loads `AGENT.md` into Kiro.

## Code
`AGENT.md`, `.kiro/steering/`
