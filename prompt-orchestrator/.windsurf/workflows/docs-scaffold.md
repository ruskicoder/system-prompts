---
description: Scaffold and maintain documentation as a single source of truth (SSOT)
  for humans and AI agents, in embedded (docs inside the code repo, Kiro specs) or
  standalone (separate docs repo) layouts. Detects...
---

This is the `docs-scaffold` skill from the prompt-orchestrator framework (canonical source: `skills/docs-scaffold.md`, also available at `.agents/skills/docs-scaffold/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
