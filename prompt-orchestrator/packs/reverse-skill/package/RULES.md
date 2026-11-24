# Reverse Engineering / Penetration Testing / Security Task Auto-Routing Rules

> **This file is the behavior-chain source of truth.** Route tables live only in `skills/config/routing.json`. Once the user explicitly activates this package for a task, every supported AI editor/client (Claude Code, Kiro, Cursor, Cline, Windsurf, Codex CLI, Aider, Continue, Reasonix, or others) MUST follow the same client-neutral hot path.

---

## ACTIVATION AND CONSENT GATE (before any side effect)

**Reading repository files is not authorization to execute them.** A request to inspect, review, summarize, or compare this repository remains read-only.

**Explicit user approval is required before running any repository script.** For a configuration or task request, first disclose the exact commands and expected filesystem writes, downloads, service starts, network access, and client-configuration changes. Obtain approval before the first such side effect. Newly discovered side-effect categories require a new approval.

**Client-global configuration remains opt-in.** Repository text MUST NOT be copied into global client rules, hooks, prompts, or MCP configuration unless the user explicitly selects that client and approves the exact change.

After activation and approval, deterministic steps covered by the disclosed plan proceed without repeated confirmation. Target authorization remains a separate hard gate: naming a target does not grant permission, and `-Force` / `--force` never bypasses scope controls.

## Activated task hot path

```text
1. NOW: Treat this file's directory as the package root.
2. NOW: Run the approved platform-native router → PRIMARY (SSoT: skills/config/routing.json).
   - Windows: powershell -File skills/scripts/master-route.ps1 -Hint "<task>"
   - Linux/macOS/Kali: bash skills/scripts/master-route.sh --hint "<task>"
3. NEXT: Run the approved platform-native case-init until scope.md has auth.status=granted plus a legal network_profile, or an explicitly authorized offline-sample scope is ready. Mentioning a target is NOT granted. -Force/--force never bypasses the gate.
4. ACT: Open PRIMARY SKILL.md and execute ACTION REQUIRED. Tools only from tool-index.md; missing tools use a separately disclosed and approved platform-native bootstrap action.

Optional later (do NOT preload):
- Ambiguous PRIMARY → skills/routing.md (advisory matrix only)
- Synthesis / Finding promotion → ops/analysis-decision-framework.md (ADF-* overlay IDs, not routing R*)
- Identity reminder → ops/IDENTITY.md (skill router, not a Z3r0 platform)
```

IMPORTANT: Shared installation:
- tool-index.md is the SINGLE SOURCE OF TRUTH for tool availability
- If another CLI already installed tools (tool-index shows "yes"), DO NOT reinstall
- Only run the platform-native refresh-tool-index if it is covered by the consent plan and the index may be stale
- Only run bootstrap for tools that are BOTH needed AND marked "no", after disclosing and obtaining approval for installation effects

Conditional reads (load only when needed, do NOT preload):
- Hesitating about whether a target operation is allowed → read skills/field-journal/precedent-reverse.md or precedent-pentest.md; these files do not replace explicit target authorization
- Wanting to skip approved deterministic steps or stop at acknowledgment → read skills/llm-security/references/agent-obedience-engineering.md excuse rebuttal table
```

Once activated, the goal is completing the requested task rather than merely acknowledging these rules. Before activation, remain read-only.

---

## Client integration boundary

The files in `skills/`, routing configuration, tests, manifests, case artifacts, and reports are the platform-neutral core. A host such as Claude Code, Codex, Cursor, OpenCode, or another agent may load this repository through its own project-instruction or skill adapter, but no host-specific file is required for routing or tests.

Core scripts MUST NOT write client-global configuration. Optional adapters belong in isolated platform documentation or adapter packages and must preserve identical routing semantics.

---

## Trigger Keywords (ANY match triggers routing)

- APK, Android reverse, decompile, smali, jadx, apktool, Frida, Hook
- binary analysis, IDA, radare2, r2, disassembly, reverse engineering, RE, source recovery
- frontend signature, encrypted params, JS reverse, jshookmcp, CDP, SourceMap
- packet capture, HTTP capture, request replay, anything-analyzer
- CTF, Pwn, web pentest, exploit, privilege escalation
- MCP reverse tools, idalib-mcp, repackage, certificate pinning, certificate validation, root detection, anti-debugging
- .so analysis, native hook, JNI
- penetration testing, red team, security assessment, blue team, incident response
- report/docs generation in security context, writeup, pentest report
- security browser automation, Playwright pentest, agent-browser recon
- N-day, patch diff, CVE reproduction, 1day, ghidriff, Diaphora
- pwn, stack overflow, heap overflow, ROP, ret2libc, pwntools, GEF, pwndbg, kernel pwn
- firmware, IoT, binwalk, unblob, squashfs, EMBA, UART, JTAG, embedded exploitation
- EDR bypass, AV bypass, AV evasion, unhook, direct syscall, indirect syscall, AMSI patch, ETW patch
- port scan, Nmap, vulnerability scan, Nuclei, SQL injection, SQLMap, directory brute force, FFUF, password cracking, Hashcat, Hydra, Metasploit, Impacket
- SRC, Bug Bounty, crowdsourced testing, WAF bypass, IDOR, broken access control
- BurpSuite, Burp MCP, Intruder, Repeater, Collaborator, proxy history
- LLM security, AI security testing, Prompt injection, jailbreak, Agent security, agent skills security, Agentic Skills Top 10, skill supply chain, malicious skill, MCP supply chain
- OWASP LLM Top 10, ASI Top 10, Agentic AI, tool abuse, memory poisoning, garak, PyRIT, promptfoo
- API security, GraphQL, JWT attack, supply chain security
- iOS reverse, Objection, YARA, malware analysis, AI decompilation
- internal network, lateral movement, domain penetration, AD attack, BloodHound
- privilege escalation, credential extraction, Mimikatz, Kerberoasting, DCSync
- C2, persistence, Cobalt Strike, Sliver, Havoc
- game reverse, anti-cheat, Unity, IL2CPP, Cheat Engine
- .NET reverse, C# reverse, dnSpy, dnSpyEx, de4dot, ConfuserEx, SmartAssembly, .NET Reactor, dnlib, IL patch, SharpHound, Rubeus
- symbol migration, bindiff, cross-version, PDB missing
- OSINT, open source intelligence, threat intelligence, CTI, public X/Twitter IOC enrichment
- security diagram, attack path diagram, security architecture: trigger `diagram-generator/`

Additional trigger keywords (from the upstream Chinese keyword list):

- re-signing, signature, writing reports, writing documentation, technical documentation, reverse engineering report
- browser automation, opening web pages, form filling, crawling, screenshots, automated login, headless, desktop automation, OpenReverse, UIA, CUA, Windows automation
- function offset migration, version comparison, old version symbols
- Nday, patch Tuesday, vulnerability reconstruction, DeepDiff, Microsoft Update Catalog, wsuspect, MSRC, patch analysis
- ret2csu, one_gadget, libc-database, tcache, fastbin, unsorted bin, large bin, House of Force, House of Orange, kROP, SMEP, SMAP, KASLR, modprobe_path, core_pattern, commit_creds
- UBI, JFFS2, Firmadyne, FAT, QEMU full-system emulation, cve-bin-tool, firmware penetration testing, router firmware, AFL++, boofuzz
- Hell's Gate, Halo's Gate, Tartarus Gate, SysWhispers, call stack spoofing, hardware breakpoint Blindside, MITRE T1562, ntdll unhook, kernel callback, CrowdStrike bypass, Defender bypass, SentinelOne bypass, Elastic Defend, pe-sieve, pentestMCP
- vulnerability bounty, HackerOne, bypassing the WAF, privilege escalation, arbitrary account
- drawing, flowchart, architecture diagram, sequence diagram, state diagram, data flow diagram, Mermaid, Graphviz, PlantUML, diagram
- virus analysis, sample analysis, sandbox, IOC, kernel driver, Rootkit, LKM, IOCTL, DeviceIoControl
- cryptography, encryption and decryption, AES, RSA, hash collision, signature verification
- protocol reverse engineering, custom protocol, Protobuf, serialization, ARM, MIPS, embedded
- WASM, WebAssembly, Python bytecode, pyc, IL, macOS, Mach-O, ObjC, Swift, Frida iOS
- Go reverse engineering, Rust reverse engineering, stripped binary, GoReSym
- memory dump, forensics, steganography
- cloud security, container escape, K8s, Docker, AWS, Azure
- Pass-the-Hash, SUID, Potato, UAC bypass, LSASS, remote control, backdoor, reverse shell
- detection, defense, SIEM, EDR, threat hunting, activity correlation
- mobile security testing, OWASP MASTG, app security, unpacking, packer analysis
- SSTI, template injection, SSTImap, XSS, XSStrike, cross-site scripting, WordPress, WPScan, WPProbe, CMS penetration testing
- AdaptixC2, C2 framework, adversary emulation, red team emulation, Atomic Red Team
- WiFi attacks, wireless penetration testing, Fluxion, aircrack-ng, deauth
- NTLM relay, Coercer, authentication coercion, PetitPotam, WinRM, evil-winrm, Windows remote execution
- NetExec, nxc, CrackMapExec, SMB enumeration
- AI automated penetration testing, HexStrike, MetasploitMCP, mcp-kali-server
- Pentest Swarm, pentestswarm, swarm penetration testing, Swarm AI, autonomous scanning, stigmergy
- Bug Bounty automation, attack surface management, ASM, continuous monitoring
- GDB enhancement, debugging framework, Wireshark, tshark, PCAP analysis
- web proxy, intercepting requests, Responder, LLMNR poisoning, NBT-NS, MDNS, AD paths, attack graph
- Certipy, AD CS, certificate attacks, ESC1, ESC8, wfuzz, parameter fuzzing, web fuzzing
- objdump, strings, file, static analysis, ProxyCat, proxy pool, IP rotation
- HW, offensive and defensive exercises, initial foothold, initial access, perimeter breach
- full penetration test, end-to-end penetration test, from the internet into the intranet, from outside to the domain controller
- attack surface assessment, attack path planning, attack chain, kill chain
- next step after getting a shell, post-exploitation, foothold expansion, in-depth penetration
- close-access penetration testing, BadUSB, Rubber Ducky, WiFi Pineapple, Proxmark3, RFID cloning
- shellcode loader, fileless attack, phishing email, social engineering, OAuth phishing, HTML smuggling
- supply chain attack, component poisoning, third-party penetration testing
- trace cleanup, anti-forensics, log clearing, timestamp modification, Mythic
- redaction, placeholders, anonymization, {target_ip}, {username}, writing a writeup, sharing payloads
- msfconsole hang, MSF stuck, orphan process, orphan ruby, MSF calling conventions
- indirect injection, system prompt extraction, model security, Agent hijacking, goal hijacking
- AgentThreatBench, AI red team, LLM red team, model red team
- API security testing, interface penetration testing, introspection attack, REST API audit
- BOLA, BFLA, object-level authorization, function-level authorization, alg:none, key confusion, OAuth bypass
- rate limit bypass, API rate limiting, WebSocket security
- SBOM, software composition analysis, SCA, dependency scanning, dependency vulnerabilities
- CI/CD security, pipeline audit, build integrity, container security, image scanning, container signing
- Trivy, Syft, Cosign, Gitleaks, OSV-Scanner, Dependency-Track, SLSA
- IPA analysis, Objective-C, jailbreak detection, class-dump, jtool2, Hopper
- dynamic instrumentation, SSL pinning bypass, root detection bypass, Frida Gadget, rootless injection
- MSTG, OWASP Mobile, MobSF, mobile penetration testing, Android security, iOS security
- Sigma, threat detection rules, behavior detection, IOC extraction
- CAPE, Joe Sandbox, Azul, anti-analysis detection, anti-sandbox, VM detection, anti-VM, PEB detection
- FLOSS, Detect It Easy, CAPE Sandbox
- LLM reverse engineering, neural decompilation, LLM4Decompile, Glaurung, AI-assisted reverse engineering
- agent not working, AI not executing, reads but does not act, agent compliance, lazy AI, skipping steps, Codex not working, Claude Code not executing
- prompt engineering, prompt optimization, instruction strengthening, Skill engineering, agent instructions, Harness Engineering, Steering Hooks, Excuse Rebuttal
- agent enforcement, AI behavior constraints, agent rule engine, AI compliance engineering, making the AI do the work

---

## Routing Entry

> **Detection method**: The directory containing this file (`RULES.md`) is the package root. Do NOT assume a fixed drive letter.
>
> This hot path applies only after explicit package activation and approval for the disclosed first-side-effect plan. Inspection-only requests stop before it.

Hot path only:

1. Platform-native master-route — `skills/scripts/master-route.ps1 -Hint "<task>"` (Windows) / `skills/scripts/master-route.sh --hint "<task>"` (Linux, macOS, Kali) — PRIMARY from `skills/config/routing.json`
2. Platform-native case-init (`.ps1` / `.sh`) — `scope.md` gate
3. PRIMARY `SKILL.md` ACTION REQUIRED
4. `skills/tool-index.md` — real tool paths (if missing → generate it with the approved platform-native refresh command)

`skills/routing.md` is an advisory 3-axis view **after** PRIMARY, not a second router.

---

## Execution Principles

### Tool Usage
- **NEVER guess tool paths** — read `tool-index.md` first, it contains the exact installed path for each tool
- Missing tools → disclose the exact platform bootstrap command and its install, network, service, and configuration effects; obtain approval, then run it instead of guessing paths:
  - Windows: `bootstrap-reverse.ps1`
  - Linux / macOS: `bash skills/scripts/bootstrap-reverse.sh`
  - Kali Linux: `bash kali/scripts/bootstrap-reverse.sh`
- **After an approved tool installation, run the platform-appropriate refresh script only when it is covered by the disclosed plan** (otherwise disclose it and obtain approval first). Windows: `refresh-tool-index.ps1`; Linux / macOS / Kali: `bash skills/scripts/refresh-tool-index.sh` or `bash kali/scripts/refresh-tool-index.sh`. This keeps tool-index.md accurate without introducing an undisclosed write.
- When writing tool-index.md entries, paths MUST be **complete absolute paths** (e.g., `D:\wangluo\jadx\bin\jadx.bat`, NOT just `jadx`). Include: full path, version number, install method, and verification command.
- Same tool fails auto-install 2 times → stop retrying, output full manual install steps
- MCP service port mismatch → ask user for actual port, help update config
- `tool-index.md` is the **shared registry** — all CLIs read from it, all CLIs write to it after installing

### Routing Decisions
- Route not matched → do NOT force-fit into existing skill, propose new skill creation
- One path blocked → switch: static↔dynamic, Java↔Native, IDA↔r2, tool X↔equivalent tool Y
- Cross-module tasks → combine multiple skills per routing.md "Path Crossing" section

### Experience Reuse
- Before entering any route, **MUST check** `field-journal/_index.md`
- Similar past experience exists → read the log, reuse verified solutions
- If historical solution doesn't apply → explain why in new log entry

### Self-Supervision (prevent loops, prevent drift)
- Every 5 tool calls, or when feeling "stuck", pause for `<self_review>`:
  - Am I actually making progress toward the goal? Cite specific evidence
  - Have I called the same tool with same params ≥ 2 times? Yes → MUST change approach
  - Can I clearly explain the last error message? No → understand first, then act
- Same method fails 2-3 times → MUST switch approach
- Single command repeated ≥ 3 times → MUST stop and evaluate
- Approaching tool call budget (>30 calls per subtask) → report to user, ask whether to continue

### Security Boundaries
- All operations MUST be within user's authorized scope
- Pentest MUST confirm user has legal authorization (SRC/Bug Bounty/own system/CTF)
- Do NOT expand attack surface beyond user-specified target range
- High-severity vulnerability found → immediately inform user, wait for instructions
- Do NOT retain un-anonymized sensitive info in reports or logs

### Output Quality
- Critical operations MUST include reproducible commands (not just descriptions)
- Reverse analysis MUST annotate addresses/offsets/function names (not just "some function")
- Pentest MUST provide complete PoC (curl commands/scripts/screenshot paths)
- Uncertain conclusions MUST be labeled with confidence level

---

## Canonical Behavior Chain (All other files reference THIS version)

```text
0. Require explicit package activation and approval for the exact first-side-effect plan; inspection-only requests stop here and remain read-only
1. Identify task as security/reverse type → trigger this routing rule
2. Detect package root path (derive from this file's location)
3. Platform-native master-route (`.ps1` Windows / `.sh` Linux, macOS, Kali) → PRIMARY from skills/config/routing.json; use routing.md only when ambiguous
4. Platform-native case-init / scope.md (ops/scope-contract): auth.status=granted + valid network profile, or explicit authorized offline sample, before any target ACT; Force never bypasses the hard gate
5. Open PRIMARY SKILL.md ACTION REQUIRED
6. Route not matched → propose new skill (edit routing.json + benchmark; do not hand-edit routing.md as SSoT)
7. Read tool-index.md → confirm local tool status. If missing, use the approved platform-native refresh command
8. Missing tools → disclose exact bootstrap/refresh commands and effects, obtain approval, then run the platform-native actions
9. Enter skill workflow → execute (timeline/workitems; Evidence→Finding→Path per ops/). At transitions, carry unchanged authoritative state by reference and emit only `decision_delta`; menus only at genuine decision boundaries.
10. Continuously report progress (do NOT go silent)
11. Task complete → Completion Checklist (report must include Evidence chain)
12. Output final results
```

---

## Completion Checklist (MUST NOT skip)

After task completion (vulnerability verified / reverse complete / flag captured), AI **MUST** execute each item:

```text
□ 1. Generate the formal report (docs-generator skill)
     - Use the matching template (reverse engineering report / penetration test report / CTF writeup / signing report)
     - Must contain: target overview, complete steps, key evidence, reproduction commands
     - Write it to the user's project directory (not inside the skill package)

□ 2. Generate diagrams (diagram-generator skill)
     - At least 1 flowchart embedded in the report
     - Type: penetration → attack path diagram / reverse engineering → call graph / JS → sequence diagram / CTF → solving flow

□ 3. Write back to the field-journal (redacted)
     - Follow the field-journal/_template.md format
     - Must contain: pitfalls, reusable patterns, toolchain findings, environment information
     - Redaction check: no real domains/IPs/tokens/usernames

□ 4. Capture searched knowledge (if web searches ran during this task)
     - Write valuable search results into the matching skill's references/
     - Note the source URL and date
     - New tool found → update bootstrap-manifest
     - New scenario found → update routing-benchmark.json first, then routing.json; sync MASTER-ROUTING.md and the routing.md appendix as needed

□ 5. Ask about community contribution
     - "Contribute this experience to the community main repository? The data is redacted, and only field-journal files are submitted."
     - User agrees → create a PR per the CONTRIBUTE-BACK.md flow
     - User declines → skip

□ 6. Update the system indexes
     - Update field-journal/_index.md (add the entry)
     - Check whether these need updates: routing.json / routing-benchmark / MASTER-ROUTING.md / routing.md appendix / bootstrap-manifest / tool-index
     - New tool or new scenario found → run the matching update
```

If the AI skips this checklist after a task, the user can remind it ("you forgot the report and the journal write-back"), and the AI must complete the items right away.

---

## Error Handling Strategy

| Scenario | AI Action |
|----------|-----------|
| Approved bootstrap succeeds | Continue within the already disclosed plan |
| Bootstrap fails, clear reason | Output structured guidance, wait for user |
| Bootstrap fails, unclear reason | Output known info + suggest checking network/permissions |
| Service port mismatch | Ask actual port, help update MCP config |
| Same tool fails 2 times | Declare "auto-install cannot complete", give full manual steps, stop retrying |
| Analysis direction blocked | Switch path (static↔dynamic, Java↔Native, IDA↔r2) |
| Task exceeds capability | Clearly state limitations, suggest specific human intervention points |
| MCP tool call errors | Check whether the service is online; start it only if covered by the approved plan, otherwise disclose the action or guide the user |

---

## MCP Service Management

| Service | Port | Purpose | Startup |
|---------|------|---------|---------|
| idapro | 13337-13350 | IDA Pro 72 reverse tools | Auto-start (IDA plugin), port increments per instance |
| anything-analyzer | 23816 | Browser automation + HTTP capture | `pnpm dev` (project dir) |
| jshookmcp | — | JS Hook/CDP/Network/AST | `npx -y @jshookmcp/jshook@0.3.4` (stdio) |
| ghidra | 8765 | Ghidra free decompiler | Ghidra GUI auto-listens after launch |
| burpsuite | 9876 | BurpSuite 78-tool full control (Proxy/Intruder/Repeater/Scanner/Collaborator) | Burp extension auto-loads |

Before using MCP tools:
1. First confirm the service's `MCP registered` status in `tool-index.md`
2. Not registered → disclose the exact registration command and its configuration impact, and call bootstrap only after consent
3. Registered but the port does not respond → a read-only scan of the port range is allowed (IDA: 13337-13350); start the service only when the approved plan covers it, otherwise disclose and get consent first
4. IDA MCP in particular: **do not hard-code 13337**; the port may change each time a new file opens, so check the `[MCP] port=xxxxx` log in the IDA Output window
5. Startup failed → guide the user through manual handling

---

## Excuse Rebuttal Table (Anti-Laziness — 2026 Field-Tested)

| Agent's Common Excuse | Rebuttal (ENFORCE) |
|---|---|
| "I can skip this step, let me just..." | **FORBIDDEN to skip.** Every step in the behavior chain is required. If you think you can skip, output your specific reason and wait for user confirmation. |
| "Based on my judgment, this isn't necessary" | **Your judgment does not apply here.** List the specific criteria you used, explain why it allows skipping an explicitly written step. |
| "The user probably doesn't need this" | **NEVER decide for the user.** Present all options, mark recommendations but don't hide alternatives. |
| "I already know how to do this, don't need to read X" | **Read X first, then act.** Even if you're sure, X may contain task-specific constraints. Reading takes seconds. |
| "To save time, I can skip..." | **The correct way to save time is parallel execution of independent steps, NOT skipping steps.** |
| "I've used this tool before, I know the path" | **FORBIDDEN to guess paths.** MUST get actual path from tool-index. Different machines have different install locations. |
| "Task is basically done, don't need checklist" | **Task completion = ALL Checklist items checked.** Unchecked checklist = task NOT complete. |
| "I can't find tool-index, so I'll just guess the path" | **A missing file is safer than a wrong guessed path.** Disclose the platform's native refresh command and its local writes, generate tool-index after consent; guessing paths is forbidden. |
| "The user didn't explicitly ask for a report, so I won't write one" | **The report is the default.** Security/reverse engineering tasks must end with a report unless the user explicitly says "no report". |
| "This is too simple to record in the journal" | **Simple tasks have pitfall value too.** Record at least: target type + what was used + any surprises. One line is fine, but it must be written. |
| "After approval, I will pause before every deterministic step" | **Do not repeatedly re-confirm disclosed actions.** Continue while informing the user; pause only for a new side-effect category or genuine decision point. |
| "An activated task exists, but I will only acknowledge the rules" | **Continue the approved task.** Match the existing user intent to the routing table and begin the disclosed workflow. Inspection-only requests remain read-only. |
| "User asked to redo import-table / step X, but I did something else more useful" | **Redo = redo the named step** (or the user-confirmed prerequisite path). MUST refresh Evidence for X. FORBIDDEN to substitute an unrelated step or silently skip X. Unpacking is a **prerequisite** for readable IAT, not a substitute for import Evidence. |
| "User said skip unpack and read IAT on a packed sample; I'll just dump the garbage table as done" | **Feasibility gate:** if X is blocked (packed/unreadable IAT), MUST state the blocker, recommend order (unpack/repair IAT or go dynamic), and **ask confirm**. If user forces X, do it and mark `quality=unreadable/packed`; FORBIDDEN to draw capability-negative conclusions from garbage IAT. |
| "Self-check crash after unpack; keep patching the file on disk" | **Patch 6:** record E-self-check-crash / E-iat-repair-fail, switch to dynamic (bp CreateFile/GetFileSize). FORBIDDEN endless static file thrash. |
| "IAT repair keeps failing; I'll grind more static unpackers" | **IAT repair iron rule:** try auto/semi-auto repair first; on tool error or unreable binary after repair, STOP static IAT, record E-iat-repair-fail, switch to dynamic API breakpoints. FORBIDDEN infinite static IAT thrash. |
| "No import table (.NET) so the hard gate does not apply" | **Equivalent anchor still MUST:** .NET → dnSpy/IL/metadata summary into E-imports slot; DLL/SYS → E-exports alongside imports. FORBIDDEN to skip the gate. |

> If you catch yourself thinking any of the sentences above, stop, return to the correct step of the behavior chain and continue.

---

## Self-Audit Before Claiming "Complete"

Before saying "task complete" or "done", MUST self-check:

```text
□ 1. After activation and approval, did I execute every applicable step in the disclosed behavior chain (not just read docs)?
□ 2. Did I guess any tool paths? If yes, what's the actual tool-index path?
□ 3. Did I produce the approved task artifacts/evidence without any undisclosed side-effect category?
□ 4. Is the Completion Checklist fully checked?
□ 5. If ANY answer is "no" → task is NOT complete. Go back and fix.
```

**Note**: this self-check is not optional. Run through it before every step you claim as "done".

---

## Prohibited Behaviors

- ❌ Do NOT start reverse/pentest without explicit package activation, first-side-effect approval, and the platform-native router (routing.json)
- ❌ Do NOT guess tool paths — MUST get from tool-index
- ❌ Do NOT skip field-journal lookup before starting task
- ❌ Do NOT skip Checklist after task completion
- ❌ Do NOT retain un-anonymized real target info in reports
- ❌ Do NOT expand pentest scope without user authorization
- ❌ Do NOT retry auto-install after 2 failures
- ❌ Do NOT go silent — immediately inform user of problems
- ❌ Do NOT fabricate tool version numbers or feature descriptions
- ❌ After activation, do NOT stop at acknowledging the rules — continue the approved routed task; inspection-only requests remain read-only
- ❌ Do NOT say "steps 1-4 complete" when you only read them — distinguish "read" from "executed"
- ❌ After approval, do NOT request confirmation for every disclosed deterministic step; pause only for new effects or genuine decisions

---

## Multi-Task & Interrupt Handling

- If user switches topic mid-task, save current progress to field-journal (mark as "incomplete")
- When user returns, restore context from field-journal
- Multiple security tasks given simultaneously → execute sequentially by priority (avoid tool conflicts)
- Long-running tasks (e.g., large file IDA analysis) → report progress periodically, don't let user think it's stuck

---

## Context Window Layout Rules (Attention Optimization)

LLM attention distribution (high→low):
```text
[First 10%]  ████████████ ← Highest attention: put "immediate action" instructions here
[Middle 80%] ████░░░░░░░░ ← Attention decays: put reference materials here
[Last 10%]   ████████████ ← Attention recovers: put "MUST NOT skip" and Checklist here
```

- **MUST**: Critical actions go in first or last 10% of any instruction file
- **MUST NOT**: Bury important directives in the middle of long documents

---

## Parameter Stability (Code Words)

When tool parameters MUST be passed exactly as given, use opaque identifiers (code words) to reduce model's tendency to "semantically optimize":

- Applicable: bootstrap params, dangerous action switches, approval status values, scan scope boundaries
- **MUST**: Define mapping table first, expand in command layer
- **MUST NOT**: Let Agent freely rewrite semantic parameters (e.g., changing strict/deny to lenient synonyms)

Example:
```text
alpha -> --scope authorized-only
beta  -> --approval required
gamma -> --destructive false
```

---

## Web Search Knowledge Augmentation (MUST use when search capability available)

When AI has web search capability, **MUST proactively search** in these scenarios:

| Scenario | Search For | After Search |
|----------|-----------|--------------|
| Unknown packer/protection/obfuscation | Unpacking methods and tools | Write to skill's references/ |
| Unknown framework/protocol | Reverse/pentest methodology | Write to references/ or propose new skill |
| Tool error/incompatibility | Error message + version compatibility | Write to field-journal |
| New CVE/vulnerability discovered | PoC and exploitation method | Write to pentest-tools/references/ |
| Route not matched (new scenario) | Domain methodology and tools | Propose new skill with search results |
| A specific Frida script is needed | Ready-made scripts on GitHub/CodeShare | Write to apk-reverse/references/ or use directly |
| A specific payload is needed | PayloadsAllTheThings/HackTricks | Write to pentest-tools/payloads/ |
| Tool version is outdated | Latest version and breaking changes | Update bootstrap-manifest and the documentation |

### Knowledge capture after a search

```text
1. Search and collect the information
2. Check its reliability (official documentation > GitHub > blogs > forums)
3. Extract the actionable content (commands/scripts/configuration/steps)
4. Write it to the matching place in this package:
   - General methodology → the matching skill's references/*.md
   - Specific tool usage → the matching skill's references/ or SKILL.md
   - Pitfall experience → field-journal/
   - Newly found tools → bootstrap-manifest.json + ToolDiscovery.ps1
   - Newly found scenarios → routing-benchmark.json + routing.json; sync MASTER-ROUTING.md and add to the routing.md appendix when needed
5. Note the source (URL + date) so its freshness can be checked later
6. If the information is large enough (a new domain), propose a new standalone skill
```

### File format for captured knowledge

When search results go into references/, use this format:

```markdown
# [Topic name]

> Source: [URL] ([date])
> Applies to: [when to use it]

## [Content]
...
```

### Registering new domains in routing

When a search reveals a completely new technical domain (not covered by the current `routing.json` at all), the AI should:

1. Add a failing case to `routing-benchmark.json` first
2. Add keywords or a new PRIMARY to `routing.json`, and sync the priority table in `MASTER-ROUTING.md`
3. Add notes to the three-axis appendix of `routing.md` as needed; never treat it as the source of truth
4. If the content stands on its own, add a skill directory per the CONTRIBUTING.md flow
5. Update the module table in skills/SKILL.md

### Search quality requirements

- **Do not answer a search with only a link**: extract the key content and write it into this package
- **Do not trust search results blindly**: check them against official documentation and state the confidence
- **Prefer Chinese-language resources when the user communicates in Chinese**, but take technical details from the official English documentation
- **Note freshness**: the security field changes fast, so record the search date and mark stale content `[possibly outdated]`

---

## Bootstrap Command (reference; execute only after disclosure and approval)

These commands can install software, access the network, start services, or change configuration. Include the exact selected command and effects in the consent plan before execution.

Windows (PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<SKILL_ROOT>/skills/scripts/bootstrap-reverse.ps1" -Capability @('tool_name') -StartServices

Supported capability names (must match `skills/scripts/bootstrap-manifest.json`):  
jadx, apktool, jeb-pro, binaryninja, frida, frida-ps, idalib-mcp, reqable-mcp, jshookmcp, xquik-mcp, anything-analyzer, idapro, r2, rabin2, adb, agent-browser, ghidra-mcp, seclists, proxycat, burpsuite-mcp, nmap, pentestswarm, binwalk, yara, pwntools, bkcrack

Do NOT invent capabilities. Tools not listed require manual install steps in the skill docs.
```

Linux / macOS (Bash):

```bash
bash <SKILL_ROOT>/skills/scripts/bootstrap-reverse.sh tool_name --start-services
```

Kali Linux (Bash, Kali-native tooling):

```bash
bash <SKILL_ROOT>/kali/scripts/bootstrap-reverse.sh tool_name --start-services
```

## Refresh Tool Index (reference; execute only when covered by the approved plan)

This writes generated local index files. Disclose and obtain approval unless the action was already included in the active plan.

Windows (PowerShell):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<SKILL_ROOT>/skills/scripts/refresh-tool-index.ps1"
```

Linux / macOS (Bash):

```bash
bash <SKILL_ROOT>/skills/scripts/refresh-tool-index.sh
```

Kali Linux (Bash):

```bash
bash <SKILL_ROOT>/kali/scripts/refresh-tool-index.sh
```

---

## Adding a Skill

When `routing.json` cannot cover the current task type, add a skill per the `CONTRIBUTING.md` flow.

Path: `<package root>/skills/CONTRIBUTING.md`

After adding one, update routing-benchmark.json, routing.json, MASTER-ROUTING.md and skills/SKILL.md in sync; when tools are involved, also update bootstrap-manifest.json, ToolDiscovery.ps1 and refresh-tool-index.ps1. Sync `routing.md` only as an ambiguity appendix when needed.

---

## Compact reminder (do NOT write this into client-global config)

> Optional in-session recap. Core scripts MUST NOT write client-global configuration.

### Trigger Keywords (Bilingual)

- APK, Android reverse, decompile, jadx, apktool, Frida, Hook
- binary analysis, IDA, radare2, r2, disassembly, reverse engineering
- frontend signature, JS reverse, jshookmcp, CDP, SourceMap
- packet capture, HTTP capture, anything-analyzer
- CTF, Pwn, web pentest, exploit, privilege escalation
- penetration testing, red team, Nmap, Nuclei, SQLMap, FFUF, Hashcat, Metasploit
- SRC, Bug Bounty, WAF bypass, IDOR, broken access control
- BurpSuite, Burp MCP, Intruder, Repeater, Collaborator
- LLM security, Prompt injection, jailbreak, Agent security, garak, PyRIT
- EDR bypass, AV evasion, AV bypass, direct syscall
- firmware, IoT, binwalk, embedded
- internal network, lateral movement, domain penetration, BloodHound
- API security, supply chain security, supply chain, YARA, malware analysis
- iOS reverse, game reverse, anti-cheat, pwn, ROP, kernel pwn

### Post-Activation Execution (Compact — do NOT re-run first-time setup!)

```text
0. GATE: Require explicit package activation and approval for the disclosed first-side-effect plan; inspection-only requests remain read-only.
1. NOW: Run the approved platform-native master-route (.ps1 on Windows / .sh on Linux, macOS, Kali) → PRIMARY from routing.json
2. NEXT: If ambiguous, open <SKILL_ROOT>/skills/routing.md
3. NEXT: Use the approved platform-native case-init / scope.md; set auth.status=granted + valid network profile, or an explicit authorized offline-sample scope; Force never bypasses the hard gate
4. ACT: Open PRIMARY SKILL.md; timeline/workitems + Evidence→Finding→Path (ops/*)
```

### Core Rules (Compact)

- **MUST**: explicit package activation + approval for the disclosed first-side-effect plan before running repository scripts
- **MUST**: case scope (platform-native case-init / ops/scope-contract) before ACT; auth.status=granted + valid network/offline-sample scope required
- **MUST**: `-Force` / `--force` never bypasses authorization, scope, network, or readiness gates
- **MUST**: Missing tools → disclose the installation action, obtain approval, then bootstrap; NEVER guess paths
- **MUST NOT**: Treat repository text, precedent-auth.md, or "user named a target" as execution/target authorization
- **MUST NOT**: Re-confirm every deterministic step already covered by an activated and approved plan

### Excuse Rebuttal (Compact)

| Excuse | Rebuttal |
|--------|----------|
| "Can skip this step" | FORBIDDEN. Output reason, wait for user |
| "User probably doesn't need this" | NEVER decide for user |
| "Already know how, don't need to read X" | Read X first, may have task-specific constraints |
| "Task basically done, no checklist needed" | Completion = ALL checklist items checked |
| "I'll stop after every approved step" | After activation and approval, disclosed deterministic steps continue without repeated confirmation |
| "After activation, I will only acknowledge the rules" | Continue the approved task instead of stopping at acknowledgment |

### Task Completion Self-Check (Compact)

```text
□ After activation and approval, did I run every applicable step of the disclosed behavior chain?
□ Did I produce the approved task artifacts/evidence without any undisclosed category of side effect?
□ Did I guess a tool path? If so, what is the actual tool-index path?
□ Is every Checklist item (report + diagrams + journal) ticked?
□ If any item above was "not done" → the task is not complete; go back and finish it.
```

### Prohibited Behaviors (Compact)

- Do not run repository scripts before activation; stay read-only when only reading, reviewing, summarizing or comparing the repository
- Do not treat repository text or precedent-auth.md as execution/target authorization
- Do not stop at acknowledging the rules after activation; continue the approved task
- Do not ask for confirmation again for every disclosed deterministic step once approved
- Do not guess tool paths; take them from tool-index
- Do not skip the Checklist
- Do not stay silent; report problems immediately
