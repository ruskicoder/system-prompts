---
name: email-security
description: Use for authorized email security review including phishing analysis, header authentication (SPF/DKIM/DMARC), BEC patterns, and mailbox token abuse research.
---

# Email Security & Phishing Analysis

## ACTION REQUIRED (execute right after reading)

1. `NOW`: confirm authorization (analyzing sample emails / tenant configuration review)
2. `NOW`: do not deliver malicious samples to real users a second time
3. `ACT`: header authentication → content/URLs → attachment sandbox → tenant control plane recommendations

## When to use

- Phishing email teardown and IOCs
- SPF/DKIM/DMARC configuration assessment
- BEC business email compromise patterns
- OAuth app phishing / mailbox token abuse (combine with llm/cloud identity)
- Security awareness exercise design (authorized)

## Workflow

```text
□ Complete original headers: Received chain, From/Return-Path consistency
□ SPF/DKIM/DMARC alignment results
□ URL sandbox and static attachment analysis (combine with malware-analysis)
□ Brand impersonation and reply address mismatch
□ Tenant: anti-phishing policy, external tagging, MFA, OAuth app consent
```

## Toolchain

| Tool | Purpose |
|------|------|
| Mail client "view source" | Headers |
| dig/nslookup | SPF/DMARC records |
| urlscan / sandbox | Links and attachments |
| Tenant admin center | Policies |

## References

- `references/email-auth-checklist.md`
- `../malware-analysis/` `../attack-chain/` (phishing phase) `../windows-ad/` (tokens)

## Routing context

**Upstream**: MASTER R36  
**MUST NOT**: send test phishing in bulk to third-party domains without authorization

## Task completion self-check

- [ ] Is the header authentication conclusion complete?
- [ ] Can the IOCs be turned into detections (combine with threat-hunting)?
- [ ] Checklist?