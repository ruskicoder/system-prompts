---
name: threat-hunting
description: Use for blue-team threat hunting, detection engineering with Sigma/YARA, SIEM query design, and incident detection validation.
---

# Threat Hunting & Detection Engineering

## ACTION REQUIRED (execute right after reading)

1. `NOW`: confirm the blue team/hunting authorization and the data source scope (SIEM, EDR exports)
2. `NOW`: state a clear hypothesis before querying, to avoid mindlessly churning through alerts
3. `NEXT`: tools and data access methods
4. `ACT`: hypothesis → query → verify → turn into rules

## When to use

- Threat hunting (hypothesis-driven)
- Sigma / YARA detection engineering
- Alert tuning, false positive analysis
- With `malware-analysis/`: sample-side IOCs → this skill turns them into detections
- With `digital-forensics/`: case artifacts → lateral hunting

## Workflow

### 1. Build the hypothesis

```text
Example: an attacker moves laterally with living-off-the-land
→ Data sources: Sysmon 1/3/10, Windows Security 4624/4648
→ Success criterion: find anomalous parent processes or rare account log sources
```

### 2. Query and stack

```text
□ Baseline: normal administrator behavior hours and hosts
□ Anomalies: new services, encoded PowerShell, unusual outbound traffic
□ Correlation: the same account logging in on many hosts in a short time
```

### 3. Turn into rules

```yaml
# Sigma skeleton is in malware-analysis; this skill emphasizes:
# - false positive surface
# - data source field mapping
# - links to response playbooks
```

### 4. Verification

```text
□ Atomic tests (Atomic Red Team) only in an authorized lab
□ Replay historical logs to verify recall
```

## Toolchain

| Tool | Purpose |
|------|------|
| Sigma CLI / sigmac | Rule conversion |
| YARA | Files/memory |
| SIEM (ELK/Splunk and others) | Queries |
| osquery | Endpoint hunting |
| Atomic Red Team | Detection verification (lab) |

## References

- `references/hunting-loop.md`
- `../malware-analysis/references/yara-sigma-rules.md`
- `../digital-forensics/`

## Routing context

**Upstream**: MASTER R27  
**Downstream**: intrusion confirmed → forensics; malicious samples → malware-analysis  
**MUST NOT**: run attack simulations in an unauthorized production environment

## Task completion self-check

- [ ] Is there a clear hypothesis and conclusion?
- [ ] Do the rules state false positives and data sources?
- [ ] Checklist?