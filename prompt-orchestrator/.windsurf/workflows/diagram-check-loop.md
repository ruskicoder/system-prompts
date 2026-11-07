---
description: Check a boxes-and-arrows figure before anyone sees it. Runs the architecture-diagrams
  geometry lint to zero findings, renders the figure headless, reads the render whole
  and in full-size crops, checks...
---

This is the `diagram-check-loop` workflow from the prompt-orchestrator framework (canonical source: `workflows/diagram-check-loop.md`, also available at `.agents/skills/diagram-check-loop/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the workflow, if anything was provided:

// turbo
{{ user input }}
