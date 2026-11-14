---
description: Cloud security attack methodology covering AWS, Azure, and GCP. Includes
  credential harvesting (IMDS, ~/.aws, env vars, leaked CI secrets, instance roles),
  enumeration with cloud-specific tools (pacu...
---

This is the `offensive-cloud` skill from the prompt-orchestrator framework (canonical source: `skills/offensive-cloud.md`, also available at `.agents/skills/offensive-cloud/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
