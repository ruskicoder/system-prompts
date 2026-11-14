---
description: 'Remote Code Execution testing checklist: OS command injection, SSTI-to-RCE,
  deserialization RCE, file upload RCE, XXE with SSRF to RCE, RCE via dependency confusion,
  and CVE-based RCE patterns. Use...'
---

This is the `offensive-rce` skill from the prompt-orchestrator framework (canonical source: `skills/offensive-rce.md`, also available at `.agents/skills/offensive-rce/SKILL.md`).

1. Load and follow the full instructions in that file exactly.
2. Treat everything after this line as the argument/context for the skill, if anything was provided:

// turbo
{{ user input }}
