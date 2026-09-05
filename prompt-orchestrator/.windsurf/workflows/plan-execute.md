---
description: Multi-phase plan-then-execute workflow for non-trivial features and refactorings.
  Enforces strict intent gating between read-only planning mode (GitNexus impact analysis,
  multi-axis solution mapping)...
---

This is the `plan-execute` workflow from the prompt-orchestrator framework (canonical source: `workflows/plan-execute.md`, also available at `.agents/skills/plan-execute/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the workflow, if anything was provided:

// turbo
{{ user input }}
