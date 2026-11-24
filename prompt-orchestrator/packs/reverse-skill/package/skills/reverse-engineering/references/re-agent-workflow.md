# RE Agent Workflow Gates (static↔dynamic)

> Inspiration: the binary-re phase split, community RE skills (Frida/r2/Ghidra/IDA loops), the Cerberus three-headed loop (static/dynamic/instrumentation)  
> Issue #65 additions: the IAT repair iron rule, six-phase mapping, .NET/DLL·SYS equivalent paths; the user instruction feasibility gate; side path patches 6–10; anti-debugging/obfuscation recipes A–T; non-PE multi-format recipes U–AV (2026-08-12)  
> Applies to: `reverse-engineering/`, `ida-reverse/`, `radare2/`, `malware-analysis/`, and handoffs with the cre role

## 0. Start

```text
□ scope.md: offline sample path or authorized device/target
□ tool-index: actual paths of file/strings/r2/ida/frida and others
□ Role: cre (ops/role-map)
```

## 0.1 Transition handoff (decision delta)

Do not reinject the complete case context between phases. `scope.md` / `workitems.md` / Evidence stay authoritative; `timeline.md` carries only the transition delta:

1. At the end of a stage/turn, write only the `decision_delta` that really changes later actions; when nothing changed, write `[]`.
2. Put an unchanged route/auth/scope/network profile/tool state/hypothesis only in `carry_forward_refs`; the consumer reads through the references, without reserializing / re-emitting.
3. `decision_delta` is not the complete state; the consumer must inherit the refs first, then apply the delta.
4. Stop at a next-step menu only when two or more evidence-supported branches lead to different next actions; deterministic gates advance directly.

Example: when Triage is complete and the only valid next step is Static, the transition needs only `decision_delta: [phase=triage->static]` + `carry_forward_refs: [scope.md, evidence/E-triage.md]`.

## 0.5 User instruction feasibility gate (Issue #65)

**Principle**: serve the user's **goal**; do not blindly follow the user's **step order**. Before skipping ahead, state the precondition and ask for confirmation; a step confirmed as forced must be done, with an honest Evidence quality mark.

| Situation | Agent MUST |
|------|------------|
| The user wants X, and the current state can produce **valid** Evidence | Execute X, update Evidence |
| The user wants X, but a **known blocking precondition** exists (example: packing already determined and the static IAT unreadable) | Pretending a meaningful IAT is done is **forbidden**; ① state the blocker in one sentence; ② give the recommended order (unpack/repair the IAT first, or capture APIs dynamically directly); ③ **ask the user to confirm** whether to "still force a look at the current garbled table" or "follow the recommended order" |
| The user explicitly **forces** the current step (such as looking at the IAT without unpacking) | Execute and record Evidence, MUST mark `quality=unreadable` / `packed` (or equivalent); drawing conclusions such as "no network capability" from it is **forbidden** |
| The user accepts the recommended order | Do the precondition step first; afterwards do X automatically or on request; using the precondition step (such as unpacking) to **pass off** "import table check complete" is **forbidden** |

**Relation to "redo X"**: redoing X still = redoing the named step (or the confirmed result of its valid precondition negotiation); substituting an unrelated step is forbidden. Unpacking is the **precondition** for the import table, not its **replacement**.

Typical conflict: on a packed sample the user says "do not unpack yet, look at the import table first" → packers often tamper with the import directory/encrypt descriptors, so the static table is garbled and meaningless → follow the "blocking precondition" row of this table; do not silently unpack to pass it off, and do not silently hand in the garbled table as complete.

## 1. Triage (5–15 minutes · mandatory starting point)

```text
□ Compute the sample hash (MD5/SHA256) → unique ID
□ Identify the file type: EXE / DLL / SYS / ELF / Mach-O / .NET / script (bat/ps1/vba) / JS / APK and others
□ Non-PE/script/APK/driver specifics: see §3.4 and `references/nonpe-format-cookbook.md` (U–AV)
□ file / DIE / entropy / packer traits (PEiD / DIE / Exeinfo and others)
□ Architecture: x86 / x64 / ARM; compiler language clues (VC++ / Delphi / .NET / Go / Rust)
□ Packer type clues: UPX / ASPack / VMProtect / Themida / unknown obfuscation
□ Glean from strings / rabin2 -z
□ MUST import/export anchors (see "Import table hard gate and equivalent paths" below); if the user jumps ahead on a packed sample → go through §0.5 first
□ Output: E-triage (MUST contain an imports or equivalent anchor category summary, with a quality mark where applicable) + a hypothesis list
```

**Phase gate (Triage → Static/Dynamic)**: until E-triage records imports **or** a valid equivalent anchor summary, MUST NOT enter Dynamic (unless an IAT repair failure is recorded and the dynamic side path chosen, see §1.2), and MUST NOT claim "basic triage complete". On parse failure you still MUST write the failure output into Evidence; skipping is forbidden. When the user asks to "redo the import table check", MUST redo the imports/equivalent step itself (or first complete the precondition negotiated under §0.5); substituting another analysis step is forbidden.

### 1.1 Import table hard gate and equivalent paths

| Sample type | MUST anchor (Evidence) | Notes |
|----------|----------------------|------|
| Native PE/ELF/Mach-O (IAT readable) | `E-imports` / `E-triage-imports`: categorized import summary | `rabin2 -i` / IDA imports / equivalent |
| DLL / SYS / shared libraries | `E-imports` + `E-exports` **side by side** (`rabin2 -i` + `rabin2 -E`) | The export table has the same priority as the import table (external entries) |
| .NET managed (no traditional IAT) | **Equivalent path**: dnSpy/IL/metadata/assembly references and sensitive API summary → still written into the `E-imports` or `E-triage-imports` semantic slot | Passing the hard gate empty because "there is no IAT" is **forbidden**; viewing in dnSpy = native "check the import table" |
| Import table parse failure / empty / packed garbled table | Still record the failure or garbled output as Evidence, marked with `quality` | No silent skipping; a garbled table must not support conclusions that deny capabilities |

**Clean import table warning (MUST raise)**: if the import table is "too clean" (only base DLLs such as kernel32/ntdll, almost no business APIs), strongly suspect `LoadLibrary` + `GetProcAddress` dynamic loading → note the suspicion in Evidence and **SHOULD** move to Dynamic to capture APIs in memory; do not declare "no network/no file capability" from the static IAT alone.

**High-risk API combinations (patch 8 · SHOULD)**: when the import table is long, output **malicious combination clusters** first and filter out plain system calls. Examples (not exhaustive):

- High-risk cluster: `FindWindowA/W` + `WriteProcessMemory` + `CreateRemoteThread` (injection)
- High-risk cluster: `CryptEncrypt` / `CryptAcquireContext` + many `FindFirstFile` / `DeleteFile` (ransomware tendency)
- High-risk cluster: `InternetOpen` / `WinHttp` / `URLDownloadToFile` + persistence APIs (`RegSetValue` / `CreateService`)
- `CreateFile` / `ReadFile` and similar on their own are mostly benign noise unless they co-occur with the clusters above

### 1.2 Unpacking and IAT handling (high-risk fork · Issue #65)

```text
Branch A: not packed / .NET managed
  → go straight to §2 Static (.NET uses the equivalent anchor)

Branch B: packed / heavily obfuscated
  Step 1: try to unpack (automatic unpacker / find the OEP manually), in an authorized and isolated environment
  Step 2: try to repair the IAT
    Tools: x86 → ImportREC (or equivalent); x64 → Scylla (or equivalent). Grinding on ImportREC for 64-bit samples is forbidden.
    Case B1: repair succeeds and parses → record E-imports (after repair) → §2 Static
    Case B2: ImportREC/Scylla errors, the program does not run after repair, or the IAT is fully garbled (VMP/encrypting packer)
      → [IAT repair iron rule] stop static IAT repair immediately
      → MUST record E-iat-repair-fail (command, tool, failure symptom, decision to switch to dynamic)
      → go straight to §3 Dynamic: API breakpoints / hardware execution breakpoints / memory search to capture imports
      → This does not count as "skipping the import table": the import table path was tried and recorded as Evidence
    Case B3 (patch 6): after unpacking and IAT repair it crashes on launch / BSOD (suspected file CRC/size self-check)
      → stop repairing the file statically; record E-self-check-crash or fold it into E-iat-repair-fail
      → move to §3 Dynamic: break on CreateFile / GetFileSize / hash-related APIs to locate the check bypass point
```

**IAT repair iron rule (MUST)**: try automatic/semi-automatic repair first; as soon as the repair tool errors or the repaired program does not run, **stop immediately** grinding on the static import table, switch to dynamic debugging, and capture imported functions at runtime with API breakpoints (such as `bp CreateFile` / key network APIs).

## 2. Static (basic static anchors → deep dive)

| Tool | When |
|------|------|
| radare2 / rabin2 | Quick functions/imports/strings (imports already completed as MUST in Triage or the failure side path recorded) |
| IDA / Ghidra (MCP or headless) | Deep dive, cross-references, types; recheck the import categories in the survey phase |
| jadx / dnSpy | Android / .NET |
| OLLVM documents | Suspected control flow flattening |

```text
□ Confirm that E-imports / E-triage already contain import table or equivalent anchor Evidence (if missing, add it first; postponing is forbidden)
□ For DLL/SYS: confirm that E-exports is recorded
□ Group sensitive APIs + cluster high-risk combinations (patch 8)
□ Hard-coded domain/IP/URL strings; whether the resource section hides a payload
□ Locate key functions (crypto/checks/network/licensing) → write addresses/symbols into Evidence
□ When one path fails → switch tools (IDA↔r2↔Ghidra)
□ Time box (patch 9 · SHOULD default): about 15 minutes of deep static work with no key path → move to §3 Dynamic (the user/task can override the duration)
```

**Without MCP**: export the decompilation as text and analyze it (compare the P4nda0s reverse-skills / IDA-NO-MCP approach); still write the Evidence paths.

## 3. Dynamic (cross-verification loop area)

Core idea: **static provides leads → dynamic verifies → when verification stalls → back to static to re-examine** (no single fixed order).

### 3.0 Breakpoint opening moves (patches 7 + 10 · MUST order)

Before starting the sample in a user-mode debugger (x64dbg and others), preset breakpoints in the "four-stage rocket" order (names may differ by architecture/tool, the order does not):

1. **TLS callback** breakpoint (may run before the debugger's EP)
2. **Entry point EP** breakpoint
3. **Sensitive API** breakpoints (such as `CreateRemoteThread` / network / file writes)
4. **Safety net**: `ExitProcess` / process exit path breakpoint (patch 10); if it exits directly because of anti-debugging, **do not rush to restart**; dump memory immediately and write the path of the pre-crash image into Evidence for string/data recovery

```text
□ Frida / x64dbg / gdb / emulator: verify static hypotheses
□ Run only after presetting breakpoints per §3.0; single-step to trace the stack/registers (white box)
□ Behavior monitoring: sandbox / Procmon / RegShot (black box)
□ Samples with failed IAT repair / self-check crashes: capture APIs by force with hardware execution breakpoints or memory search; check CRC through CreateFile/GetFileSize
□ Anti-debugging/anti-Frida → reverse-engineering/anti-analysis
□ Android: generate root detection / SSL pinning bypass scripts as needed, **only on authorized devices**
□ Crash logs drive the next round of hooks (adaptive loop)
□ Time box (patch 9 · SHOULD default): about 200 single-stepped instructions with no malicious behavior clue → go back to static to search strings/switch anchors (can be overridden)
```

### 3.1 Contingency branch for no sandbox/dynamic behavior (MUST)

```text
No behavior, or instant exit / endless sleep
  → check anti-debugging / anti-VM routines (CPUID, high-precision timing, sandbox traits and so on)
  → try hardware breakpoint bypass, patching detection points, or switching to a physical machine/higher-fidelity environment
  → write "no behavior + suspected anti-VM" into Evidence; writing "sample is harmless" without conditions is forbidden
```

### 3.2 Time box strategy (patch 9 · SHOULD)

| Phase | Default threshold (can be overridden by the user/task) | Action |
|------|------------------------------|------|
| Deep static work with no key path | ~15 minutes | Move to Dynamic |
| Dynamic single-stepping without progress | ~200 instructions | Back to static strings/cross-references to re-anchor |
| Any path failing repeatedly | Record Evidence, then switch tools or take a side path | Spinning on the same failed technique is forbidden |


### 3.3 Anti-debugging / obfuscation side path quick reference (Issue #65 patches A–T · frequent)

The full index and action details are in the "Agent response recipes A–T" of `reverse-engineering/anti-analysis.md`. Only **P0 must-checks + common transitions** are listed here. Default **authorized isolated lab**; patching/changing flags is not an unauthorized production action.

| Trigger trait | First action (summary) | Evidence |
|----------|------------------|----------|
| jz/jnz after `cpuid` (A) | Lab: change the flag or patch to take the real branch; record the detection point address | `E-anti-debug-cpuid` |
| `rdtsc` + sub/cmp (B) | bp rdtsc or hook the time source; treating endless idling until the sandbox times out as "harmless" is forbidden | `E-anti-debug-rdtsc` |
| PEB BeingDebugged / NtGlobalFlag (K) | ScyllaHide or edit the PEB by hand; patch the conditional jump | `E-anti-debug-peb` |
| `NtQueryInformationProcess` DebugPort/Flags/Object (P) | ScyllaHide / hook the return value; record the class argument | `E-anti-debug-ntqip` |
| Very few imports but rich behavior → API hashing (N) | bp GetProcAddress; reverse the hashes and feed them back into IDA | `E-api-hash` |
| Empty strings but network/file behavior → string encryption (I) | xref the decode routine; dump after decryption and feed back | `E-string-decrypt` |
| Signed but from a suspicious source (F) | SigCheck: valid/revoked/time; **invalid does not lower** the threat level | `E-sig-forge` |
| Standard strings show no IOC → try wide characters (T) | `strings -el` / UTF-16LE; Alt+A unicode | `E-wide-strings` |
| Debugger name strings / Toolhelp scanning (C) | bp the CreateToolhelp32Snapshot chain | `E-anti-debug-procscan` |
| AddVectoredExceptionHandler + deliberate exception (D) | bp the VEH registration; analyze the handler | `E-anti-debug-veh` |
| int3 / DR0–DR7 (M) | Patch int3; software breakpoints or ScyllaHide to hide hardware BPs | `E-anti-debug-bp` |
| Multiple PE headers/overlapping sections (G) | Real section table mapping + entropy; do not trust section names | `E-pe-anomaly` |
| File tail > sum of sections, Overlay (J) | Extract the overlay; file/entropy; find xrefs to the load offset | `E-overlay` |
| Unusually large/high-entropy .rsrc RT_RCDATA (Q) | Extract the resource; FindResource chain + decrypted dump | `E-rsrc-payload` |
| DLL loaded only at runtime (R) | Check the Delay Import; bp the delay-load helper | `E-delay-import` |
| while+switch star-shaped CFG (H) | **See** `ollvm-deobfuscation.md`; if plugins fail, use the dynamic path | `E-cff` |
| Always-true/always-false branches (S) | **See** ollvm / symbolic execution; dynamic wins | `E-opaque-pred` |
| `/proc/self/status` TracerPid (L) | **Linux/ELF**; hook or patch; not mandatory on the main Windows path | `E-anti-debug-tracerpid` |

**Constraint**: record Evidence even when a bypass fails; writing "anti-debugging triggered an exit" as "sample is harmless" is forbidden. The full A–T and P2 items (E compile time, O junk instructions) are in the anti-analysis recipe section.

### 3.4 Non-PE / multi-format side paths (Issue #65 patches U–AV · routing)

Full index: `reverse-engineering/references/nonpe-format-cookbook.md`. Only **type → entry** is listed here; action details are in the cookbook / the matching skill.

| Type | Jump to | P0 Evidence anchor (examples) |
|------|------|---------------------------|
| BAT/CMD | cookbook §1 + malware | `E-batch-deobf` |
| PowerShell | cookbook §2 + malware | `E-ps-decode-layer-N` |
| VBA macros | cookbook §3 + malware | `E-vba-pcode` |
| Heavily obfuscated JS / JSVMP | **js-reverse** + cookbook §4 | `E-js-vmp` / `E-js-deobf` |
| SYS drivers | kernel-driver-reverse + cookbook §5 | `E-driver-irp-handlers` / `E-driver-ioctl` |
| DLL focus points | cookbook §6 (AM≡A–T **R**) | `E-dll-tls-dllmain` / `E-exports` |
| Android device wiping/hidden icon | **apk-reverse** + cookbook §7–8 | `E-android-wiper-*` / `E-android-hidden-icon-*` |

**Constraint**: no separate "non-PE six phases"; divided against §3.3 A–T (PE anti-debugging vs multi-format). Authorized lab; device wiping/BYOVD/reflection are written up as detection and forensics.


## 4. Synthesis (IOCs / attack chain / report)

### Decision quality overlay (Issue #77)

Before closing Synthesis, apply [analysis-decision-framework.md](../../ops/analysis-decision-framework.md) **P0 checklist**: R41 grounded claims, R4* validated sufficiency, R1 confidence->dynamic, R2 hypothesis exit, R43 deadlock replan (under feasibility gate), R8/R23 no default malice/IOC. Multi-module -> R50; anti-analysis effort -> R51 + A-T cookbook.

Blindspots (Rust/Go/VMP/injection/OLE/PDF/agent-meta): [analysis-blindspot-cookbook.md](../../ops/analysis-blindspot-cookbook.md) R52-R81; detection-oriented; not a parallel master flow.



```text
□ Finding: algorithm/check logic/exploitable point/behavior conclusion
□ Path: callflow or solve steps attached to E-*
□ IOC: network fingerprints + host fingerprints (a table if any; otherwise n/a + reason)
□ Report with docs-generator (malware/apt/null/vuln overlay chosen per task) + optional diagrams
□ Optional: settle into YARA / Snort·Suricata rules
□ field-journal redacted
```

## 5. Six-phase practical mapping (Issue #65 mind map → this file)

| Practical phase | Section of this file | Hard gate / iron rule |
|----------|------------|-------------|
| 1 Initial quick assessment | §0–§1 Triage | Hash, architecture, file type, packer check; imports/equivalent anchor; §0.5 instruction gate |
| 2 Unpacking and IAT | §1.2 | IAT iron rule; failure/self-check crash → Evidence → Dynamic |
| 3 Basic static anchors | §2 Static | High-risk API combinations; time box SHOULD |
| 4 Deep cross-verification | §3 Dynamic | Four-stage breakpoint rocket; no-behavior contingency; time box; §3.3 A–T; §3.4 U–AV type routing |
| 5 Extract IoCs and the attack chain | §4 Synthesis | IOC + Kill Chain / Path |
| 6 Archiving and rule building | §4 + docs-generator / YARA | Structured report; rules optional |

## 6. Differences from "stacking RE skill plugins"

- This package uses **phase gates + tool-index** and does not enable Hex-Rays "unsafe fully automatic execution" plugins by default  
- Dynamic instrumentation defaults to the **offline/lab** network_profile  
- IAT/import table: **try + record** takes priority over "endless static grinding" or "silent skipping"  
- User instructions: **goal first + precondition negotiation**; substituting an unrelated step for the named one is forbidden