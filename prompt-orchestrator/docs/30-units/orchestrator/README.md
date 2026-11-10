---
id: units.orchestrator
type: section
status: draft
owner: unassigned
summary: "Central orchestrator system prompt and the files that load it."
kind: module
sources: [AGENT.md, .kiro/steering/**]
verified: {commit: 9e695a7, date: 2026-11-07}
---

# orchestrator

## Purpose
The Central AI Agent Orchestrator prompt: operating principles, pre-action protocol, power modes, routing, safety engine, and session continuation.

## Responsibilities
- `AGENT.md` is the canonical, hand-edited prompt. It defers communication rules to `skills/communication-tone.md`, wording rules to `skills/prose-and-wording.md`, the ban on AI attribution to `skills/no-ai-trailer.md` and build rules to `skills/build-discipline.md`, and routes outside content to `workflows/third-party-vetting.md`. Section K points to the canary line of communication-tone section 1, and five of the eight canary markers sit in it (decision 0005). Section L lists the review and audit skills, including `skills/issue-checker.md`, a Submitted Writing line that sends every graded, submitted or sent document through a genre skill (`skills/academic-writing.md` or `skills/professional-writing.md`), then `skills/concision-and-logic.md` and `skills/human.md`, with `skills/thesis-defense.md` for a defence, a UI Work line that loads `skills/ui-ux-philosophy.md` with `skills/ui-flow-and-layout.md`, and a Diagram Work line for `skills/architecture-diagrams.md` and `workflows/diagram-check-loop.md`.
- `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/orchestrator.mdc` and `.windsurf/rules/orchestrator.md` are generated from it by the [generator](../generator/README.md); never edit them by hand.
- `.kiro/steering/orchestrator-steering.md` is hand-maintained and loads `AGENT.md` into Kiro.

## Code
`AGENT.md`, `.kiro/steering/`
