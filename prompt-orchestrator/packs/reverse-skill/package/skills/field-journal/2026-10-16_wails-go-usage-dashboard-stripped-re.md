# 2026-10-16 Full Logic Recovery of a Go+Wails Usage Dashboard Desktop Program (Stripped, No Symbols)

## Scenario classification
Binary analysis / Go stripped PE symbol recovery + logic recovery (Wails v2 desktop application)

## Target overview
**Pure static black-box** recovery of an owned Windows desktop "AI coding assistant usage dashboard" (`{target_app}`, Go + Wails v2, a single ~15MB exe):
without reading the project's source code, recovered every function symbol from the binary alone, plus data collection (3 kinds of data sources), SQLite storage, cost calculation, reports and the front-end interface surface.

## Scope summary (redacted)
- auth_basis: the user's own program, static analysis explicitly authorized (read-only, the sample is not run)
- network_profile: offline (pure local static analysis, no outbound connections throughout)
- asset_types: [pe_go_stripped, wails_v2_desktop, sqlite_schema]

## Roles
- lead_role: lead
- specialists: []

## Complete execution chain

1. Baseline forensics: sha256 / PE structure / BuildInfo / all strings (41,000) → confirmed Go 1.24.4, `-trimpath -s -w`, Wails v2.11.0, CGO_ENABLED=1
2. Symbol recovery step one: GoReSym v1.7.1 → **`failed to locate pclntab`** (incompatible with the newer Go layout) → dropped it and switched to an in-house tool
3. Manual pclntab parsing: scanned `.gopclntab` for magic `0xFFFFFFF1` to locate the pcHeader (file_off=10,155,296), read nfunc=15,684 / nfiles=1,062 / the offsets of each subtable
4. Locating functab: pclntab+72 was zero-filled (expected failure); switched to brute-force location by "enumerating candidate offsets + entryoff/funcoff structural validation" (file_off=12,921,688), and exported all `va/entryoff/name`
5. Disassembly aggregation: capstone x86-64 disassembled function by function, `call rel32` targets were looked up in the functab table for function names (including `+offset` inline annotations); three string resolution strategies: `[E]` exact LEA + length immediate pairing, `[V]` descriptors (ptr,len), `[R]` printable window fallback → 2,418 lines of pseudocode for 208 project functions
6. Logic rebuild: grouped the 208 functions into 9 modules by call graph + strings (startup lifecycle/config/store/report/claude/cursor/pricing/netx/front-end interface); runtime behavior was triangulated with "time constants + string constants + call chains" (such as the 5h=18e12 ns block, 20s timeout, 1.5s retry)
7. Byte-level recheck of key chains: wrote a `probe_func.py` single-function probe (header constants/error messages/lengths all locked), for example `User-Agent: token-meter/1.0` (len=15 confirmed by `mov [rax+8],0xf`)
8. Data model: extracted the DDL of 5 business tables (entries/raw_lines/sessions/files/kv) + indexes from `CREATE TABLE` strings; confirmed incremental scanning (files.offset position), idempotent upsert, WAL pragma
9. Delivery: mermaid architecture diagram + pseudocode of 30+ key functions (traceable by VA/line number) + full report; case-review `--strict --verify-hashes` → **0 error / 0 warning PASS**

## Evidence chain summary (redacted)
| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-001 | n/a | observed | command | `sha256sum <target>.exe` + BuildInfo extraction | F-001 |
| E-002 | n/a | validated | script | `python scripts/pclntab_parse.py <exe>` (magic scan) | F-002 |
| E-003 | n/a | validated | script | `python scripts/pclntab_find_ftab.py <exe>` (brute-force location by structural validation) | F-002 |

## Finding / Path summary
- top_finding: for newer stripped Go PEs where GoReSym fails, "magic scan + brute-force functab location by structural validation + capstone call-rel32 lookup" fully recovers function names; combined with exact string length pairing (LEA + mov len), header constants/error messages can be recovered at byte level
- path_type: solve
- path_one_liner: locate pclntab by magic → brute-force functab → full disassembly + string aggregation → group modules by call graph → byte-level verification with single-function probes → deliver architecture diagram/pseudocode/report

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| GoReSym `failed to locate pclntab` | The tool's compatibility with the newer Go (1.24.x) layout is insufficient | An in-house Python parser (magic 0xFFFFFFF1 scan + header field parsing) | 1h |
| functab not at pclntab+72 | That region is zero-filled; the layout after the header differs from the assumption | Brute-force location with enumerated candidate offsets + the double check "entryoff monotonic + funcoff resolves to known function names" | 0.5h |
| A temporary script using the flat mapping `va-0x400000+0x1c00` produced garbled strings | Holds only for .text and fails across sections (.rdata/.data) | Always use the pefile section mapping (va_to_off) | 0.3h |
| `probe_func.py` truncated FetchLimits to 0x400 bytes | Assumed the jsonl had off/size fields (it has only va/entry_off/name) | Binary search over sorted VAs for the next function entry and use the difference as the function size | 0.3h |
| Bash pipe output containing CJK was marked `[Binary output]` | Terminal encoding (GBK) problem | Always write to a file + read it with the Read tool, never pipe directly | 0.2h |
| 9 evidence records were written into the same E-001.md by mistake | Did not follow the "one record per file + title matches file name" contract | Split into separate files E-001..E-009 (the review_case contract is already stressed in the template; still needs care) | 0.3h |
| String extraction mixed in lots of standard library noise | Go stores all constants together | Only [E] strings with "near-function window + exact length match" are used for conclusions | 0.5h |

## Toolchain findings
- **GoReSym v1.7.1**: fails to locate pclntab for Go 1.24.4 + `-trimpath -s -w` samples → this scenario needs manual parsing
- **capstone** (Python): stable x86-64 disassembly; `call rel32` → looking up the target VA in the function table names the call (including inline offsets)
- **pefile**: section mapping (VA→file offset) is the prerequisite for string/data parsing
- The in-house trio is reusable: pclntab parsing / brute-force functab location / function-level disassembly + string aggregation (see the script pattern below)

## Key code/commands

```
# 1) Locate pclntab: scan for magic 0xFFFFFFF1 (little-endian bytes F1 FF FF FF)
#    parse pcHeader: magic, pad, minLC, ptrSize, nfunc, nfiles, textStart, funcnameOff, cuOff, filetabOff, pctabOff, pclnOff
python scripts/pclntab_parse.py <target>.exe

# 2) Brute-force functab: read the {entryoff u32, funcoff u32} array at candidate offsets
#    validate: entryoff strictly increasing; funcoff points into the funcnameOff area, and funcnameOff resolves the "runtime." prefix
python scripts/pclntab_find_ftab.py <target>.exe

# 3) Full disassembly + string aggregation ([E] exact LEA+len pairing / [V] descriptors / [R] raw window)
python scripts/disasm_funcs.py <target>.exe evidence/funcs_all.jsonl evidence/pseudocode_raw2.txt

# 4) Byte-level single-function probe (header constants / error messages / immediate lengths)
python scripts/probe_func.py <target>.exe evidence/funcs_all.jsonl "<pkg>.<Func>" out.txt

# 5) Consistency recheck (cross-links among the four tables: evidence/work items/timeline/report)
python skills/case-review/scripts/review_case.py work/<case> --verify-hashes --strict
```

## Improvement suggestions for this package
- `seed-002_go-malware-stripped` could add a "manual pclntab/functab recovery after GoReSym fails" branch, including the idea of brute-force functab location by structural validation
- tool-index should note the known version limit of GoReSym (1.7.1 reports `failed to locate pclntab` for some Go ≥1.24 samples)
- Reusable script entries could be added: `pclntab_parse.py` / `pclntab_find_ftab.py` / `disasm_funcs.py` (proven in this case)
- The evidence contract "one record per file, title = file name" works well but is easy to trip on (the template already hints at it; consider giving a fix example directly in the case-review error message)

## Reusable patterns/script snippets
- **Three-step full symbol recovery for stripped Go PEs**: magic scan → (if +72 fails) brute-force functab location by structural validation → name calls by call rel32 lookup
- **Byte-level string recovery**: the LEA instruction of a Go string constant is directly followed by a `MOV reg, len` immediate → exact (pointer, length) pairing; an order of magnitude more trustworthy than a bare window scan
- **Triangulating runtime constants**: crossing `time` constants (ns bignums) + string constants + the call graph recovers behavioral parameters (timeouts/retries/block lengths) with high confidence even without running anything
- **Recognizing the Windows credential chain**: `Local State → os_crypt.encrypted_key → base64 → DPAPI → AES-GCM("v10")` is a common fingerprint of Chromium-based applications; an import of `CryptUnprotectData` is enough to anticipate it

## Evolution actions
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added a pitfalls record (the pitfall table in this file)
- [ ] No update needed

## Environment information
- OS: Windows 10.0.26300 (x64, Git Bash)
- Tool versions: GoReSym v1.7.1 (dropped), capstone (pip), pefile, Python3
- Target platform/version: PE32+ x86-64, Go 1.24.4, Wails v2.11.0, strip+trimpath

## Redaction requirements
Handled per anonymization.md: no real username paths, no token/credential values, no private domains; the target is referred to as `{target_app}`.

---
<!-- [Evolution statistics] Projects completed by this package: 22 | New patterns this time: 4 | Toolchain problems fixed this time: 0 -->
<!-- [Community contribution] When done, ask the user whether to open a PR to the main repository. The process is in CONTRIBUTE-BACK.md -->
