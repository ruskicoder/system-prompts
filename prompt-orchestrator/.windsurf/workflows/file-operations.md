---
description: Read, write, search, and edit files across the workspace. Enforces the
  READ-BEFORE-WRITE rule, batch file reads, atomic SEARCH/REPLACE blocks, and file
  discovery via grep and glob rather than terminal...
---

This is the `file-operations` skill from the prompt-orchestrator framework (canonical source: `skills/file-operations.md`, also available at `.agents/skills/file-operations/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
