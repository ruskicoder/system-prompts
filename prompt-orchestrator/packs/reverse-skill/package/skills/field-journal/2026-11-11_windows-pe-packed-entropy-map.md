# 2026-11-11 Static Mapping of a Heavily Packed Windows PE

## Scenario classification

Binary analysis / comprehensive triage of a packed PE sample (pure static, offline)

## Target overview

Ran a comprehensive static analysis of a local ~60 MiB Windows x64 GUI executable, determining the software identity, the protection structure and the inferable risk boundary, and stating clearly which conclusions cannot be drawn.

## Scope summary (redacted)

- auth_basis: owner-operated (local offline sample, offline-sample preset)
- network_profile: offline (no outbound packets)
- asset_types: [local_pe_binary, sibling_executables_readonly]

## Roles

- lead_role: lead
- specialists: [cre]

## Complete execution chain

1. `master-route.ps1` → PRIMARY = R0 general reverse engineering (confidence low, no strong keyword hit); in parallel, `case-init.ps1 -Preset offline-sample` set the scope, auth=granted / network=offline / ready_for_act=true.
2. Read `scope-contract.md`, `re-agent-workflow.md`, `precedent-reverse.md`, `tool-index.md`; confirmed r2/rabin2/Python are available and IDA/Ghidra/YARA missing → the dynamic unpacking path is out of reach this time.
3. Manual PE header parsing in the first round: x86-64 PE32+ / 10 sections / 6 sections with RawSize=0 / a single 60 MiB full-entropy section / EP inside the encrypted section → judged a memory-restoring heavy packer.
4. Cross-verified the import table with rabin2 (Triage hard gate): only 6 DLLs / 7 APIs; manually recovered the truncated 7th; labeled `quality=packed/decoy`.
5. Manually parsed the resource directory tree → the version information gave the software's real name, version and language; extracted 7 PNG icons and the manifest.
6. Statistical encryption verdict: 4 MiB entropy, printable ratio, χ², repeated 16B blocks, single-byte XOR brute force, scan for known packer markers.
7. Full-payload entropy map with 64 KiB windows → located the code block address table, the metamorphic x64 stub area and the trailing RVA range table.
8. Survey of low-entropy island contents → confirmed 6-byte (u32 RVA + u16 flag) records and machine code generated with REX+push/pop.
9. Read-only structural comparison with sibling exes in the same directory → environmental corroboration (without expanding their contents).
10. Generated E-001~E-010 / F-001~F-007 / P-001; `review_case.py --strict` validation PASS (0 error / 0 warning); produced a formal Markdown report + an HTML visual report.

## Evidence chain summary (redacted)

| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-002 | high | observed | command | `python static_analyze.py` (PE header / section table / EP mapping) | F-001 |
| E-003 | high | observed | command | `rabin2 -i sample.exe` + manual IMAGE_IMPORT_DESCRIPTOR | F-003 |
| E-006 | high | observed | command | `python context_analyze.py` (entropy / printable ratio / XOR brute force) | F-001 |

## Finding / Path summary

- top_finding: a commercial-grade memory-restoring heavy packer; 99.8% of the content is encrypted and cannot be audited statically; the decoy minimal IAT must not be used to rule out capabilities.
- path_type: callflow
- path_one_liner: loader maps the virtual sections → fills the decoy IAT → enters the EP in the encrypted section → looks up the code block mapping table → resolves the real APIs dynamically → decrypts and writes back the original image → executes through metamorphic stubs (structural inference, not verified dynamically).

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| `rabin2` reports `Cannot open file` with a garbled path | Windows-side tools interpret the command line as ANSI and corrupt Chinese file names | Made a read-only copy with a pure ASCII name in the case directory, verifying that the SHA256 matches first | 5 min |
| `pefile` reports `module has no attribute DIRECTORY_TYPE` | The constant was renamed/removed in version 2024.8.26 | Do not depend on py constants; parse the 20-byte IMAGE_IMPORT_DESCRIPTOR structure by hand | 5 min |
| Python `SyntaxError: bytes can only contain ASCII` | Chinese keywords were written inside a bytes literal | Generate Chinese strings with `x.encode("utf-8")` | 2 min |
| Entropy function `NameError: math` | The new script missed an import | Added the import and reran | 1 min |
| The first read of ImageBase gave 0x40000000 (wrong) | The PE32+ ImageBase is 8 bytes, but `<I` read 4 bytes by mistake | Changed to `<Q`, correct value 0x140000000; also read subsystem as 2 bytes, not 4 | 3 min |
| gzip/zlib/MZ magic numbers hit 900+ times in the payload, nearly misjudged as nested archives | The expected number of hits of a 2-byte magic in 60 MB of uniform random data is about 960 | Added an "expected hits" comparison and cross-verification with entropy/repeated blocks; judged a random coincidence | 8 min |
| The first marker scan showed `UPX`, suspected a UPX packer | A 3-byte short string hits occasionally in 60 MB | Checked UPX section headers/section names/entry stub, none present → ruled out, written into evidence to avoid a false report | 3 min |

## Toolchain findings

- Available: `rabin2 6.2.4`, `Python 3.13.15` (`pefile 2024.8.26`, `capstone 5.0.9`). Manual struct parsing handles packer-tampered PEs more reliably than pefile.
- Missing: IDA Pro, Ghidra, x64dbg, YARA, Frida → the "unpack → fix IAT → decompile" path is unavailable; work can only stop at static triage + structural mapping.
- Comparing `cmp.csum` from `rabin2 -I` with the PE header `checksum` field is a low-cost signal for recognizing "packer-rebuilt headers".
- `rabin2 -z` outputs only noise strings in full-entropy sections; combine it with entropy filtering and do not use the output directly as IOCs.

## Key code/commands

```bash
# Chinese path → ASCII copy (verify the hash first)
cp "{local_sample}" "{case_root}/sample.exe" && sha256sum "{case_root}/sample.exe"

# Triage hard gate
rabin2 -I sample.exe; rabin2 -i sample.exe; rabin2 -E sample.exe

# four rounds of home-made mapping
python static_analyze.py     # header / sections / entropy / data directories / IOCs
python deep_analyze.py       # import descriptors / resource tree / version / disassembly
python context_analyze.py    # entropy statistics / sibling sample comparison / anomaly list
python payload_map.py        # 64 KiB entropy map / trailing index table
python islands.py            # low-entropy island survey

# evidence chain validation
python review_case.py "{case_root}" --verify-hashes --strict
```

## Improvement suggestions for this package

- R0 in `routing.json` gives only a low confidence fallback for requests like "analyze this software / sample comprehensively"; add a keyword group for "comprehensive PE sample triage / software composition analysis", or give explicit combination guidance "unknown PE → R9 six-phase method + R0 mapping" in the three-axis appendix of `routing.md`.
- Missing Windows dynamic tools in `tool-index` were the main external reason this run stopped at static analysis; the documentation could state up front "the ceiling of static mapping without IDA/x64dbg", to avoid the impression that the analysis is incomplete.
- Write "the expected number of hits of short magic numbers in full-entropy data" into the triage recipes, so random coincidences are not taken as container evidence.

## Reusable patterns/script snippets

1. **Virtual section detection**: the number of `RawSize=0` sections in the section table + whether the EP falls inside the single large section → identifies a memory-restoring packer.
2. **Encryption verdict trio**: Shannon entropy (≥7.99), the printable ASCII ratio compared with the theoretical 37.11%, the number of repeated 16B blocks (ECB detection) → separates "encrypted" from "plaintext/simple XOR".
3. **Locating packer metadata with an entropy map**: a 64 KiB sliding window scan; low-entropy islands are usually the packer's code block mapping table / range table / metamorphic code area.
4. **Decoy IAT recognition**: total APIs < 20 with no business relation across DLLs → label `quality=packed/decoy` and forbid ruling out capabilities on that basis.
5. **Evidence chain self-check**: in the report, `### F-xxx` carries `evidence_ids` and `### P-xxx` carries `E-xxx` references, so `review_case.py --strict` passes with zero warnings.

## Evolution actions

- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added a pitfalls record (this file)
- [ ] No update needed

## Environment information

- OS: Windows (win32, Git Bash + PowerShell 5.1)
- Tool versions: radare2 6.2.4 / Python 3.13.15 / pefile 2024.8.26 / capstone 5.0.9
- Target platform/version: Windows PE32+ x86-64 GUI, commercial-grade third-party protection packer

## Redaction notes

This record contains no real domains, IPs, tokens, usernames or intranet addresses; sample paths are always the placeholders `{local_sample}` / `{case_root}`, the software name is generalized as "local PE sample", and hashes stay only in the evidence directory of the user's project.

<!-- [Evolution statistics] Projects completed by this package: 22 | New patterns this time: 5 | Toolchain problems fixed this time: 0 -->
<!-- [Community contribution] When done, ask the user whether to open a PR to the main repository. The process is in CONTRIBUTE-BACK.md -->
