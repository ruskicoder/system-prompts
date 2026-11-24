---
name: edr-bypass-re
description: |
  Reverse the defender's implementation → targeted red team bypass. First reverse the hook tables, ETW providers and AMSI implementation of the EDR / Defender / AV,
  then write targeted unhook / indirect syscall / ETW patch / call stack spoof. Maps to MITRE ATT&CK T1562 defense evasion.
  Trigger keywords: EDR bypass, AV bypass, AV evasion, unhook, direct syscall, indirect syscall, Hell's Gate, Halo's Gate,
  Tartarus Gate, ETW patch, AMSI patch, call stack spoofing, hardware breakpoint Blindside, MITRE T1562,
  ntdll unhook, kernel callback, CrowdStrike bypass, Defender bypass, Sentinel One bypass, Elastic Defend,
  Sysmon evasion, PPID spoof, Sleep mask, Process Hollowing, Reflective DLL.
---

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

# EDR Bypass: From Reversing the Defender's Implementation to Red Team Bypass

> Only for authorized red team / adversary exercises / testing your own products; use against unauthorized targets is forbidden.

## Scope

Use this skill when a red team / adversary emulation delivers an implant to an authorized target host and must evade a modern EDR.

1. **Red team / Purple team / adversary exercise**: the client wants to assess the real detection capability of the SOC and EDR
2. **In-house implant / C2 framework development**: develop payloads for testing your own products that must bypass your own or the target EDR
3. **EDR product evaluation**: objectively evaluate an EDR's detection coverage once the compliance boundary is confirmed
4. **Windows-side breach in CTF / attack and defense exercises**: you need stable execution on a hardened host during the competition

**Not suitable for**:

- An AV vendor doing complete RE of its own product for a commercial client assessment report (seek formal vendor cooperation)
- AV evasion against unauthorized targets (illegal)
- AV evasion for ordinary viruses and trojans (this skill focuses on red team OPSEC and does not teach how to write malicious code)

### Division of work with other skills

| Scenario | What to use |
|------|--------|
| Full-chain attack and defense (from the internet to the domain controller) | `attack-chain/` |
| Internal lateral movement / AD attacks | `pentest-tools/network-attack-defense.md` |
| Delivering an implant past the EDR on one specific host | **This skill** |
| Static AV evasion only (obfuscation / packing) | `malware-analysis/` (reverse perspective) |

`attack-chain` covers the complete kill chain; this skill focuses only on **one adversary, the EDR**, its internals and targeted bypasses.

## Core principle

```text
The EDR's four main monitoring surfaces               Red team countermeasures
─────────────────────              ─────────────────────
User-mode ntdll hook       ◄──►   unhook (Peruns Fart / fresh ntdll)
                                  Indirect syscall / Hell's Gate
                                  hardware breakpoint Blindside

kernel callback         ◄──►   call stack spoof
(Ps/Cm/Ob families)                   Use a legitimate trigger chain (no direct bypass, combine with upstream stealth)

ETW telemetry           ◄──►   EtwEventWrite patch
(Microsoft-Windows-Threat-          NtTraceControl disables the provider
 Intelligence and others)                  AmsiContext synchronous handling

AMSI scan               ◄──►   AmsiScanBuffer patch (mov eax,0x80070057; ret)
(amsi.dll)                       hardware breakpoint bypass
                                  reflectively load a copy of amsi.dll
```

Key insights:

- **The EDR is not a black box**: key hooks / callbacks / providers can all be reversed with IDA + windbg
- **Bypass techniques must be combined**: an unhook alone does not solve ETW alerts, and an AMSI patch alone does not solve syscall hooks
- **Order matters**: ETW patch first → then AMSI patch → then unhook; in the wrong order the EDR receives the unhook alert first
- **Modern EDRs already treat ETW + kernel callbacks as the main battlefield**, so user-mode unhooking alone has long been insufficient

## Workflow

### Step 1: Identify the EDR on the target host

```powershell
# List common EDR / AV drivers
Get-Service | Where-Object {$_.Name -match 'CSAgent|SentinelAgent|elasticendpoint|esets|ekrn|MsMpEng|wdsvc|cyserver|sysmon|aswbidsagent'}

# List loaded minifilters
fltmc filters

# List registered kernel callbacks (needs windbg + kernel debugging / or PChunter / DRVHV)
# !object \Callback
# !pnpcallback / Process / Thread / Image
```

The EDR fingerprint table is at the top of `references/hook-survey.md`.

### Step 2: Extract the hook table from the EDR DLL

1. Attach to a process into which the EDR user-mode component is injected (any running process)
2. Dump the `.text` section of the current `ntdll.dll` in windbg
3. Diff it against the clean `C:\Windows\System32\ntdll.dll` on disk
4. Every mismatch is a hook point

Or use `pe-sieve` directly:

```powershell
pe-sieve64.exe /pid 1234 /shellc 3 /modules 3 /dir hooks_dump
```

See `references/hook-survey.md` for the detailed method.

### Step 3: Choose a combination of bypass techniques

| Defense point | Recommended bypass |
|--------|---------|
| ntdll inline hook | indirect syscall + dynamic SSN (Halo's Gate) |
| ETW-TI provider | EtwEventWrite head patch |
| AMSI (PowerShell / .NET) | AmsiScanBuffer patch or HWBP |
| kernel callback | call stack spoof + legit gadget |
| Sysmon ProcessCreate | PPID spoof + unbacked memory |

### Step 4: Implement in the implant

Code skeletons are in `references/unhook-techniques.md` and `references/telemetry-blinding.md`.

### Step 5: Local sandbox verification

```powershell
# Deploy a trial of the target EDR in an isolated environment (default Defender is enough to start)
# Enable Sysmon + olaf-config
sysmon64.exe -i sysmonconfig.xml

# Run the implant and check whether these alert sources fire:
#   - Defender AMSI
#   - ETW-TI
#   - Sysmon Event ID 1/7/8/10
#   - EDR console
```

### Step 6: Delivery

- Use a legitimate software directory as the file drop path
- PPID spoof to explorer.exe
- Combine with the initial access section in `attack-chain`

## Typical scenarios

### Scenario 1: deliver a cobalt-strike-alike beacon past Defender + Sysmon

```text
Target: Windows 11 Enterprise + Defender (cloud protection on) + Sysmon (olaf configuration)
Requirement: after landing, the beacon can call back without triggering any alert

Combination:
  1. Store the shellcode encrypted and decrypt it at runtime
  2. AMSI patch (if delivered through PowerShell)
  3. EtwEventWrite patch (removes ETW-TI)
  4. Indirect syscall + Halo's Gate (removes ntdll hook alerts)
  5. PPID spoof to explorer.exe
  6. Encrypt its own memory with Ekko / Foliage during sleep
```

### Scenario 2: EDR sleep mask on a landed low-privilege shell

```text
Precondition: a medium IL shell was obtained through phishing, and the EDR is monitoring
Risk: a long stay makes it easy for memory scans to find beacon signatures

Solution:
  1. Stop allocating new RWX memory
  2. Use Ekko during sleep:
       - WaitForSingleObjectEx + CreateTimerQueueTimer
       - In the timer, encrypt its own .text + wipe the stack to all zeros
  3. Restore with ROP on wake
  4. Combine with call stack spoof so RtlCaptureStackBackTrace cannot see the beacon address
```

## On-Demand Bootstrap

### Tool dependencies

| Tool | Purpose | Auto-installable |
|------|------|-----------|
| pe-sieve | Detect hooks / injection in a process | ✓ |
| API Monitor v2 | Observe API calls and hooks dynamically | Semi-automatic (manual download) |
| SysWhispers3 | Generate direct / indirect syscall stubs | ✓ (git clone + python) |
| Hell's Gate POC | Reference implementation of dynamic SSN resolution | ✓ (git clone) |
| windbg + IDA | Statically reverse EDR DLLs / kernel callbacks | ✗ (install yourself) |
| Sysmon + olaf config | Local verification environment | ✓ |

### Bootstrap commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "&lt;SKILL_ROOT&gt;\skills\scripts\bootstrap-reverse.ps1" -Capability @('pe-sieve','syswhispers3','sysmon') -StartServices
```

## Routing context

**Upstream entries**:

- `reverse-engineering/`: when you first need to understand the implementation of the EDR DLL / driver
- `attack-chain/`: decides at which kill chain phase this skill comes in

**Sibling links**:

- `pentest-tools/network-attack-defense.md`: how to link with this skill during internal lateral movement
- `malware-analysis/`: reverse perspective, how the detection side writes rules
- `field-journal/`: write back experience after each engagement

**Downstream deliverables**:

- When generating the report, cite MITRE ATT&CK **T1562 (Impair Defenses)**, T1562.001 (Disable or Modify Tools), T1562.006 (Indicator Blocking), T1055 (Process Injection), T1027 (Obfuscated Files or Information)

## Legal boundary statement

- Only for legally authorized red team / adversary exercises / testing your own products
- Written authorization is required before operating (SoW / test contract / SRC scope statement)
- Do not use against unauthorized targets or beyond the authorized scope
- Report high-risk issues to the client immediately and follow responsible disclosure
- Redact real target information in every report (placeholders for IP / host name / domain / credentials)

## References

- Detailed hook survey: `references/hook-survey.md`
- unhook / syscall techniques: `references/unhook-techniques.md`
- ETW / AMSI / anti-forensics: `references/telemetry-blinding.md`
- MITRE ATT&CK T1562: <https://attack.mitre.org/techniques/T1562/>


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
