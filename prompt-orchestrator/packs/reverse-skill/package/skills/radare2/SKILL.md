---
name: radare2
description: |
  Use this skill whenever the user wants to analyze binaries with radare2/r2 from the command line, including reverse engineering, disassembly, function analysis, strings/import inspection, patching, binary diffing, hex inspection, or r2 scripting. Also use it when the user mentions PE/ELF/Mach-O/DEX/WASM files together with CLI analysis, `rabin2`, `rasm2`, `radiff2`, `r2pipe`, or asks for radare2 command help on Windows/Linux/macOS.
---

# radare2

Binary analysis skill for the `radare2` CLI. It focuses on doing reconnaissance, analysis, location, export and light modification directly on the command line, without a GUI.

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

## Scope

Prefer this skill when the user wants to:

- Analyze `exe`, `dll`, `so`, `elf`, `apk`, `dex`, `wasm` and similar files with `r2` / `radare2`
- Ask how to use `rabin2`, `rasm2`, `radiff2`, `rahash2`, `rax2`
- Disassemble on the command line, view functions, strings, imports and exports, query cross-references, patch
- Write `radare2` batch commands, `-c` automation commands or `r2pipe` scripts

If the user explicitly wants GUI reverse engineering, Hex-Rays style pseudocode or an IDA workflow, prefer `ida-reverse`. For web JS reverse engineering, prefer `reverse-engineering`.

## Check the environment first

Do not assume `r2` is available. Check first:

```powershell
r2 -v
rabin2 -v
```

If it is not installed, check common install locations or suggest installing it.

Common executables on Windows:

- `radare2.exe`
- `rabin2.exe`
- `rasm2.exe`
- `radiff2.exe`
- `rahash2.exe`
- `rax2.exe`
- `r2pm.exe`

## Bundled resources

This skill ships two resources; reuse them instead of improvising a duplicate set of commands each time.

### `scripts/recon.ps1`

Standard reconnaissance script, suited to a first-pass overview. It prints:

- Basic information
- Sections
- Imports
- Exports
- Strings
- Optional `r2 -A` automatic analysis summary

How to call:

```powershell
powershell -File "<skill-root>\radare2\scripts\recon.ps1" -TargetPath "C:\path\to\sample.exe"
```

To include the `r2` automatic analysis:

```powershell
powershell -File "<skill-root>\radare2\scripts\recon.ps1" -TargetPath "C:\path\to\sample.exe" -RunAnalysis
```

### `references/cheatsheet.md`

When you need more command details, common scenario templates or a quick syntax reminder, read this cheat sheet instead of guessing from memory.

## Known behavior

### Occasional missing `.sdb` warning on Windows

For some PE files, `rabin2` reconnaissance may show a warning like this:

```text
ERROR: Cannot find ...\share\format\dll\*.sdb
```

If the main output still comes back normally, it usually does not affect basic reconnaissance conclusions; keep analyzing. Do not declare the analysis failed because of such an incidental warning.

## Basic principles

### 1. Reconnaissance first, then dig deep

Do not start with full automatic analysis. First confirm the file type, architecture, entry point, strings and import table with lightweight commands, then decide whether to run `aaa`, `aaaa` or targeted analysis.

### 2. Prefer the minimal sufficient command

`radare2` has a great many commands; the user usually only needs the shortest path:

- File information: `rabin2 -I`
- Strings: `rabin2 -z`
- Imports and exports: `rabin2 -i` / `rabin2 -E`
- Interactive analysis: `r2 <file>`, then run local commands

### 3. Be careful before modifying

If the user wants to patch the binary:

- Open read-only by default first: `r2 <file>`
- Use write mode only when modification is clearly needed: `r2 -w <file>` or `oo+` in the session
- State the risk before modifying, to avoid overwriting the original file unintentionally

## Common workflows

## Workflow 1: quick reconnaissance

Suited to a binary you just received.

### Hard gate (MUST; entering workflow 2 and later is forbidden until satisfied)

For binaries with an import table such as PE/ELF/Mach-O, you **MUST** complete the import table check and record it as Evidence before entering function-level analysis or dynamic steps:

1. Run `rabin2 -i <sample>` (or the imports section of the `recon.ps1` output); for DLL/SYS you also MUST run `rabin2 -E` and record `E-exports`
2. Write the complete/categorized import table result to Evidence (suggested id: `E-imports` or `E-triage-imports`), containing at least:
   - The reproduction command (`repro_command`)
   - Categorized summary of key imports: network / file / crypto / process injection / registry / other suspicious APIs
   - If the import table is empty, parsing fails or the tool errors: you still MUST record the failure and the raw output as Evidence, **no silent skipping**
   - Import table "too clean" (only base DLLs): MUST note the suspicion of dynamic loading, SHOULD move to dynamic API capture
3. .NET and others without a traditional IAT: MUST use the equivalent anchor (dnSpy/IL/metadata summary) written into the same Evidence semantic slot; passing empty is forbidden
4. IAT repair of packed samples: ImportREC (or equivalent) for x86, Scylla (or equivalent) for x64. On repair failure, MUST record `E-iat-repair-fail` and switch to dynamic API breakpoints; endless grinding on the static IAT is **forbidden** (see `reverse-engineering/references/re-agent-workflow.md` §1.2)
5. When the user explicitly asks to "redo the import table check / recheck the import table / redo the IAT": MUST redo the named step itself (when blocked, go through the feasibility gate first: explain the precondition + ask for confirmation; if forced, mark quality=unreadable); **substituting an unrelated step to claim completion is forbidden**

Until import table Evidence (or a valid equivalent anchor / IAT failure side path) is recorded: MUST NOT claim "basic reconnaissance complete", MUST NOT enter the deep conclusions of workflow 2+.

Prefer running the bundled script directly:

```powershell
powershell -File "<skill-root>\radare2\scripts\recon.ps1" -TargetPath "sample.exe"
```

If you only need minimal manual commands, use:

```powershell
rabin2 -I sample.exe
rabin2 -z sample.exe
rabin2 -i sample.exe
rabin2 -E sample.exe
```

Focus on:

- File format, bitness, architecture, platform
- Entry point address
- Suspicious strings: URLs, paths, errors, registry, command-line arguments
- Imported functions: network, file, crypto, process injection, registry operations (**MUST be recorded as Evidence, see the hard gate above**)

## Workflow 2: interactive function analysis

```powershell
r2 sample.exe
```

Common commands once inside:

```text
aaa          # regular automatic analysis
afl          # list functions
iz           # list strings
iS           # list sections
is           # list symbols
s entry0     # seek to the entry point
pdf          # disassemble the current function
VV           # enter visual mode (if the terminal suits it)
q            # quit
```

Notes:

- Prefer `aaa` by default; do not start with the heavier `aaaa`
- If the sample is large or analysis is slow, analyze only around the entry and expand manually

## Workflow 3: locate main / key logic

```text
afl~main
afl~sym.
iz~http
iz~error
axt <addr>
```

Approach:

- Start from `main`, the entry point and string references
- Use `axt` to see who references a string or address
- Once you find the reference, `s <addr>`, then `pdf`

## Workflow 4: hex and memory view

```text
px 64        # 64 bytes of hex from the current address
pd 20        # disassemble 20 instructions
psz          # read the string at the current address
pxa          # friendlier hex view
```

## Workflow 5: binary patch

Use only when the user explicitly asks to modify the file:

```powershell
r2 -w sample.exe
```

Once inside, for example:

```text
s 0x401000
wa nop
wa jmp 0x401050
wq
```

Common write operations:

- `wa <asm>`: write assembly
- `wx <hex>`: write raw bytes
- `wq`: write and quit

Back up the original file before modifying. If the user did not mention a backup, remind them at least once.

## Workflow 6: non-interactive automation

Suited to one-shot output:

```powershell
r2 -A -q -c "afl;iz;ii;q" sample.exe
```

Common parameters:

- `-A`: automatic analysis at startup
- `-q`: quiet mode
- `-c`: run a command string

If there are many commands, arrange them in a readable order; do not cram them into a hard-to-maintain long string.

It is better to lay the groundwork with the bundled reconnaissance script first, then decide whether to add custom commands.

## Common sub-tools

### `rabin2`

Suited to static information extraction:

```powershell
rabin2 -I sample.exe   # basic information
rabin2 -S sample.exe   # sections
rabin2 -s sample.exe   # symbols
rabin2 -i sample.exe   # imports
rabin2 -E sample.exe   # exports
rabin2 -z sample.exe   # strings
rabin2 -zz sample.exe  # more detailed strings
```

### `rasm2`

Suited to quick assembly/disassembly:

```powershell
rasm2 -d "9090"
rasm2 -a x86 -b 64 "xor eax, eax"
```

### `radiff2`

Suited to comparing two binaries:

```powershell
radiff2 old.exe new.exe
radiff2 -C old.exe new.exe
```

### `rahash2`

Suited to computing hashes:

```powershell
rahash2 -a md5 sample.exe
rahash2 -a sha256 sample.exe
```

### `rax2`

Suited to base and encoding conversion:

```powershell
rax2 0x401000
rax2 4198400
rax2 -s hello
```

## Recommended analysis order

For an unknown sample, work in this order:

1. `rabin2 -I` for format, architecture, entry point
2. `rabin2 -z` for strings
3. `rabin2 -i` for imported functions: **MUST + Evidence (hard gate, see workflow 1)**
4. For interactive analysis, enter `r2` (only once the Evidence from step 3 is on disk)
5. `aaa` first, then `afl` / `iz` / `pdf`
6. Locate key functions step by step through string references, import calls and the entry flow

This order keeps noise low and builds a sense of direction quickly. Step 3 is not an optional optimization; it is the hard gate before digging deep.

## Windows notes

- When a path contains spaces, the command must quote it correctly
- If the current terminal cannot find `r2`, `PATH` may have just been updated; open a new terminal and try again
- Some samples need administrator rights to read, but do not elevate by default unless the user explicitly needs it
- Before dynamically debugging a suspicious sample, confirm the user's intent to avoid mistakes

## Output style

When the user wants you to actually analyze the file rather than just get commands:

- Give a summary of the reconnaissance results first
- Then list the key evidence: strings, imports, functions, addresses
- Finally give next-step suggestions or continue the deeper analysis

Do not just list commands without explaining why.

## Typical request examples

### Example 1: analyze an exe

User: `Take a look at what this exe does, radare2 is fine`

Handling:

1. Start with `rabin2 -I/-z/-i`
2. Decide whether to enter `r2`
3. Dig into the entry and key string references with `aaa`, `afl`, `pdf`

### Example 2: find where a string is used

User: `Which function triggers this error string`

Handling:

1. Find the string address with `iz~keyword`
2. Find references with `axt <addr>`
3. Seek to the reference `s <addr>`, then `pdf`

### Example 3: change a jump

User: `Change this jne to je`

Handling:

1. Confirm the target address first
2. State clearly that you will enter write mode
3. Use `wa je <target>` or `wx` directly
4. Disassemble again after the change to verify

## Practices to avoid

- Do not treat `radare2` as a tool with only the `aaa` command
- Do not open the user's file in write mode without stating the risk
- Do not draw conclusions before basic reconnaissance
- **Skipping the import table check is forbidden** (`rabin2 -i` / recon imports): do not move on until it is written to Evidence; when the user asks to redo the import table, doing a different step instead is forbidden
- **Grinding on static after an IAT repair failure is forbidden**: record `E-iat-repair-fail`, then switch to dynamic; using only ImportREC on 64-bit samples is forbidden
- Do not steer web JS reverse engineering into this skill; that belongs to `reverse-engineering`

## References

- Command quick reference: `references/cheatsheet.md`
- Standard reconnaissance script: `scripts/recon.ps1`

## radare2-skills ecosystem

The radare2-skills project (radareorg/radare2-skills) provides a more complete set of ecosystem tools and workflows:

- **r2xsql**: SQL queries over binary imports / strings / functions
- **r2mcp / r2http**: MCP tools and a stateful HTTP command channel
- **radius2**: symbolic execution, symbolic dynamic analysis
- **r2pm**: plugin management, extensions
- **decompiler plugins**: the radare2 plugin mechanism

**Usage strategy**:
- When the user mentions `r2xsql`, `r2mcp`, `r2http`, `radius2`, `r2pm`, `rabin2`, `rasm2`, `radiff2`, `rahash2`, `rax2`, route to this skill first (radare2/SKILL.md)
- These tools are only ecosystem accelerators and **cannot bypass**: the authorization gate, `tool-index` validation, Evidence imports, write mode confirmation
- Give minimal reproducible command examples:
  - `r2xsql -s <file> -q "SELECT ..."`
  - `curl.exe -sS --data-binary 'aaa' http://127.0.0.1:9393/cmd`
  - `radius2 -p <binary> ...`
  - `r2pm -ci <plugin>`

This skill keeps its original hard gates and evidence chain integrity; skipping any authorization or Evidence step is not allowed.

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Upstream alternative**: `ida-reverse/` (upgrade to IDA when decompilation/pseudocode is needed)
**Downstream exits**:
- Dynamic analysis needed → `reverse-engineering/tools-dynamic.md` (Frida/GDB)
- Deep decompilation needed → `ida-reverse/`
- After PAT finds interesting strings and cross-references are needed → `ida-reverse/` (IDA's xrefs are stronger)

**Sibling modules**: `ida-reverse/` (complementary: r2 is fast for reconnaissance, IDA is deep for decompilation)

## On-Demand Bootstrap

This skill's entry scripts are wired into the unified bootstrap system. A missing radare2 does not raise an error right away; the scripts try to install it automatically.

### Automation boundaries

| Tool | Auto-installable | Install method | Notes |
|------|-----------|---------|------|
| r2 | ✓ | GitHub Release ZIP (w64) | Downloads and extracts automatically to `%USERPROFILE%\Tools\radare2\` |
| rabin2 | ✓ | Same as above (included in the radare2 release package) |: |
| rasm2 | ✓ | Same as above |: |
| radiff2 | ✓ | Same as above |: |
| rahash2 | ✓ | Same as above |: |
| rax2 | ✓ | Same as above |: |

### Bootstrap trigger points

- `scripts/recon.ps1`: calls `bootstrap-reverse.ps1` automatically when `rabin2` or `r2` is missing

### When bootstrap fails

If the automatic install fails (no network, GitHub API rate limit and similar), the script raises a clear error with a manual install link.

Manual install: download `radare2-*-w64.zip` from https://github.com/radareorg/radare2/releases, extract it to `%USERPROFILE%\Tools\radare2\` and make sure the `bin\` directory is on PATH.


## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did the import table check run and get written to Evidence (E-imports / E-triage-imports or the .NET equivalent)? Does a DLL/SYS include E-exports?
- [ ] Did an IAT repair failure record E-iat-repair-fail and switch to dynamic? Did a redo request return to the same step?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
