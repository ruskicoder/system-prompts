---
description: Pre-deployment verification checklist. Use when about to ship a release,
  deploying a change with database migrations or feature flags, verifying CI status
  and approvals before going to production, or...
---

This is the `deploy-checklist` skill from the prompt-orchestrator framework (canonical source: `skills/engineering-deploy-checklist.md`, also available at `.agents/skills/deploy-checklist/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
