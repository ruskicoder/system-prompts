---
name: database-security
description: Use for authorized database security assessment covering PostgreSQL/MySQL/MSSQL/Mongo/Redis exposure, authz, UDF/command paths, and misconfiguration review.
---

# Database Security Assessment

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read precedent-pentest; **destructive statements against production databases are forbidden** unless explicitly allowed
2. `NOW`: scope states the instance, account permissions, and whether writes/deletes are allowed
3. `NEXT`: client tool paths
4. `ACT`: exposure surface → authentication → authorization → configuration → exploitation chain verification (safe)

## When to use

- Unauthorized database access/weak passwords/wrong binding to 0.0.0.0
- Excessive permissions, dangerous features (xp_cmdshell, COPY PROGRAM, UDF)
- Lateral movement: from application account to DBA
- NoSQL injection, Redis file writes and similar (authorized environments)

## Workflow

```text
□ Network exposure and TLS
□ Account roles and grantees
□ Access control on sensitive tables
□ Dangerous configuration: file_priv, xp_cmdshell, load_file
□ Whether audit logging is on
□ Backup and snapshot permissions
```

## Toolchain

| Tool | Purpose |
|------|------|
| Official CLI | Connection and enumeration |
| sqlmap | Injection verification (authorized) |
| nuclei | Known exposure templates |
| Cloud RDS console audit | Configuration |

## References

- `references/db-misconfig-checklist.md`
- `../pentest-tools/` `../cloud-k8s/`

## Routing context

**Upstream**: MASTER R35  
**Downstream**: OS command obtained → attack-chain; cloud hosted → cloud-k8s

## Task completion self-check

- [ ] Did I avoid unauthorized writes and deletes?
- [ ] Did I distinguish configuration issues from exploitable chains?
- [ ] Checklist?