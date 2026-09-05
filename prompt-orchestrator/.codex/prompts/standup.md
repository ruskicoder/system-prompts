---
description: Generate a standup update from recent activity. Use when preparing for
  daily standup, summarizing yesterday's commits and PRs and ticket moves, formatting
  work into yesterday/today/blockers, or...
argument-hint: '[yesterday | today | blockers]'
---

This is the `standup` skill from the prompt-orchestrator framework (canonical source: `skills/engineering-standup.md`, also available at `.agents/skills/standup/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

$ARGUMENTS
