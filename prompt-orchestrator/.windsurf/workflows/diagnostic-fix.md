---
description: Structured diagnostic-then-fix workflow using GitNexus knowledge graph
  and Ariya-4 problem framing. Gathers symptoms, isolates root causes, formulates
  hypotheses, verifies via reproduction, and...
---

This is the `diagnostic-fix` workflow from the prompt-orchestrator framework (canonical source: `workflows/diagnostic-fix.md`, also available at `.agents/skills/diagnostic-fix/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the workflow, if anything was provided:

// turbo
{{ user input }}
