---
name: dotnet-reverse
description: .NET / C# binary reverse engineering. Use when the target is a .NET assembly (PE header with CLR, managed .exe/.dll), C# build output (including NativeAOT), red team Sharp* tools (Rubeus / SharpHound and similar), obfuscated .NET programs (ConfuserEx / SmartAssembly / Babel / Eazfuscator), or a .NET loader / info-stealer / packed malware. Prefer dnSpyEx + de4dot, and link with the dnSpy MCP when the AI needs to operate directly. Not for pure native binaries (use reverse-engineering / ida-reverse).
license: MIT
compatibility: Requires a filesystem-based code agent or CLI with shell access, Windows host preferred (dnSpyEx is a Windows GUI); Linux/macOS can use the ILSpy/de4dot CLI + mono/dotnet runtime.
allowed-tools: Bash Read Write Edit Glob Grep Task WebFetch WebSearch
metadata:
  user-invocable: "false"
---

# .NET / C# Reverse Engineering Work Standard

## ACTION REQUIRED (execute immediately after reading)

1. `NOW`: confirm with DIE/`file`/the CLR header that the target is .NET managed (otherwise SWITCH to `ida-reverse/` / `reverse-engineering/`)
2. `NOW`: if obfuscation is suspected → unpack with `de4dot` first, produce `*-clean.exe`, keep the original sample
3. `NEXT`: dnSpyEx (or the dnSpy MCP / `ilspycmd`) statically: browse C# + use the **IL view** for key branches
4. `ACT`: debug dynamically when you need plaintext/C2; when the logic needs changing, prefer an **IL patch** over C# recompilation
5. At the end of the phase, give the user a menu of 3–6 next steps (including report export)

## Scope

Prefer this skill when the task falls into one of these scenarios:

- Identify and reverse .NET / C# build output (managed PE / .exe / .dll)
- Analyze the red team Sharp* toolchain (Rubeus, SharpHound, SharpShell and others)
- Deobfuscate ConfuserEx / SmartAssembly / Babel / Eazfuscator / .NET Reactor and similar packers
- Reverse the decryption and C2 logic of .NET loaders / info-stealers / RATs
- Patch C# programs (change branches, change constants, keygen)
- Analyze the Mono/Unity managed layer before IL2CPP (note: after IL2CPP compilation it is native, so use `reverse-engineering/` + seed-014)

If the target is a pure native binary (C/C++/Go/Rust build, no CLR), use `reverse-engineering/`, `ida-reverse/` or `radare2/` instead.

## Core principles

- **Identify before acting**: first confirm a .NET managed program (PE header CLR + `#~` / `#Strings` streams + mscoree `_CorExeMain`), then choose dnSpy over IDA
- **IL over C#**: dnSpyEx's C# decompiler loses or distorts information (compiler-generated state machines, async/await, yield), so key branches and patches must switch to the **IL editor**; use the C# view only for quick browsing
- **de4dot first**: when you meet an obfuscator, run `de4dot` once before static analysis, or strings and control flow stay garbled
- **MCP link**: if the environment registers the dnSpy MCP (`dnspy_*` tools), prefer the MCP surface for decompile / IL inspection to avoid switching back and forth in the GUI
- **Evidence-backed output**: write deobfuscated output, extracted configuration/C2/keys and patch diffs to disk

## Toolchain mapping

| Capability | First choice | Notes |
|------|------|------|
| Decompile + debug + patch | **dnSpyEx** | The ace, the only GUI with an IL editor; the old dnSpy is unmaintained, use the Ex fork |
| Lightweight CLI / headless decompilation | **ILSpy** (`ilspycmd`) | Suited to batches, scripting, Linux/macOS |
| Deobfuscation | **de4dot** | Default answer for mainstream packers such as the ConfuserEx family and SmartAssembly |
| Obfuscator identification | **Detect It Easy (DIE)** / **file** | Determine the packer type first, then choose de4dot parameters |
| Programmatic IL operations | **dnlib** | Write C# scripts that bulk-modify metadata / string decryptors |
| Direct AI operation | **dnSpy MCP** | Tool surface such as `dnspy_decompile` / `dnspy_inspect_il` |

> Prerequisites: install dnSpyEx + de4dot on a Windows host (choco or release); on Linux/macOS use `ilspycmd` + `dotnet runtime`. See the install matrix in `references/sharp-tools.md`.

## Six-phase workflow

### 1. Identify (recognize .NET)

Confirm that the target is a managed program; do not analyze a native PE as .NET:

```powershell
# Windows
file target.exe                       # "PE32 executable ... for MS Windows" is not enough
# Key: check for a CLR header
powershell -c "[System.Reflection.AssemblyName]::GetAssemblyName('target.exe')"
# or
Drag it into dnSpyEx directly: if it opens, it is managed

# General
strings target.exe | grep -iE "mscoree|_CorExeMain|mscorlib|System\\."
```

**.NET identification markers:**
- PE header `Data Directory[14]` (CLR Runtime Header) is non-zero
- `mscoree.dll` import / `_CorExeMain` entry
- `#~`, `#Strings`, `#US`, `#GUID`, `#Blob` metadata streams
- `mscorlib` / `System.Private.CoreLib` strings

**NativeAOT exception:** compiled to native with no CLR header, but it has `System.Private.CoreLib` strings and restructured type metadata; these go to `reverse-engineering/` (IDA/r2), and this skill only gives an identification hint.

### 2. Detect (detect the obfuscator)

```powershell
# DIE quick identification
diec target.exe                        # Detect It Easy CLI
# Or drag into dnSpyEx and check for many garbled class names / control flow distortion
```

Common obfuscators → unpacking strategy (details in `references/obfuscators.md`):

| Obfuscator | Characteristics | de4dot handling |
|--------|------|------------|
| ConfuserEx (1.0.0 / 2.x) | `<module>` anti-tamper, control flow distortion, string encryption | `de4dot target.exe` usually detects it automatically |
| SmartAssembly | `circular`/`string encoding`, resource compression | `de4dot target.exe` |
| Babel.NET | Method body encryption, control flow | `de4dot target.exe` |
| Eazfuscator.NET | String/resource encryption | `de4dot`, some versions need manual work |
| .NET Reactor | anti-tamper + necrobit | `de4dot`, new versions may fail and need manual work |

### 3. Deobfuscate

```powershell
# de4dot detects most packers automatically by default
de4dot target.exe -o target-clean.exe

# Specify the type (when automatic detection fails)
de4dot --type cfze target.exe          # ConfuserEx
de4dot --type sa target.exe            # SmartAssembly

# Multi-layer obfuscation / de4dot reports unknown
de4dot --detect target.exe             # see what it detects
# You may need to patch anti-tamper before de4dot (see references/obfuscators.md)
```

Output: `target-clean.exe`, used for later analysis. **Keep the original sample** for comparison.

### 4. Static Analyze

Load the unpacked sample in dnSpyEx:

- **C# view**: browse class structure, method signatures and strings quickly (for locating)
- **IL view**: key branches, crypto logic and state machines must be read in IL (right-click → Edit IL or the IL view)
- Find the entry: `Main` / `Startup` / module initializer (`Module .cctor`)
- Find key logic: search `flag`, `password`, `verify`, `check`, `encrypt`, `http`, `Config`

```text
Locate the string → cross-reference → find the method that uses it → read the branch logic in the IL view
```

### 5. Dynamic (dynamic debugging)

dnSpyEx debugger: attach to the process / start debugging, set breakpoints in key methods, observe at runtime:
- Decrypted plaintext strings (many obfuscators decrypt strings only at runtime)
- C2 addresses, configuration decryption results
- Exception-driven control flow (anti-debug often uses `try/catch` to hide the real path)

> .NET dynamic debugging is far friendlier than native: you see object values and string contents directly. Prefer dynamic over grinding on static.

### 6. Patch (modify as needed)

```text
dnSpyEx → right-click the method → Edit Method (C#) or Edit IL
  - Change a branch: ldc.i4.0 → ldc.i4.1 (false→true)
  - Change a constant: edit the string/number directly
  - Remove a check: nop out the whole block
File → Save Module → replace the original file
```

**IL patch reliability > C# patch**: C# recompilation can fail (missing references, wrong syntax), while IL editing almost never distorts. See `references/common-workflow.md`.

## Trigger scenario routing

Enter this skill when the user says:
- ".NET / C# binary reverse engineering" / "decompile a C# program"
- "dnSpy analysis" / "dnSpyEx patch"
- "ConfuserEx / SmartAssembly / Babel deobfuscation / unpacking"
- "Sharp* tool analysis" (Rubeus / SharpHound / SharpShell)
- ".NET malware / loader / info-stealer reverse engineering"
- "C# program patch / keygen / change a check"

## When to switch out

- Unity games compiled with IL2CPP → `reverse-engineering/` + `seed-014_unity-il2cpp-reverse.md` (IL2CPP is native, not dnSpy)
- NativeAOT output → `reverse-engineering/` (same as above, native)
- Pure native PE (no CLR) → `reverse-engineering/` / `ida-reverse/`
- Symbols/functions need bulk migration to another version → `binary-diff/`
- Attack path / call chain diagram needed → `diagram-generator/`

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Downstream exits**:
- IL2CPP / NativeAOT (native) → `reverse-engineering/`
- Deep native .so/.dll section analysis → `ida-reverse/` / `radare2/`
- AI needs to operate dnSpy directly → register and link the dnSpy MCP (see `references/sharp-tools.md`)

**Sibling modules**:
- `reverse-engineering/languages-compiled.md` (the .NET overview points to this module)
- `apk-reverse/` (Xamarin/MAUI Android reverse engineering can switch back to this module for the C# layer)

## Reference documents

- [references/obfuscators.md](references/obfuscators.md): ConfuserEx / SmartAssembly / Babel / Eazfuscator / .NET Reactor deobfuscation in detail + anti-tamper bypass
- [references/common-workflow.md](references/common-workflow.md): complete workflow, IL patch reliability, string decryptor extraction, state machine recognition
- [references/sharp-tools.md](references/sharp-tools.md): red team Sharp* tool analysis, tool install matrix, dnSpy MCP integration, community resource index

## Task completion self-check

- [ ] Did I confirm the CLR / managed identity (or SWITCH out of this skill)?
- [ ] Was the obfuscated sample unpacked with de4dot or an equivalent before deep analysis?
- [ ] Did I verify key logic in the IL view (not only the C# pseudocode)?
- [ ] Are the outputs (clean sample / configuration / patch diff) on disk and reproducible?
- [ ] Did I provide a next-step menu or a report exit?
