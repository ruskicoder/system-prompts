---
name: code-audit
description: Use for authorized source-code security review and SAST workflows including Semgrep, CodeQL patterns, dangerous API hunting, and fix verification.
---

# Source Code Security Audit

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` or the code audit authorization
2. `NOW`: confirm that you have **source/repository access** (binary without source → switch to an RE skill)
3. `NOW`: state the language stack and scope clearly (directories/services/PR diff)
4. `NEXT`: tool-index; semgrep and similar
5. `ACT`: threat model sketch → automated scan → manual verification

## When to use

- White-box audit, PR/diff security review
- SAST such as Semgrep / CodeQL / Bandit / gosec
- Dangerous APIs, injection points, missing authentication, crypto misuse
- Division of work with `supply-chain-security/`: this skill focuses on **in-house code logic**, supply chain focuses on dependencies and pipelines

## Workflow

### 1. Scope and threat model

```text
□ Trust boundaries: user input, files, deserialization, SSRF, authentication middleware
□ High-value assets: authentication, payments, admin side, key handling
```

### 2. Automated scan

```bash
semgrep --config auto .
# Or the project rule pack
semgrep --config p/owasp-top-ten .
```

### 3. Manual verification (MUST)

```text
□ For every SAST hit: reachable? exploitable? false positive?
□ Authentication: IDOR/privilege bypass, missing checks, wrong multi-tenant isolation
□ Injection: SQL/command/template/LDAP
□ Crypto: hard-coded keys, ECB, custom crypto
```

### 4. Output

```text
Finding: location + data flow + PoC + fix recommendation
Optional ATT&CK / CWE ids
```

## Toolchain

| Tool | Language/scenario |
|------|-----------|
| Semgrep | Fast multi-language rules |
| CodeQL | Deep data flow (GitHub) |
| Bandit | Python |
| gosec / staticcheck | Go |
| SpotBugs / FindSecBugs | Java |

## References

- `references/sast-review-checklist.md`
- `../supply-chain-security/` `../api-security/` `../llm-security/` (agent code)

## Routing context

**Upstream**: MASTER R26  
**Role**: `ops/role-map.md` cae  
**Downstream**: dependency vulnerabilities → supply-chain; runtime verification → pentest-tools

## Task completion self-check

- [ ] Did I verify manually instead of pasting scanner output?
- [ ] Does it include fix recommendations?
- [ ] Did I stay within the authorized repository scope?
- [ ] Checklist?