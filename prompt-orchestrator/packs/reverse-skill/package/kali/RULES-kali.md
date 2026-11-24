# Auto-Routing Rules for Reverse Engineering / Pentest / Security Tasks (Kali Linux Edition)

> **This file is the Kali path adaptation layer, not a second behavior chain.** The root `RULES.md` is authoritative for behavior and authorization.
> The core knowledge base (`skills/config/routing.json`, SKILL.md, references) is shared with the Windows edition.
> Writing this file into `~/.claude/CLAUDE.md` or any other client-global configuration is **forbidden**. Core scripts must not write client-global files.

Hot path (same as `RULES.md`): `skills/scripts/master-route.sh` → `case-init.sh` (ACT against targets is forbidden before `auth.status=granted`) → PRIMARY `SKILL.md`. Identity: `skills/ops/IDENTITY.md`. Scripts are `kali/scripts/*.sh` in this directory.

---

## Trigger keywords (identical to the Windows edition)

- APK, Android reverse engineering, decompilation, smali, jadx, apktool, Frida, Hook
- binary analysis, IDA, radare2, r2, disassembly, reverse engineering, RE, source recovery, source reconstruction, reverse reconstruction
- frontend signing, encrypted parameters, JS reverse engineering, jshookmcp, CDP, SourceMap
- packet capture, HTTP capture, request replay, anything-analyzer
- CTF, Pwn, web pentest, exploitation, privilege escalation
- MCP reverse engineering tools, idalib-mcp
- repackaging, signing, certificate validation, root detection, anti-debugging
- so analysis, native hook, JNI
- penetration testing, red team, security assessment, blue team, incident response
- write a report, write documentation, produce a report, writeup, technical documentation, pentest report, reverse engineering report
- browser automation, open a web page, fill forms, crawl, screenshot, automated login, Playwright, agent-browser, headless
- symbol migration, bindiff, cross-version, missing PDB, function offset migration, version comparison, old version symbols
- N-day, Nday, patch diffing, patch diff, patch tuesday, 1day, CVE reproduction, vulnerability reconstruction, ghidriff, Diaphora, DeepDiff, patch analysis
- pwn, stack overflow, heap overflow, ROP, ret2libc, ret2csu, one_gadget, libc-database, tcache, fastbin, kernel pwn, SMEP, SMAP, KASLR, modprobe_path, commit_creds, pwntools, GEF, pwndbg
- firmware, IoT, binwalk, unblob, squashfs, UBI, JFFS2, Firmadyne, FAT, QEMU full-system emulation, EMBA, firmware pentest, router firmware, embedded exploitation, AFL++, boofuzz, UART, JTAG
- BurpSuite, Burp MCP, Intruder, Repeater, Collaborator, proxy history analysis
- LLM security, AI security testing, prompt injection, jailbreak, agent security, garak, PyRIT
- API security testing, GraphQL security, JWT attacks, supply chain security, SBOM, Trivy
- iOS reverse engineering, Objection, YARA, malware analysis, AI decompilation, LLM4Decompile
- agent does not do the work, lazy AI, skipped steps, prompt engineering, agent obedience
- EDR bypass, AV bypass, AV evasion, unhook, direct syscall, indirect syscall, Hell's Gate, SysWhispers, ETW patch, AMSI patch, call stack spoofing, MITRE T1562, CrowdStrike bypass, Defender bypass, SentinelOne bypass, pe-sieve
- port scan, Nmap, vulnerability scan, Nuclei, SQL injection, SQLMap, directory brute force, FFUF, password cracking, Hashcat, Hydra, Metasploit, Impacket, pentestMCP
- SRC, Bug Bounty, crowdsourced testing, bug bounty rewards, HackerOne, WAF bypass, IDOR, broken access control, arbitrary account
- drawing, flowchart, architecture diagram, attack path diagram, sequence diagram, state diagram, data flow diagram, Mermaid, Graphviz, PlantUML, diagram
- malware analysis, virus analysis, sample analysis, sandbox, YARA, IOC
- kernel driver, Rootkit, LKM, IOCTL, DeviceIoControl
- cryptography, encryption and decryption, AES, RSA, hash collision, signature verification
- protocol reverse engineering, custom protocol, Protobuf, serialization
- firmware reverse engineering, IoT, binwalk, ARM, MIPS, embedded
- WASM, WebAssembly, Python bytecode, pyc, .NET, dnSpy, IL
- macOS, iOS, Mach-O, ObjC, Swift, Frida iOS
- Go reverse engineering, Rust reverse engineering, stripped binary, GoReSym
- memory dump, forensics, forensic, steganography
- cloud security, container escape, K8s, Docker, AWS, Azure
- prompt injection, AI security, agent security, LLM attacks
- internal network pentest, lateral movement, Pass-the-Hash, domain penetration, AD attacks, BloodHound
- privilege escalation, privesc, SUID, Potato, UAC bypass
- credential extraction, Mimikatz, Kerberoasting, DCSync, LSASS
- C2, remote control, persistence, backdoor, Cobalt Strike, reverse shell
- blue team, detection, defense, incident response, SIEM, EDR, threat hunting, IOC
- mobile security testing, OWASP MASTG, app security, unpacking, packer analysis
- SSTI, template injection, SSTImap, XSS, XSStrike, cross-site scripting
- WordPress, WPScan, WPProbe, CMS pentest
- AdaptixC2, C2 framework, adversary emulation, red team simulation, Atomic Red Team
- WiFi attacks, wireless pentest, Fluxion, aircrack-ng, deauth
- NTLM relay, Coercer, authentication coercion, PetitPotam
- WinRM, evil-winrm, Windows remote execution
- NetExec, nxc, CrackMapExec, SMB enumeration
- AI automated pentesting, HexStrike, MetasploitMCP, mcp-kali-server
- Pentest Swarm, pentestswarm, swarm pentesting, Swarm AI, autonomous scanning, stigmergy
- Bug Bounty automation, attack surface management, ASM, continuous monitoring
- GEF, enhanced GDB, debugging framework
- Wireshark, tshark, PCAP analysis, packet capture analysis
- BurpSuite, web proxy, request interception, Intruder
- Responder, LLMNR poisoning, NBT-NS, MDNS
- BloodHound, AD paths, attack graph, SharpHound
- Certipy, AD CS, certificate attacks, ESC1, ESC8
- wfuzz, parameter fuzzing, Web Fuzz
- objdump, strings, file, static analysis
- ProxyCat, proxy pool, IP rotation
- red team, HW, attack and defense drill, initial foothold, initial breach, perimeter breach
- complete pentest, full-process pentest, from the internet into the internal network, from the outside all the way to the domain controller
- attack surface assessment, attack path planning, attack chain, kill chain
- next step after getting a shell, post-exploitation, foothold expansion, in-depth penetration
- close-access pentest, BadUSB, Rubber Ducky, WiFi Pineapple, Proxmark3, RFID cloning
- EDR bypass, AV evasion, AV bypass, shellcode loader, fileless attack
- phishing email, social engineering, OAuth phishing, HTML smuggling
- supply chain attack, component poisoning, third-party penetration
- trace cleanup, anti-forensics, log clearing, timestamp modification
- Cobalt Strike, Sliver, Havoc, Mythic, C2 frameworks

---

## Routing entry

> **Detection method**: the parent directory of the directory that holds this file (`RULES-kali.md`) is the package root.

Hot path (same as `RULES.md` / `routing.json`):

1. `skills/scripts/master-route.sh -Hint "<task>"`: PRIMARY
2. `skills/scripts/case-init.sh`: `scope.md`; ACT against targets is forbidden before `auth.status=granted`
3. PRIMARY `SKILL.md` ACTION REQUIRED
4. `skills/tool-index.md`: real paths; when a tool is missing, `kali/scripts/bootstrap-reverse.sh`

---

## Execution principles (same as the Windows edition, only the commands differ)

### Tool usage
- **Never guess tool paths**; read `tool-index.md` first
- When a tool is missing, call `bootstrap-reverse.sh` first to complete it automatically
- Kali preinstalls many tools, so bootstrap fails far less often than on Windows
- After 2 failed automatic installs of the same tool, stop retrying and print manual steps
- When an MCP service port does not match, ask the user for the actual port and help update the configuration

### Routing decisions
- When routing misses, **do not force the task into an existing skill**; propose a new one
- When one path fails, take another: if static fails go dynamic, if the Java layer fails look at the so, if IDA fails switch to r2
- For cross-module tasks, combine several skills per the "path crossing" section of `routing.md`

### Experience reuse
- Before each routing pass, **check** `field-journal/_index.md` **first**
- When similar experience exists, read the matching log first and reuse the verified solution
- If a past solution does not apply, explain why in the new log

### Safety boundaries
- Every operation must stay within the user's authorized scope
- Penetration testing must confirm that the user has legitimate authorization (SRC/Bug Bounty/own systems/CTF)
- Do not expand the attack surface on your own or go beyond the target scope the user specified
- When a high-risk vulnerability is found, tell the user immediately and wait for instructions before continuing
- Do not keep unredacted sensitive information in reports or logs

### Output quality
- Key operations must come with reproducible commands (not only described steps)
- Reverse engineering must state addresses, offsets and function names (not just "some function")
- Penetration testing must give a complete PoC (curl command, script, screenshot path)
- Uncertain conclusions must carry a confidence level

---

## Complete behavior chain

```
1. Identify the task as security or reverse engineering
2. Package root = the parent directory of this file
3. master-route.sh → PRIMARY (routing.json)
4. case-init.sh / scope.md: ACT against targets is forbidden before auth.status=granted
5. Open the PRIMARY SKILL.md
6. Missing tool → kali/scripts/bootstrap-reverse.sh
7. Do not write into client-global configuration
```

---

## Bootstrap command (Kali edition)

```bash
bash "<package root>/kali/scripts/bootstrap-reverse.sh" <capability1> [capability2] ... [--start-services]
```

### Common combinations

```bash
# Set up the native Kali MCPs in one step (recommended on first use)
bash kali/scripts/bootstrap-reverse.sh mcp-kali-server metasploitmcp hexstrike-ai

# Install all the 2026.1 tools
bash kali/scripts/bootstrap-reverse.sh adaptixc2 atomic-operator sstimap xsstrike wpprobe fluxion gef

# AD and internal network pentest toolchain
bash kali/scripts/bootstrap-reverse.sh coercer evil-winrm-py netexec responder bloodhound certipy

# Reverse engineering toolchain
bash kali/scripts/bootstrap-reverse.sh jadx frida gef ghidra-mcp

# Web pentest toolchain
bash kali/scripts/bootstrap-reverse.sh sstimap xsstrike wpprobe nuclei
```

All supported capability names: jadx, apktool, frida, idalib-mcp, jshookmcp, xquik-mcp, anything-analyzer, idapro, r2, rabin2, adb, agent-browser, ghidra-mcp, nmap, sqlmap, hashcat, hydra, gobuster, ffuf, msfconsole, nuclei, seclists, proxycat, mcp-kali-server, metasploitmcp, hexstrike-ai, pentestswarm, adaptixc2, atomic-operator, sstimap, xsstrike, wpprobe, fluxion, gef, evil-winrm-py, coercer, netexec, responder, crackmapexec, bloodhound, certipy, wfuzz, aircrack-ng

## Refresh the tool index

```bash
bash "<package root>/kali/scripts/refresh-tool-index.sh"
```

---

## MCP service management

### Native Kali MCPs (installed directly with apt, no extra configuration)

| Service | Package | Port | Purpose | Start command |
|------|------|------|------|---------|
| mcp-kali-server | mcp-kali-server | 5000 | Official Kali MCP; the AI calls terminal tools directly | `kali-server-mcp --port 5000` |
| MetasploitMCP | metasploitmcp | 8085/stdio | Metasploit Framework MCP interface | `metasploitmcp --transport stdio` |
| HexStrike AI | hexstrike-ai |: | MCP automation platform for 150+ security tools | `hexstrike-ai` |

### Third-party MCP services

| Service | Port | Purpose | Start command |
|------|------|------|---------|
| Pentest Swarm AI | stdio | Swarm-intelligence autonomous pentesting (recon→classify→exploit→report) | `pentestswarm mcp serve` |
| idapro | 13337-13350 | IDA Pro reverse engineering tool | `bash kali/scripts/ida-start.sh` |
| anything-analyzer | 23816 | Browser automation + HTTP capture | `cd ~/tools/anything-analyzer && pnpm dev` |
| jshookmcp |: | JS Hook/CDP/Network/AST | `npx -y @jshookmcp/jshook@0.3.4` (stdio) |
| ghidra | 8765 | Free Ghidra decompilation | Listens automatically after the Ghidra GUI starts |
| burpsuite | 9876 | BurpSuite web proxy | Started by the BurpSuite extension |

### MCP priority recommendations (Kali 2026.1)

For penetration testing scenarios, the recommended MCP priority is:

1. **pentestswarm**: fully automatic swarm pentesting, suited to large targets (1000+ subdomains) and continuous Bug Bounty monitoring
2. **mcp-kali-server**: the most general; it can call any terminal tool on Kali
3. **metasploitmcp**: dedicated to Metasploit, exploit/payload/session management
4. **hexstrike-ai**: automated orchestration, suited to multi-tool scenarios
5. **jshookmcp**: dedicated to web and JS reverse engineering

Set up every pentest MCP in one step:
```bash
bash kali/scripts/bootstrap-reverse.sh mcp-kali-server metasploitmcp hexstrike-ai pentestswarm
```

---

## Error handling strategy

| Scenario | What the AI should do |
|------|-------------|
| bootstrap succeeds | Continue the task |
| apt install fails | Check the network and sources, run `apt update`, then retry once |
| pip install fails | Try adding `--break-system-packages`, or suggest a venv |
| GitHub download fails | Check the network or proxy and give a manual download link |
| Service port mismatch | Ask for the actual port and help the user update the MCP configuration |
| The same tool fails twice | Give complete manual steps and stop retrying |

---

## Kali-specific advantages

In a Kali 2026.1 environment, the AI should know:

1. **Many tools preinstalled**: nmap/sqlmap/hashcat/hydra/metasploit/gobuster/ffuf/radare2/binwalk/burpsuite/wireshark/nikto/impacket/netexec/responder/bloodhound and others need no install
2. **Native MCP support**: the three MCP tools `mcp-kali-server`, `metasploitmcp` and `hexstrike-ai` are in the official Kali repository and install with `apt install`
3. **New in 2026.1**: AdaptixC2 (C2 framework), Atomic-Operator (red team testing), SSTImap (SSTI detection), XSStrike (XSS scanning), WPProbe (WP enumeration), Fluxion (WiFi social engineering), GEF (enhanced GDB)
4. **New in 2025.4**: evil-winrm-py (WinRM remote execution), hexstrike-ai (AI security automation), bpf-linker
5. **Kernel 6.18**: supports the latest hardware, NetHunter wireless injection patch (QCACLD-3.0)
6. **Full Wayland support**: GNOME 49 + KDE Plasma 6.5, Wayland also works in VMs
7. **Rich apt sources**: `apt install ghidra`, `apt install seclists`, `apt install coercer` and similar in one line
8. **Complete Python environment**: python3/pip3 preinstalled, frida-tools installs directly with pip
9. **No permission limits**: root by default or passwordless sudo
10. **Complete network tools**: nc/curl/wget/socat/proxychains/chisel and others preinstalled
11. **SecLists path**: after apt install it is in `/usr/share/seclists/`
12. **Wordlists**: `/usr/share/wordlists/` holds common dictionaries such as rockyou
13. **LLM integration**: the official Kali blog has a local LLM integration tutorial for Claude Desktop + Ollama + 5ire
14. **BackTrack mode**: `kali-undercover --backtrack` switches to the classic BackTrack 5 look (social engineering scenarios)

---

## Prohibited behavior (same as the Windows edition)

- Do not start reverse engineering or pentest operations without reading routing.md
- Do not guess tool paths; get them from tool-index
- Do not skip the field-journal lookup and start the task directly
- Do not skip the Checklist after the task completes
- Do not keep unredacted real target information in reports
- Do not expand the pentest scope without user authorization
- Do not keep retrying an automatic install that already failed twice
- Do not stay silent; report problems to the user immediately
- Do not invent tool version numbers or feature descriptions

---

## Mandatory post-task checklist (must not be skipped)

When the task is done (vulnerability verified, reverse engineering complete, flag obtained), the AI **must** execute each item:

```text
□ 1. Generate the formal report (docs-generator skill)
     - Use the matching template (reverse engineering report / pentest report / CTF writeup / signature report)
     - Must include: target overview, complete steps, key evidence, reproduction commands
     - Write it to the user's project directory (not inside the skill package)

□ 2. Generate diagrams (diagram-generator skill)
     - At least 1 flowchart embedded in the report
     - Type choice: pentest → attack path diagram / reverse engineering → call relationship diagram / JS → sequence diagram / CTF → solution flow

□ 3. Write back to field-journal (redacted)
     - Follow the field-journal/_template.md format
     - Must include: pitfall record, reusable patterns, toolchain findings, environment information
     - Redaction check: no real domains, IPs, tokens or usernames

□ 4. Record the knowledge found through search (if this task used web search)
     - Write the valuable content found into the references/ of the matching skill
     - State the source URL and date
     - New tool found → update bootstrap-manifest.json
     - New scenario found → update the routing.md + RULES-kali.md keywords

□ 5. Ask about community contribution
     - "Contribute this experience to the community main repository? The data is redacted, and only field-journal files are submitted."
     - User agrees → create a PR per the CONTRIBUTE-BACK.md process
     - User declines → skip

□ 6. Update the system index
     - Update field-journal/_index.md (new entry)
     - Check whether routing.md / bootstrap-manifest / tool-index need updates
     - New tool or new scenario found → apply the matching update
```

If the AI does not run this checklist after the task completes, the user can remind it: "You forgot to write the report and record the experience", and the AI must make up for it immediately.

---

## Multi-task and interruption handling

- If the user switches topics in the middle of a task, first save the current progress to field-journal (marked "unfinished")
- When the user comes back, restore the context from field-journal
- If the user gives several security tasks at once, execute them one at a time by priority, not in parallel (avoids tool conflicts)
- Long tasks (such as IDA analysis of a large file) must report progress regularly so the user does not think they are stuck

---

## Web knowledge supplement (MUST use when search is available)

When the AI can search the web, it **must search proactively** in the following scenarios:

| Scenario | What to search | What to do after the search |
|------|---------|-------------|
| Unknown packer, protection or obfuscation | Unpacking methods and tools for that packer | Write the method into the references/ of the matching skill |
| Unknown framework or protocol | Methods for reversing or pentesting that framework | Write into references/ or propose a new skill |
| Tool error or incompatibility | Error message + version compatibility | Write a field-journal pitfall record |
| New CVE or vulnerability found | PoC and exploitation methods | Write into pentest-tools/references/ |
| Routing miss (entirely new scenario) | Methodology and tools of that domain | Propose a new skill with the material found |
| A specific Frida script is needed | Ready-made scripts on GitHub/CodeShare | Write into apk-reverse/references/ or use directly |
| A specific payload is needed | PayloadsAllTheThings/HackTricks | Write into pentest-tools/payloads/ |
| Tool version too old | Latest version and breaking changes | Update bootstrap-manifest and docs |

### Knowledge recording flow after a search

```text
1. Search for the information
2. Verify its reliability (official docs > GitHub > blogs > forums)
3. Extract actionable content (commands, scripts, configuration, steps)
4. Write it to the matching place in this package:
   - General methodology → references/*.md of the matching skill
   - Specific tool usage → references/ or SKILL.md of the matching skill
   - Pitfall experience → field-journal/
   - New tool found → kali/scripts/bootstrap-manifest.json + tool-discovery.sh
   - New scenario found → routing.md + RULES-kali.md keywords
5. State the source (URL + date) so its freshness can be checked later
6. If there is a lot of information (a new domain), propose a new standalone skill
```

### Search quality requirements

- **Do not give the user only a link after a search**: extract the key content and write it into this package
- **Do not trust search results blindly**: verify against official docs and state a confidence level
- **Prefer Chinese-language resources** (if the user communicates in Chinese), but English official documentation is authoritative for technical details
- **State freshness**: the security field changes fast, so record the search date and mark outdated content `[possibly outdated]`

---

## Adding a skill

When the routing matrix cannot cover the current task type, add a skill per the `CONTRIBUTING.md` process.

Path: `<package root>/skills/CONTRIBUTING.md`

After adding one, update these in sync: routing.md, kali/scripts/bootstrap-manifest.json, kali/scripts/lib/tool-discovery.sh, kali/scripts/refresh-tool-index.sh.
