---
description: Periodic background system health check, task integrity audit, artifact
  review, and security scan workflow. Generates daily digest summaries and returns
  HEARTBEAT_OK when state is unchanged.
---

This is the `heartbeat-monitoring` workflow from the prompt-orchestrator framework (canonical source: `workflows/heartbeat-monitoring.md`, also available at `.agents/skills/heartbeat-monitoring/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the workflow, if anything was provided:

// turbo
{{ user input }}
