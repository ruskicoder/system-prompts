---
description: Full lifecycle spec-driven development methodology across three gated
  phases - Requirements (EARS-format acceptance criteria), Design (architecture, data
  models, edge cases), and Tasks (phased...
---

This is the `spec-driven` workflow from the prompt-orchestrator framework (canonical source: `workflows/spec-driven.md`, also available at `.agents/skills/spec-driven/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the workflow, if anything was provided:

// turbo
{{ user input }}
