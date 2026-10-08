---
name: tech-debt
description: Identify, categorize, and prioritize technical debt. Trigger with "tech
  debt", "technical debt audit", "what should we refactor", "code health", or when
  the user asks about code quality, refactoring priorities, or maintenance backlog.
license: Apache-2.0 (Anthropic, PBC; engineering plugin v1.2.0). Complete terms in
  LICENSE.txt
---

<!-- Generated from skills/engineering-tech-debt.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Tech Debt Management

Systematically identify, categorize, and prioritize technical debt.

## Categories

| Type | Examples | Risk |
|------|----------|------|
| **Code debt** | Duplicated logic, poor abstractions, magic numbers | Bugs, slow development |
| **Architecture debt** | Monolith that should be split, wrong data store | Scaling limits |
| **Test debt** | Low coverage, flaky tests, missing integration tests | Regressions ship |
| **Dependency debt** | Outdated libraries, unmaintained dependencies | Security vulns |
| **Documentation debt** | Missing runbooks, outdated READMEs, tribal knowledge | Onboarding pain |
| **Infrastructure debt** | Manual deploys, no monitoring, no IaC | Incidents, slow recovery |

## Prioritization Framework

Score each item on:
- **Impact**: How much does it slow the team down? (1-5)
- **Risk**: What happens if we don't fix it? (1-5)
- **Effort**: How hard is the fix? (1-5, inverted; lower effort = higher priority)

Priority = (Impact + Risk) x (6 - Effort)

## Output

Produce a prioritized list with estimated effort, business justification for each item, and a phased remediation plan that can be done alongside feature work.

---
_Modified from the Apache-2.0 `tech-debt` skill by Anthropic, PBC (engineering plugin v1.2.0): punctuation edits, vetting front matter. See LICENSE.txt._
