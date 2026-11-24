---
name: windows-ad
description: Use for authorized Active Directory and Windows identity attacks including Kerberos, AD CS, BloodHound paths, NTLM relay, and domain privilege escalation research.
---

# Windows / Active Directory Security

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md`
2. `NOW`: **domain/AD testing must have a clearly authorized scope** (including DCs, and whether poisoning/relay is allowed)
3. `NOW`: case-init; state the network_profile and forbidden actions clearly
4. `NEXT`: tool-index (impacket/certipy/bloodhound and similar are usually manual)
5. `ACT`: start from identity enumeration and the BloodHound graph; do not lead with destructive exploitation

## When to use

- Domain pentest, Kerberoasting, AS-REP, delegation
- AD CS (ESC1–ESC8 and others) certificate attacks
- BloodHound / SharpHound attack paths
- NTLM Relay / Coercer forced authentication
- Local privilege escalation into domain paths (Potato and similar as stepping stones)

## Relation to attack-chain

- **Multi-phase from the internet to the domain controller** → PRIMARY can stay `attack-chain/`, with this skill as the **AD specialist**
- **Already inside the domain, focused on identity** → PRIMARY = this skill

## Workflow

### 1. Enumeration

```bash
# Example Impacket / built-in (needs credentials and authorization)
nxc smb <range> -u user -p pass
bloodhound-python -d domain.local -u user -p pass -c All -ns <DC>
```

### 2. Common paths (map first, then shoot)

```text
□ Kerberoast / AS-REP → offline cracking
□ ACL abuse (GenericAll/WriteDacl)
□ Delegation (unconstrained/constrained/resource-based)
□ AD CS template errors → Certipy
□ Relay: LLMNR/NBT-NS + ntlmrelayx (confirm authorization)
```

### 3. Credentials and lateral movement

```text
□ secretsdump / lsassy / mimikatz (strict authorization and cleanup)
□ PtH / PtT / golden tickets only within the authorized red team scope
□ Write Evidence for every step; wait for user confirmation on high-risk steps
```

## Toolchain

| Tool | Purpose |
|------|------|
| BloodHound / SharpHound | Path graph |
| Certipy | AD CS |
| Impacket / NetExec | Lateral movement and enumeration |
| Rubeus / Mimikatz | Tickets and credentials (authorized) |
| Coercer / Responder | Forced authentication / poisoning |

## References

- `references/ad-attack-paths.md`
- `../pentest-tools/references/network-attack-defense.md`
- `../attack-chain/`
- seeds: `field-journal/seed-005_ad-certipy-esc1.md` `seed-007_ntlm-relay-coercer.md` `seed-013_kerberoasting-spn.md`

## Routing context

**Upstream**: MASTER R24  
**Downstream**: report `docs-generator`; EDR research needed `edr-bypass-re`  
**MUST NOT**: unauthorized DCSync / golden tickets against production

## Task completion self-check

- [ ] Was there a graph/enumeration before exploitation?
- [ ] Did I record reproducible commands with redaction?
- [ ] Did I respect the scope prohibitions?
- [ ] Checklist?