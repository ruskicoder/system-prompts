---
description: Continuous autonomous agent execution loop for open-ended, complex, or
  emergent multi-step tasks. Iterates through assessment, single tool execution, observation,
  and state updating until the task...
---

This is the `agent-loop` workflow from the prompt-orchestrator framework (canonical source: `workflows/agent-loop.md`, also available at `.agents/skills/agent-loop/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the workflow, if anything was provided:

// turbo
{{ user input }}
