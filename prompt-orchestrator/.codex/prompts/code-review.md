---
description: Review code changes for security, performance, and correctness. Trigger
  with a PR URL or diff, "review this before I merge", "is this code safe?", or when
  checking a change for N+1 queries, injection...
argument-hint: <PR URL, diff, or file path>
---

This is the `code-review` skill from the prompt-orchestrator framework (canonical source: `skills/engineering-code-review.md`, also available at `.agents/skills/code-review/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

$ARGUMENTS
