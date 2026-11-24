---
name: reverse-skill-router
description: Routes reverse engineering, exploitation, penetration testing, malware, mobile, firmware, browser automation, documentation, and security tasks to the appropriate specialist skill. Use when a task spans modules or the correct reverse-skill entrypoint is unclear.
---
# Reverse Engineering Skills Master Control

This directory collects reverse engineering skill modules. Each subdirectory is an independent module whose `SKILL.md` describes its scenarios, toolchain and workflow.

## CRITICAL: routing execution contract (execute immediately)

After reading this file, replying only "read" or "understood" is not allowed. Execute in order:

1. `NOW`: run the platform-native router (Windows `scripts/master-route.ps1`; Linux/macOS/Kali `scripts/master-route.sh`) and take PRIMARY from `config/routing.json`; for hard cases, read the three-axis appendix in `routing.md`.
2. `NOW`: run the platform-native `case-init` to create `work/<case>/scope.md` of the current analysis project; **until auth is granted, ACT against targets is forbidden**. A local offline sample uses the `offline-sample` preset + an explicit sample; Force must not bypass the hard gate.
3. `ACT`: open the PRIMARY `SKILL.md` right away and execute ACTION REQUIRED.
4. `NEXT`: tool paths come only from `tool-index.md`; for a missing tool, run the platform-native bootstrap (manifest only).
5. Conclusions use Evidence→Finding→Path. Reports and journals are SHOULD, unless the user wants a deliverable.

**Identity**: see `ops/IDENTITY.md` (lightweight routing package + tool bootstrap + journal; **not** a Z3r0-style platform).

If routing cannot hit, first supplement the methodology through web search and propose a new skill; forcing the task into a mismatched module is forbidden.

## Instruction semantic levels (RFC 2119)

- `MUST`: must be executed; a violation fails the task.
- `MUST NOT`: forbidden; a violation is a security violation.
- `SHOULD`: should be done in principle; skipping it requires a stated reason.
- `MAY`: optional action.
## Current modules

| Module | Directory | Scenarios |
|------|------|---------|
| **General reverse engineering** | `reverse-engineering/` | GDB / Frida / angr / Unicorn / Qiling / anti-analysis countermeasures / reverse engineering across languages and platforms / CTF pattern library |
| **APK reverse engineering** | `apk-reverse/` | Android APK unpacking, jadx decompilation, smali modification, Frida hooks, repackaging, signing and installing |
| **.NET / C# reverse engineering** | `dotnet-reverse/` | Managed PE reverse engineering, dnSpyEx + de4dot deobfuscation (ConfuserEx/SmartAssembly/Babel), IL patching, Sharp* red team tool analysis, dnSpy MCP integration |
| **IDA Pro reverse engineering** | `ida-reverse/` | IDA Pro MCP HTTP server (72 tools): decompilation, disassembly, data flow tracing, cross-references |
| **Frontend JS reverse engineering** | `js-reverse/` | Browser-side signature location, encrypted parameter analysis, runtime sampling, Node environment patching and reproduction; prefer the existing `js-reverse_*` tools, and connect jshookmcp when a stronger browser/CDP/Hook surface is needed, but only after that MCP server is downloaded, registered and enabled |
| **radare2 analysis** | `radare2/` | CLI binary recon, disassembly, patching: r2 / rabin2 / rasm2 / radiff2 |
| **CTF entry** | `ctf-sandbox/` | Single PRIMARY; downstream stays in the sidecar `../CTF-Sandbox-Orchestrator/` |
| **Technical documentation** | `docs-generator/` | Generates reverse engineering reports, pentest reports, CTF writeups and signature reverse engineering reports after a task |
| **Evidence graph review** | `case-review/` | Validates scope, Evidence→Finding→Path traceability, workitems, timeline and artifact hashes |
| **Browser and desktop automation** | `browser-automation/` | Browser operation (Playwright) + Windows desktop app operation (OpenReverse UIA/CUA) + network observation |
| **Cross-version symbol migration** | `binary-diff/` | Migrate old symbols to a new version, infer without a PDB, migrate function names in bulk after a program update |
| **N-day patch diff to exploit** | `patch-diff-exploit/` | Locate the vulnerability from a vendor patch, write a PoC, weaponize an N-day (split with binary-diff: this skill leans to the attack side) |
| **RE to exploit chain** | `pwn-chain/` | From reverse engineering to a working exploit: stack/heap/kernel pwn, pwntools, libc-database, stabilization from CTF to real remote targets |
| **Firmware pentest chain** | `firmware-pentest/` | The nine OWASP FSTM stages: extraction→EMBA automation→Firmadyne/QEMU emulation→AFL++ fuzzing→exploitation on real devices |
| **EDR bypass reverse engineering** | `edr-bypass-re/` | Red team scenarios: reverse-engineer EDR hook tables/ETW/AMSI → direct syscall / Hell's Gate / hardware breakpoints / call stack spoofing |
| **Pentest toolchain** | `pentest-tools/` | 20+ pentest tools such as Nmap/Nuclei/SQLMap/FFUF/Hashcat/Pentest Swarm, exposed to AI through MCP |
| **Diagram generation** | `diagram-generator/` | Generates Mermaid/Graphviz/PlantUML diagrams from natural language (attack path diagrams, data flow diagrams, architecture diagrams, state machines) |
| **Attack chain orchestration** | `attack-chain/` | Overall command for multi-stage attack path planning and execution; cross-stage tasks such as a complete pentest, an HW drill, or going from the internet all the way to the domain controller start here |
| **LLM/AI security testing** | `llm-security/` | OWASP LLM + ASI Top 10: prompt injection, tool abuse, memory poisoning, agent hijacking, system prompt extraction, **agent obedience engineering** |
| **API security testing** | `api-security/` | Every protocol of REST/GraphQL/WebSocket: BOLA/IDOR, JWT/OAuth attacks, 10-phase methodology |
| **Supply chain security** | `supply-chain-security/` | SBOM/SCA/CI-CD pipelines: dependency scanning, container security, build integrity, vulnerability reachability verification |
| **Mobile reverse engineering** | `mobile-reverse/` | Android + iOS: Frida/Objection dynamic instrumentation, SSL pinning/root/jailbreak detection bypass, OWASP MASTG |
| **Malware analysis** | `malware-analysis/` | Six-phase sample analysis, YARA/Sigma, anti-analysis detection, sandbox orchestration |
| **DSL virtual machine reverse engineering** | `reverse-engineering/dsl-vm-reverse/` | JS custom instruction set VMs (IIFE + switch-case opcode); risk control and CAPTCHA engines |
| **Operations contract ops** | `ops/` | Scope / evidence chain / roles / timeline / identity / skill supply chain security |
| **Community skill comparison** | `references/community-security-skills.md` | Index of external security skills and rules for borrowing ideas (no blind installs) |
| **Skill supply chain** | `ops/skill-supply-chain.md` | Install latch for external skills and MCPs (condensed AST10) |
| **RE phase latch** | `reverse-engineering/references/re-agent-workflow.md` | triage→static→dynamic→synthesis |
| **Authorized recon pipeline** | `pentest-tools/references/recon-pipeline.md` | scope gate + a hit is not a verification |
| **Protocol reverse engineering** | `protocol-reverse/` | Custom binary protocols / Protobuf / gRPC / PCAP frame layout |
| **Ghidra reverse engineering** | `ghidra-reverse/` | Open-source decompilation, headless, Ghidra MCP (the main entry without IDA) |
| **Binary Ninja reverse engineering** | `binary-ninja-reverse/` | HLIL/MLIL/LLIL, Python API, and optional community MCP/localhost HTTP integration |
| **Cloud / containers / K8s** | `cloud-k8s/` | IMDS/IAM, container escape surface, Kubernetes RBAC |
| **Windows / AD** | `windows-ad/` | Kerberos, AD CS, BloodHound, relays and domain paths |
| **Digital forensics** | `digital-forensics/` | Memory and disk timelines, PCAP tracing, IR preservation |
| **Code audit / SAST** | `code-audit/` | Semgrep/CodeQL, white box, dangerous API and authorization review |
| **Threat intelligence / OSINT** | `threat-intelligence/` | Public-source IOC enrichment, activity correlation, independent verification and intelligence handoff |
| **Threat hunting** | `threat-hunting/` | Hypothesis-driven hunting, Sigma detection engineering, blue team validation |
| **OT / ICS industrial control** | `ot-ics/` | Purdue zones, PLC/SCADA, passive-first assessment |
| **Wi-Fi / wireless** | `wifi-wireless/` | Authorized wireless assessment, handshake/PMKID, lab rules |
| **Browser extension reverse engineering** | `browser-extension-reverse/` | Chrome/Firefox extensions, MV3 workers, permission surface |
| **macOS / Mach-O** | `macos-reverse/` | Signing, ObjC/Swift, LaunchAgent, macOS samples |
| **Thick client** | `thick-client/` | Desktop client/server, local storage, IPC, update channels |
| **Go / Rust reverse engineering** | `go-rust-reverse/` | Stripped Go/Rust, pclntab, panic strings |
| **Hardware debug interfaces** | `hardware-security/` | UART/JTAG/SWD, read-only extraction, firmware handoff |
| **Database security** | `database-security/` | MySQL/PG/MSSQL/Mongo/Redis exposure and configuration |
| **Email security** | `email-security/` | Phishing teardown, SPF/DKIM/DMARC, BEC |
| **Federated identity** | `identity-federation/` | SAML/OIDC/OAuth SSO flows and misconfigurations |
| **RF / SDR** | `radio-sdr/` | Authorized RF research, receive-only by default |

## Unified entry

For reverse engineering, CTF, packet capture, frontend signing, APK modification and binary analysis tasks, enter in this order:

1. Platform-native router (Windows `scripts/master-route.ps1`; Linux/macOS/Kali `scripts/master-route.sh`) → PRIMARY (`config/routing.json`)
2. Platform-native `case-init` → `scope.md`
3. Open the PRIMARY `SKILL.md`
4. For hard cases read `routing.md`; for local paths read `tool-index.md`

## Working approach

These modules can be combined as needed:

1. **Get a target** → check the file type first and choose the matching analysis tool
2. **Quick wins** → strings / rabin2 -z / ltrace for direct leads
3. **Deep analysis** → decompilation needs IDA; dynamic hooking needs Frida; symbolic execution needs angr
4. **When one path fails, take another** → if static analysis fails go dynamic; if the Java layer fails look at the so; if page observation is not enough, set breakpoints

## Next-Step Menu Pattern

Only at a **genuine decision boundary** (two or more materially different, evidence-supported branches where the user's choice changes the next action) does a sub-skill `MUST` offer 3-6 numbered options. If a gate or the evidence alone decides the next step, it `MUST` continue directly and record only `decision_delta` + `carry_forward_refs` per `ops/timeline-workitem.md`; it `MUST NOT` re-output unchanged route/scope/auth/context just to produce a menu.

Format requirements:
- Number each option (range 1-6)
- Each option describes one concrete executable action (not an abstract direction)
- Include at least one "export a report / write a writeup" option
- Include at least one "keep analyzing deeper" or "try another method" option
- Include a "stop / pause / ask something else" exit when needed

Example:
```
## Suggested next steps (pick a number)

1. Run a deep decompilation of sub_140001000 and recover the algorithm
2. Verify the parameter hypothesis with a Frida dynamic hook
3. Export the functions named so far and generate a symbol migration YAML
4. Generate the analysis report for the current phase
5. Switch to radare2 for a lightweight comparative recon
6. Pause; I want to confirm the earlier evidence first
```

## The directory grows dynamically

This directory keeps growing. When you find a new subdirectory, read its `SKILL.md` to learn its purpose quickly.

When adding a skill, follow the standard process in `CONTRIBUTING.md` so that:
- The routing matrix dispatches correctly
- The bootstrap system completes dependencies automatically
- tool-index reflects the state of the new tool

## Related resources

- This machine also has the **anything-analyzer** MCP server (port 23816), which provides browser automation, HTTP capture and AI analysis
- `tool-index.md` records whether local reverse engineering tools are available, their actual paths, versions and script references
- The `Readme.md` at the package root provides general install and integration instructions for Claude Code, Codex CLI and other coding AI clients

## On-demand bootstrap

When a workflow finds a missing tool, do not fail outright. Call the platform-native bootstrap:

Windows:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-root>\scripts\bootstrap-reverse.ps1" -Capability @('tool-name') -StartServices
```

Linux / macOS:
```bash
bash <skill-root>/scripts/bootstrap-reverse.sh tool-name --start-services
```

Kali:
```bash
bash <package-root>/kali/scripts/bootstrap-reverse.sh tool-name --start-services
```

Supported capabilities (per `scripts/bootstrap-manifest.json`): jadx, apktool, jeb-pro, binaryninja, frida, frida-ps, idalib-mcp, reqable-mcp, jshookmcp, xquik-mcp, anything-analyzer, idapro, r2, rabin2, adb, agent-browser, ghidra-mcp, seclists, proxycat, burpsuite-mcp, nmap, pentestswarm, binwalk, yara, pwntools, bkcrack

> JEB Pro is registered as a **manual licensed install** capability: bootstrap only prints guidance and never downloads or circumvents the commercial license. Reqable MCP registers only the pinned official runtime; the user still installs the Reqable desktop client.
>
> Tools not registered in the manifest (such as unblob/EMBA) `MUST` use manual install steps in the skill documentation; pretending they can be bootstrapped is forbidden.

After bootstrap completes, `tool-index` refreshes automatically.

## Operation precedent library (Precedent Files)

Before any reverse engineering or pentest operation, you MUST read in order:

| Order | File | When to read |
|------|------|--------|
| **#1** | `ops/scope-contract.md` + `case-init.ps1` | Executable authorization gate. `precedent-auth.md` does not write granted |
| **#2** | `field-journal/precedent-reverse.md` or `precedent-pentest.md` | On demand: load only when the AI hesitates |

**#1 first, #2 lazy-loaded.**

## Automatic evolution

After each reverse engineering or pentest task, write the experience back to the `field-journal/` directory. See the "Mandatory post-task checklist" in `RULES.md`.

- Template: `field-journal/_template.md`
- Index: `field-journal/_index.md`
- Precedents: `field-journal/precedent-auth.md` → `precedent-reverse.md` → `precedent-pentest.md`
- Before starting a new task, check the index and precedents and reuse existing experience

## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I complete three-axis routing (target type + user intent + toolchain)?
- [ ] Did I read the SKILL.md of the target skill after routing succeeded?
- [ ] When routing missed, did I propose a new skill instead of forcing a match?
- [ ] Did I use real tool paths based on `tool-index`?
