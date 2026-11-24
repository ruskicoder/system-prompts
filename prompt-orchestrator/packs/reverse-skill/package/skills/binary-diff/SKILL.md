---
name: binary-diff
description: |
  Cross-version symbol migration and binary diffing. Use when you have symbols or reverse engineering results for an old version and need to migrate them to a new version quickly.
  When to use: derive symbols from an old version when a kernel lacks a PDB, migrate function names in bulk after a program update, locate new offsets quickly after an application update.
  Core method: structured diff comparison with an LLM, programmatic input and output, very low cost (200 functions ~1 yuan).
  Trigger keywords: symbol migration, bindiff, cross-version, missing PDB, function offset migration, symbol migration, binary diff, version comparison.
---

# Cross-Version Symbol Migration (Binary Diff)

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

## Scope

Use this skill when the task falls into one of these scenarios:

1. **Kernel/driver without a PDB**: you have symbols for an old ntoskrnl.exe, Microsoft has withdrawn the new PDB, and you need to derive addresses of non-exported functions in the new version from the old symbols
2. **Symbol migration after a program update**: you reversed a program before, the program has been updated, and you want to migrate the old results in bulk instead of reversing it again
3. **Protection mechanism update**: the old version has complete reverse engineering results and you need to locate the new offset of the same function in the new version quickly
4. **Any binary comparison with "old version has symbols + new version has none"**

### Division of work with other skills

| Scenario | What to use |
|------|--------|
| Reverse a binary from scratch | `ida-reverse/` or `radare2/` |
| Old results exist, migrate to the new version | **This skill** |
| Compare two completely different binaries | BinDiff / Diaphora (traditional tools) |

### Core advantage

Compared with traditional approaches:

| Approach | Cost for 200 functions | Time | Accuracy |
|------|--------------|------|--------|
| Manual comparison in two IDA windows | Free but exhausting | Hours | High |
| BinDiff automatic matching | Free | Fast | Medium (fails when the structure changes a lot) |
| Hand it all to an agent (CC/Codex) | 50-100 yuan | Slow | High |
| **This skill (LLM batch comparison)** | **~1 yuan** | **~10 seconds/function** | **High** |

## Core principle

```text
Old function (with symbols)          Same function in the new version (no symbols)
    ↓                              ↓
Export disassembly + pseudocode          Export disassembly + pseudocode
    ↓                              ↓
    └──────── LLM structured comparison ────────┘
                    ↓
         Output YAML (symbol mapping table)
                    ↓
         Parse programmatically → apply in bulk to the new IDB
```

Key points:
- The prompt is a fixed template filled programmatically
- The input and output formats are fixed and parsed programmatically
- The LLM only handles the step "look at two pieces of code and find the correspondence"
- Time cost and token cost are very low

## Prompt template

### Standard comparison prompt

```text
I have disassembly outputs and procedure code of the same function.

This is the function for reference:

**Disassembly for Reference**
```c
{disasm_for_reference}
```

**Procedure code for Reference**
```c
{procedure_for_reference}
```

This is the function you need to reverse-engineering:

**Disassembly to reverse-engineering**
```c
{disasm_code}
```

**Procedure code to reverse-engineering**
```c
{procedure}
```

What you need to do is to collect all references to "{symbol_name_list}" in the function you need to reverse-engineering and output those references as YAML.

Example:
```yaml
found_vcall: # This is for indirect call to virtual function or virtual function pointer fetching.
  - insn_va: '0x180777700' # Always be the instruction with displacement offset
    insn_disasm: call [rax+68h] # Always be the instruction with displacement offset
    vfunc_offset: '0x68'
    func_name: ILoopMode_OnLoopActivate
  - insn_va: '0x180777778' # Always be the instruction with displacement offset
    insn_disasm: mov rax, [rax+80h] # Always be the instruction with displacement offset
    vfunc_offset: '0x80'
    func_name: INetworkMessages_GetNetworkGroupCount

found_call: # This is for direct call to non-virtual regular function.
  - insn_va: '0x180888800'
    insn_disasm: call sub_180999900
    func_name: CLoopMode_RegisterEventMapInternal
  - insn_va: '0x180888880'
    insn_disasm: call sub_180555500
    func_name: CLoopMode_SetSystemState

found_funcptr: # This is for non-virtual regular function pointer.
  - insn_va: '0x180666600' # Must load/reference the function pointer target address
    insn_disasm: lea rdx, sub_15BC910 # Must load/reference the function pointer target address
    funcptr_name: CLoopMode_OnClientPollNetworking

found_gv: # This is for reference to global variable.
  - insn_va: '0x180444400'
    insn_disasm: mov rcx, cs:qword_180666600 # Must load/reference the global variable
    gv_name: g_pNetworkMessages
  - insn_va: '0x180333300'
    insn_disasm: lea rax, unk_180222200 # Must load/reference the global variable
    gv_name: s_EventManager

found_struct_offset: # This is for reference to struct offset. NOTE THAT virtual function pointer should not be here! virtual function pointer should ALWAYS be in found_vcall !
  - insn_va: '0x1801BA12A' # Always be the instruction with displacement offset
    insn_disasm: mov rcx, [r14+58h] # Always be the instruction with displacement offset
    offset: '0x58'
    size: 8
    struct_name: CResourceService
    member_name: m_pEntitySystem
```

If nothing found, output an empty YAML. DO NOT output anything other than the desired YAML. DO NOT collect unrelated symbols.
```

### Variables

| Variable | Source | Notes |
|------|------|------|
| `{disasm_for_reference}` | Old IDA export | Disassembly with symbols |
| `{procedure_for_reference}` | Old IDA export | Pseudocode with symbols |
| `{disasm_code}` | New IDA export | Disassembly without symbols |
| `{procedure}` | New IDA export | Pseudocode without symbols |
| `{symbol_name_list}` | Extracted from the old version | List of symbols to locate in the new version |

## Workflow

### Complete process

```text
Step 1: Prepare the data
  - Load the old binary into IDA (with PDB/symbols)
  - Load the new binary into IDA (without symbols)
  - Find anchor functions shared by both versions (exported functions, string references and similar)

Step 2: Batch export
  - From the old version: export disassembly + pseudocode of the anchor functions (with symbol names)
  - From the new version: export disassembly + pseudocode of the same anchor functions (without symbol names)

Step 3: LLM comparison
  - Fill the prompt template with the data
  - Call the LLM API (recommended: deepseek for volume and low cost, switch to gpt for very large functions)
  - Parse the returned YAML

Step 4: Apply the results
  - Apply the symbol mappings in the YAML to the new IDB in bulk
  - Rename in bulk with idapro_rename or an IDAPython script

Step 5: Iterate
  - Functions migrated in the first round become new anchors
  - Step into those functions and keep comparing their internal calls
  - Repeat until every target function is covered
```

### Anchor selection strategy

| Anchor type | Reliability | Notes |
|---------|--------|------|
| Exported function | Highest | Name unchanged, address may change |
| String reference | High | String content unchanged, reference location may change |
| Constant/magic number | Medium | Signature value unchanged |
| Code pattern | Medium | Function structure similar but every address changed |

### Batch processing suggestions

- Compare 1 function at a time (avoids context blow-up)
- Use deepseek for medium functions (<200 lines)
- Switch to gpt-4o or claude for very large functions (>500 lines)
- Call concurrently for speed (10-20 concurrent)
- Cache results to avoid repeated calls

## Output format

### 5 symbol types in the YAML output

| Type | Meaning | Key fields |
|------|------|---------|
| `found_vcall` | Virtual function call (indirect call) | `vfunc_offset`, `func_name` |
| `found_call` | Direct function call | `insn_va`, `func_name` |
| `found_funcptr` | Function pointer reference | `insn_va`, `funcptr_name` |
| `found_gv` | Global variable reference | `insn_va`, `gv_name` |
| `found_struct_offset` | Struct offset reference | `offset`, `struct_name`, `member_name` |

### Actions applied after parsing

```text
found_call → idapro_rename(addr=call_target, name=func_name)
found_vcall → idapro_set_comments(addr=insn_va, comment="vcall: {func_name} @ +{offset}")
found_funcptr → idapro_rename(addr=funcptr_target, name=funcptr_name)
found_gv → idapro_rename(addr=gv_addr, name=gv_name)
found_struct_offset → idapro_set_comments(addr=insn_va, comment="{struct_name}.{member_name}")
```

## Typical scenario examples

### Scenario 1: ntoskrnl.exe without a PDB

```text
Have: ntoskrnl.exe 10.0.26100.2000 + complete PDB
Target: ntoskrnl.exe 10.0.26100.2605 (PDB withdrawn)
Need: locate the new address of PspSetCreateProcessNotifyRoutine

Steps:
1. Load both versions into IDA
2. Find the exported function PsSetCreateProcessNotifyRoutine (present in both versions)
3. In the old version it calls PspSetCreateProcessNotifyRoutine (with symbols)
4. In the new version it calls sub_140822108 (no symbols)
5. The LLM sees at once: sub_140822108 = PspSetCreateProcessNotifyRoutine
6. Apply in bulk
```

### Scenario 2: migration after an application update

```text
Have: complete reverse engineering results for target.exe v1.0 (200+ functions named)
Target: target.exe v1.1 (every symbol lost)
Need: migrate 200 function names in bulk

Steps:
1. Export disassembly + pseudocode of every named function from the old version
2. Find the matching anchors in the new version through exported functions/strings
3. Call the LLM comparison in bulk
4. Parse the YAML and rename in bulk
5. Iterate deeper
```

## LLM selection advice

| Model | Suited to | Cost | Speed |
|------|---------|------|------|
| DeepSeek V3 | Small and medium functions (<200 lines), batch processing | Very low | Fast |
| GPT-4o | Very large functions, complex control flow | Medium | Fast |
| Claude Sonnet | Medium and large functions that need reasoning | Medium | Fast |
| Claude Opus | Extremely complex functions that need deep understanding | High | Slow |

Recommended strategy: DeepSeek by default; upgrade automatically when the context limit is exceeded or results are inaccurate.

## Notes

- **Do not give the whole binary to the LLM**: compare one function at a time
- **Anchors must be reliable**: if an anchor itself is wrong, everything after it is wasted
- **Spot-check the results manually**: the LLM is not 100% accurate, so verify key symbols
- **Cache intermediate results**: avoids wasting tokens on repeated calls
- **Watch the context limit**: very large functions (>1000 lines of disassembly) need splitting or a large-context model

---

## On-Demand Bootstrap

### Tool dependencies

| Tool | Purpose | Auto-installable |
|------|------|-----------|
| IDA Pro | Export disassembly/pseudocode | ✗ (commercial software) |
| Python | Script execution, API calls | ✓ |
| PyYAML | Parse the YAML returned by the LLM | ✓ (pip install pyyaml) |
| LLM API | Run the comparison | Requires an API key |

### Notes

The core of this skill does not depend on heavy tool installs; it mainly depends on:
- IDA Pro already present (managed with the `ida-reverse/` skill)
- Python + requests/httpx (to call the API)
- An LLM API endpoint

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Trigger condition**: symbols/reverse engineering results exist for an old version and need migrating to a new version
**Downstream exits**:
- Need to open the binary first → `ida-reverse/`
- Need quick reconnaissance to confirm version differences → `radare2/`

**Sibling modules**: `ida-reverse/` (data export and symbol application both go through IDA)


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
