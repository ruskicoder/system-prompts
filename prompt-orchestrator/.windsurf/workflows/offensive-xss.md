---
description: 'Cross-Site Scripting testing checklist: stored/reflected/DOM/blind XSS
  discovery, polyglot payloads, CSP bypass, XSS filter bypass, event handler injection,
  DOM clobbering, mutation XSS, and impact...'
---

This is the `offensive-xss` skill from the prompt-orchestrator framework (canonical source: `skills/offensive-xss.md`, also available at `.agents/skills/offensive-xss/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
