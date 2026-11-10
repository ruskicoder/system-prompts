---
description: Turn the repository's written rules into checks a pull request cannot
  skip. One rule registry (rules.yaml) lists every enforceable rule with its source
  skill, checker, scope and gate or advisory...
---

This is the `ci-enforcement` skill from the prompt-orchestrator framework (canonical source: `skills/ci-enforcement.md`, also available at `.agents/skills/ci-enforcement/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
