---
description: 'XML External Entity injection testing checklist: classic XXE, blind
  XXE (out-of-band), XXE via file upload (SVG/docx), XXE in SOAP/REST, error-based
  XXE, XInclude attacks, and XXE filter bypass. Use...'
---

This is the `offensive-xxe` skill from the prompt-orchestrator framework (canonical source: `skills/offensive-xxe.md`, also available at `.agents/skills/offensive-xxe/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
