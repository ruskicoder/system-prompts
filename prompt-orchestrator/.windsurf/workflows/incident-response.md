---
description: Run an incident response workflow — triage, communicate, and write postmortem.
  Trigger with "we have an incident", "production is down", an alert that needs severity
  assessment, a status update...
---

This is the `incident-response` skill from the prompt-orchestrator framework (canonical source: `skills/engineering-incident-response.md`, also available at `.agents/skills/incident-response/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
