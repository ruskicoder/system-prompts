# 2026-09-29 Static Triage of a Stripped Go EXE + rustc Native DLL

## Scenario classification
Binary analysis (Go / Rust reverse engineering, language runtime identification + symbol/metadata recovery)

## Target overview
Pure static triage of a stripped Go application EXE and its rustc-compiled native licensing runtime DLL:
recovered the Go function name table, identified the native DLL's identity and exports, and decompiled the key exports without touching the semantics of the encrypted program.

## Scope summary (redacted)
- auth_basis: own_system (a local sample owned by the owner)
- network_profile: offline
- asset_types: [pe-exe, pe-dll]

## Roles
- lead_role: lead
- specialists: []

## Complete execution chain

1. Routing: `master-route.ps1 -Hint "... go rust binary ..."` → PRIMARY R33 (go-rust-reverse), secondary R22 (ghidra-reverse).
2. case-init (`offline-sample` preset) → `auth.status=granted`, `network_profile=offline`, `ready_for_act=true`; case-guard OK.
3. Confirmed sample hashes and types; the `rabin2` index path was stale (see pitfalls), so parsed the PE with a script instead.
4. `go version -m <exe>` → toolchain/modules/dependencies/build flags/local replace paths (`-trimpath -tags=release` still present).
5. `go tool nm <exe>` → `no symbols`; `go tool buildid <exe>` → empty (confirms it is stripped).
6. A string scan recovered the Go function names in `runtime.pclntab` (no GoReSym needed).
7. A string scan of the native DLL → the rustc commit hash + 9 C ABI exports.
8. A script parsed the PE export table → exact RVAs/VAs; Ghidra 12.1.4 headless auto-analysis + export decompilation.

## Evidence chain summary (redacted)

| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-002 | info | validated | command | `go version -m <exe>` | F-001 |
| E-003 | info | validated | command | `python3 scripts/extract_strings.py <exe> gofunc` | F-002 |
| E-006 | info | validated | command | `analyzeHeadless ... -postScript ExportDecomp.java` | F-002 |

## Finding / Path summary
- top_finding: the stripped Go EXE still fully exposes the vendor protection surface (at function name level) through the retained `runtime.pclntab`,
  which complements the clean C ABI exports of the native rustc DLL, so the licensing call path can be rebuilt without dynamic analysis.
- path_type: callflow
- path_one_liner: `go version -m` → pclntab function names → native DLL exports → Ghidra decompilation of the exported functions.

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| `rabin2`/`r2` not found | The `tool-index.md` path exists, but the install `bin` holds only `r2sdb` and is not on PATH | Switched to the `pe_exports.py` script to parse the PE; do not guess paths | Small |
| Ghidra postScript reports "class could not be found" | Actually a `javac` type error: `getExternalEntryPointIterator()` returns `AddressIterator`, not `SymbolIterator` | Read the real compile error at the start of the headless log; fix the type | Small |
| Ghidra has no system java | `JAVA_HOME` not set | Point it at the JDK directory bundled with Ghidra | Small |

## Toolchain findings
- Go's own toolchain (`go version -m` / `go tool nm` / `go tool buildid`) is enough for Go metadata and the "stripped or not" verdict; GoReSym is not required.
- GoReSym-style results (thousands of function names) can be reproduced by a pclntab string scan, which suits environments without GoReSym.
- Ghidra 12.1.4 headless is stable on Windows; a Java postScript is a reliable batch decompilation method.
- The radare2 index may lag behind; always confirm that the executable really exists.

## Key code/commands

```
go version -m <exe>
go tool nm <exe>          # expect no symbols
go tool buildid <exe>     # expect empty
python extract_strings.py <exe> gofunc
python extract_strings.py <dll> rust
python pe_exports.py <dll>
$env:JAVA_HOME="<ghidra>\jdk-21..."; $env:KOTIK_GHIDRA_OUT="<out>"
analyzeHeadless.bat <projdir> Proj -import <dll> -scriptPath . -postScript ExportDecomp.java -deleteProject
```

## Improvement suggestions for this package
- The `tool-index.md` refresh should verify executability rather than only record that a path exists.
- Add a "pclntab triage without GoReSym" subsection and script to go-rust-reverse (contributed this time).
- The skill could point out the Ghidra postScript type trap and how to locate it in the log.

## Reusable patterns/script snippets
- `scripts/extract_strings.py`: Go pclntab name / Rust string filtering, pure Python with no dependencies.
- `scripts/pe_exports.py`: dependency-free PE section table + export table parsing (outputs exact RVAs/VAs).
- `references/ExportDecomp.java`: Ghidra headless decompilation of exported executable entries + panic anchors.

## Evolution actions
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [x] Updated sub-skill documentation (go-rust-reverse SKILL.md)
- [x] Added a pitfalls record (stale tool-index, Ghidra postScript type error)
- [ ] No update needed

## Environment information
- OS: Windows 10.0.26100
- Tool versions: Go 1.27.0 (target), Ghidra 12.1.4 + JDK 21, Python 3.13
- Target platform/version: windows/amd64 (Go application + rustc native DLL)

## Redaction requirements
Redacted: no real domains/IPs/tokens; the sample is a local file owned by the owner.
