# Go Binary Reverse Engineering Guide

> Go binaries pose unique challenges: static linking makes them huge, they have tens of thousands of functions, strings use a special format, and recovery after symbol stripping is hard.
> This document covers the toolchain, recovery techniques and practical workflows.

---

## Identifying Go binaries

Quickly decide whether a binary was compiled by Go:

```bash
# String traits
strings binary | grep -E "runtime\.|go\.buildid|GOROOT"

# rabin2 reconnaissance
rabin2 -z binary | grep -i "runtime"

# Unusually large file size (statically linked runtime)
# Typical Hello World: C ~20KB, Go ~2MB
```

Common traits:
- Many functions with the `runtime.` prefix
- A `go.buildid` section
- `GOROOT`, `GOPATH` path strings
- 5000-50000+ functions (including the whole runtime and standard library)

---

## Core toolchain

### Symbol recovery

| Tool | Purpose | Link |
|------|------|------|
| **GoReSym** | By Mandiant, parses Go symbol information (pclntab/moduledata) | https://github.com/mandiant/GoReSym |
| **GoResolver** | By Volexity, deobfuscates Garble binaries automatically through CFG similarity | https://github.com/volexity/GoResolver |
| **redress** | Analyzes stripped Go binaries, recovers types/interfaces/package structure | https://github.com/goretk/redress |
| **GoStringUngarbler** | By Google, recovers strings obfuscated by Garble | https://github.com/mandiant/GoStringUngarbler |

### IDA plugins

| Tool | Purpose | Link |
|------|------|------|
| **go_parser** | IDA plugin that parses moduledata/pclntab/type information | https://github.com/0xjiayu/go_parser |
| **IDAGolangHelper** | IDA script set that parses Go type information | https://github.com/sibears/IDAGolangHelper |
| **AlphaGolang** | SentinelLabs IDAPython script set | https://github.com/SentineLabs/AlphaGolang |
| **Native support in IDA 9.2+** | Official Hex-Rays Go decompilation improvements | https://hex-rays.com/blog/stop-guessing-and-start-going |

### Ghidra plugins

| Tool | Purpose | Link |
|------|------|------|
| **Ghidra + GoReSym output** | Export symbols with GoReSym, then import into Ghidra | Used together |
| **golang_loader_assist** | Ghidra Go loading helper | Community script |

### Standalone analysis tools

| Tool | Purpose | Link |
|------|------|------|
| **gore** | Go reverse engineering library (the base of redress) | https://github.com/goretk/gore |
| **garble** | Go obfuscation tool (know it to counter it) | https://github.com/burrowers/garble |

---

## Key structures of Go binaries

### pclntab (PC Line Table)

The most important structure in a Go binary, containing:
- Every function name and address mapping
- Source file paths
- Line number information
- Stack frame sizes

Even after symbols are stripped, pclntab usually still exists (the Go runtime depends on it).

```text
How to locate it:
1. Search for the magic bytes: 0xFFFFFFF0 (Go 1.16+) or 0xFFFFFFFB (Go 1.18+)
2. Locate it automatically with GoReSym
3. Parse it automatically with the go_parser IDA plugin
```

### moduledata

Contains:
- The pclntab pointer
- Type information table
- itab (interface tables)
- Global variable information

### String format

Go strings are not C-style null-terminated but a `(pointer, length)` structure:

```text
C string:   "hello\0"
Go string:  struct { ptr *byte; len int } → ptr points to "hello" (no \0)
```

As a result the default string recognition of IDA/Ghidra misses many Go strings.

**Solutions**:
- Identify Go strings automatically with `go_parser`
- Export the string list with GoReSym
- Manually: find `runtime.stringtable` or locate through cross-references

---

## Practical workflows

### Scenario 1: unstripped Go binary

```text
1. GoReSym -t -d -p binary > symbols.json
   → Export every function name, type and source file path
2. Load into IDA/Ghidra
3. Import GoReSym's symbol information
4. Filter out runtime.* and standard library functions, focus on user code
5. Start the analysis from main.main
```

### Scenario 2: stripped Go binary

```text
1. GoReSym -t -d -p binary > symbols.json
   → Even after strip, pclntab is usually still there
2. If GoReSym fails → use redress
   redress -src binary    # recover source file paths
   redress -pkg binary    # recover the package structure
   redress -type binary   # recover type information
3. Load into IDA + the go_parser plugin
4. Run go_parser for automatic recovery
5. Start from the recovered main.main
```

### Scenario 3: Garble-obfuscated Go binary

```text
Garble:
- Randomizes function names (main.main → main.a3f2b1c)
- Encrypts strings
- Removes file path information
- Obfuscates package names

Countermeasures:
1. GoResolver (CFG signature matching)
   → Recovers standard library function names through control flow graph similarity
2. GoStringUngarbler (string decryption)
   → Identifies Garble's string encryption pattern automatically and decrypts it
3. Dynamic analysis (Frida/dlv)
   → Hook runtime functions to observe actual behavior
4. Comparative analysis
   → Compile a Hello World with the same Go version and compare the runtime part with binary-diff
```

### Scenario 4: CGo mixed compilation

```text
1. Identify the CGo boundary (_cgo_* functions)
2. Recover the Go part with go_parser
3. Analyze the C part with regular IDA
4. Watch bridge functions such as _cgo_topofstack and crosscall2
```

---

## Common command quick reference

```bash
# GoReSym: export symbols
GoReSym -t -d -p binary > symbols.json
GoReSym -t -d -p binary -o ida_script.py  # generate an IDA script

# redress: analyze stripped binaries
redress -src binary          # source file paths
redress -pkg binary          # package structure
redress -type binary         # type information
redress -interface binary    # interface information
redress -filepath binary     # complete file paths

# GoResolver: deobfuscate Garble
GoResolver -binary binary -output resolved.json

# GoStringUngarbler: decrypt Garble strings
GoStringUngarbler -i binary -o deobfuscated_binary

# Quickly determine the Go version
strings binary | grep "go1\."
GoReSym -p binary | grep "Version"
```

---

## Go analysis flow in IDA

```text
1. Load the binary (choose the correct architecture)
2. Wait for automatic analysis to finish
3. Run the go_parser plugin:
   - File → Script File → go_parser.py
   - Or Edit → Plugins → Go Parser
4. The plugin automatically:
   - Parses pclntab
   - Recovers function names
   - Marks Go strings
   - Parses type information
5. Filter the view:
   - Hide runtime.* functions
   - Focus on main.* and third-party packages
6. Start reversing from main.main
```

---

## Common pitfalls

| Pitfall | Description | Fix |
|------|------|------|
| Too many functions to read | Go static linking produces 5000-50000 functions | Filter by package name, look only at main.* and business packages |
| Incomplete string recognition | Go strings are not null-terminated | Recover with go_parser or GoReSym |
| Decompilation is hard to read | Go's defer/goroutine/interface make pseudocode complex | IDA 9.2+ improves it, or use dynamic analysis as support |
| Garble obfuscation | Function names/strings fully randomized | GoResolver + GoStringUngarbler |
| Version differences | Different Go versions use different pclntab formats | GoReSym supports Go 1.2-1.23+ |
| CGo boundary | Mixed Go and C code | Identify _cgo_* functions as the boundary |

---

## Working with other skills

| Need | What to use |
|------|--------|
| Deep IDA analysis of Go binaries | `ida-reverse/` + the go_parser plugin |
| Ghidra analysis (free) | Ghidra + GoReSym symbol import |
| Quick reconnaissance | `radare2/`: `rabin2 -z` for strings |
| Dynamic hooks | Frida (hook runtime functions) or dlv (the native Go debugger) |
| Cross-version comparison | `binary-diff/`: migrate symbols from the old version to the new one |
| Garble deobfuscation | GoResolver + GoStringUngarbler |
