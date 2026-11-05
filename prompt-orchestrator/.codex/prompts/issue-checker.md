---
description: Sweep the open GitHub issues of one or more repositories and leave none
  unanswered or answered-but-open. Reads every thread to its last real comment, checks
  the code and merged PRs on the project's...
argument-hint: '[owner/repo ...] [act|draft]'
---

This is the `issue-checker` skill from the prompt-orchestrator framework (canonical source: `skills/issue-checker.md`, also available at `.agents/skills/issue-checker/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

$ARGUMENTS
