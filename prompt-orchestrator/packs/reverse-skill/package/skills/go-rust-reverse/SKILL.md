---
name: go-rust-reverse
description: Use for reverse engineering stripped Go and Rust binaries including runtime recognition, pclntab/moduel data recovery, panic strings, and idiomatic decompilation recovery.
---

# Go / Rust Binary Reverse Engineering

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md`
2. `NOW`: confirm that the sample is a Go/Rust build (`file`/strings/runtime traits)
3. `NEXT`: whether GoReSym / related plugins are available
4. `ACT`: runtime identification → symbol/metadata recovery → business logic

## When to use

- Stripped Go malware/tools
- Rust release binaries, analysis driven by panic strings
- Language-specific methods that complement general ida/ghidra

## Workflow

### Go

```text
□ Identify go.buildid, leftover runtime symbols, pclntab
□ Recover function names with GoReSym / redress / the IDA Go plugin
□ Watch how interface, slice and string structures look in decompilation
□ Network/crypto library paths: crypto/* net/http
```

### Rust

```text
□ Panic strings, rust_begin_unwind, crate path hints
□ Code bloat from generic instantiation; locate string xrefs first
□ Async/tokio state machines need cross-references
```

### Dynamic

```text
□ Frida still works; watch Go stacks and scheduling
□ Prefer breakpoints driven by log and configuration strings
```

## Toolchain

| Tool | Purpose |
|------|------|
| GoReSym | Go metadata |
| IDA/Ghidra + Go/Rust plugins | Decompilation |
| radare2 | Quick strings |
| strings / rabin2 | Triage |
| `go version -m` / `go tool buildid` / `go tool nm` | Built-in Go metadata (no GoReSym needed) |
| `scripts/extract_strings.py` / `scripts/pe_exports.py` | Go pclntab names, Rust strings, PE export table (pure Python, no dependencies) |
| `references/ExportDecomp.java` | Ghidra headless postScript: export decompilation of exported functions |

## pclntab recovery without GoReSym (verified)

Even when a Go binary uses `-ldflags=-s -w -buildid=` and `go tool nm` reports `no symbols`,
`runtime.pclntab` still keeps every function name. Minimal flow:

```text
□ go version -m <exe>              # toolchain, modules, dependencies, build flags, local replace paths
□ go tool nm <exe>                 # expect no symbols (confirms stripping)
□ go tool buildid <exe>            # empty = cleared
□ python scripts/extract_strings.py <exe> gofunc   # recover main.* / vendor package function names
□ python scripts/pe_exports.py <dll>               # exact export RVA/VA of native companion DLLs
□ Ghidra headless (see references/ExportDecomp.java) decompiles native exports
```

**Note**: recovering function names restores metadata and does not bypass protection; the conclusion must state that boundary.
Paths in `tool-index.md` may lag; confirm that the executable really exists before running (seen before: `rabin2`
indexed but only `r2sdb` left in the install directory).

## References

- `references/go-rust-notes.md`
- `references/ExportDecomp.java` (Ghidra headless export decompilation)
- `scripts/extract_strings.py` `scripts/pe_exports.py`
- `../reverse-engineering/go-reverse.md` `../ida-reverse/` `../ghidra-reverse/`
- seed: `field-journal/seed-002_go-malware-stripped.md`
- journal: `field-journal/2026-09-29_stripped-go-pclntab-rust-dll-triage.md`

## Routing context

**Upstream**: MASTER R33  
**Downstream**: malicious sample flow `malware-analysis`; general RE `reverse-engineering`

## Task completion self-check

- [ ] Did I recover key function names or an equivalent mapping?
- [ ] Did I record the language runtime evidence?
- [ ] Checklist?