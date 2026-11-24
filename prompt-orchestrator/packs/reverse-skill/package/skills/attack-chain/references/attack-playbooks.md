# Attack Chain Playbook Quick Reference

> Choose the playbook by target type; each playbook defines the standard path from initial access to reaching the goal.

---

## Playbook 1: internet-facing web application → domain controller

```
1. Subdomain enumeration + port scan
2. Web fingerprinting → find components with known vulnerabilities
3. Exploit to get a webshell / RCE
4. Internal information gathering (ipconfig/ifconfig, arp, net user)
5. Set up a tunnel (frp/chisel/ssh)
6. Internal scan (live hosts, open ports)
7. Credential acquisition (mimikatz/hashdump/configuration files)
8. Lateral movement (PTH/WMI/PsExec)
9. Domain information gathering (BloodHound)
10. Domain privilege escalation (Kerberoasting/DCSync/constrained delegation)
11. Gain domain controller rights
```

**Key toolchain**: subfinder → httpx → nuclei → sqlmap/sstimap → frp → nmap → mimikatz → crackmapexec → bloodhound → certipy

---

## Playbook 2: phishing → internal pentest

```
1. Target employee information gathering (LinkedIn/Maimai)
2. Build the phishing email (spoofed sender/legitimate subject)
3. Build the payload (macro document/LNK/ISO/HTML smuggling)
4. Send the phishing email
5. Wait for check-in (C2 beacon)
6. Local information gathering + privilege escalation
7. Credential extraction
8. Lateral movement
9. Persistence
10. Goal reached
```

**Key toolchain**: theHarvester → gophish → msfvenom/cobalt-strike → mimikatz → bloodhound

---

## Playbook 3: close-access pentest → internal network

```
1. Physical reconnaissance (WiFi signals, access control type, USB ports)
2. WiFi attack (Fluxion fake hotspot / WPA cracking)
   or BadUSB implant (Rubber Ducky keystroke injection)
   or network implant (Raspberry Pi / LAN Turtle)
3. Get an internal network access point
4. Internal scan
5. Then steps 5-11 of Playbook 1
```

**Key toolchain**: fluxion/aircrack-ng → rubber-ducky → frp → nmap → crackmapexec

---

## Playbook 4: cloud environment pentest

```
1. Cloud asset discovery (subdomain → CNAME → cloud provider)
2. Storage bucket enumeration (public S3/OSS/Blob access)
3. SSRF → cloud metadata (169.254.169.254)
4. Get temporary credentials (AK/SK/Token)
5. Cloud API enumeration (IAM/EC2/Lambda/RDS)
6. Privilege escalation (PassRole/AssumeRole)
7. Lateral movement (cross-account/cross-region)
8. Data acquisition
```

**Key toolchain**: subfinder → nuclei(ssrf) → aws-cli → pacu → ScoutSuite

---

## Playbook 5: Bug Bounty / SRC quick foothold

```
1. Asset collection (subdomains + ports + JS files)
2. Fingerprinting → quick verification of known vulnerabilities (nuclei)
3. Parameter discovery (arjun/paramspider)
4. Test class by class:
   - IDOR/broken access control (change ID/change role)
   - SSRF (internal network probing/cloud metadata)
   - SQL injection (sqlmap)
   - XSS (xsstrike)
   - File upload (bypass checks)
   - Logic flaws (payment/CAPTCHA/password reset)
5. Write the PoC + submit the report
```

**Key toolchain**: subfinder → httpx → nuclei → arjun → sqlmap → xsstrike → burpsuite

---

## Playbook 6: AD CS certificate attacks

```
1. Discover the AD CS service (certipy find)
2. Identify vulnerable templates (ESC1-ESC8)
3. Request a malicious certificate
4. Authenticate as the target user with the certificate
5. Get the NTLM hash or TGT
6. DCSync to dump every credential
```

**Key toolchain**: certipy → rubeus → mimikatz → secretsdump

---

## General decision matrix

| Current state | Next priority |
|---------|-------------|
| Only the target domain | Subdomain enumeration → port scan → web fingerprint |
| Web vulnerability found | Get a shell → internal information gathering |
| Low-privilege shell | Privilege escalation → credential extraction |
| One internal machine | Set up a tunnel → internal scan → lateral movement |
| Domain user credentials | BloodHound → find attack paths |
| Domain admin hash | DCSync → Golden Ticket |
| Cloud AK/SK | Enumerate permissions → privilege escalation → data acquisition |
| Phishing check-in | Local privilege escalation → credentials → lateral movement |
| Close-access foothold | Internal scan → same as above |
