# 2026-07-14 Source Recovery of an Android ARM64 Self-Extracting Program

## Scenario classification

Binary analysis / Android ARM64 / self-extracting shell / control flow flattening

## Target overview

Read-only source recovery of a user-owned local `.sh` delivery package: unpacked the multi-layer compressed payload, analyzed the ARM64 main program and the protection library, and recovered business text and high-level pseudo-source without running the target.

## Complete execution chain

1. Triaged the input directory read-only by listing, size, magic numbers and SHA-256, without reading or recording plaintext credentials.
2. Identified the first layer as "shell preamble + trailing bzip2 stream" and located the exact offset by testing for a valid `BZh` stream.
3. Saved the preamble, compressed stream and decompressed payload in a separate Chinese-named output directory without executing the payload.
4. Identified the second layer as a `__ARCHIVE_BELOW__` self-extracting script and unpacked the tar.gz safely, rejecting absolute paths, `..`, links and device nodes.
5. Obtained an Android AArch64 PIE main program and an AArch64 shared library; generated the ELF header, sections, symbols, imports, strings and entry disassembly with pyelftools/Capstone.
6. The protection library kept readable C++ symbols; exported pseudocode per function and confirmed `/proc` scanning, `TracerPid`, three-level process termination and background thread behavior.
7. The symbol length of the main program's `main` was clearly larger than the length found by ordinary CFG recognition, confirming indirect-jump control flow flattening.
8. Solved the jump table statically: `target = table_entry + fixed_delta`, enumerating every unique real basic block.
9. Scanned for isomorphic string decryptors and identified the layout "the first N bytes are a cyclic XOR key + the next M bytes are ciphertext".
10. Ran AArch64 constant propagation on each real basic block, resolved the targets of indirect decryptor calls and the `x1` data sources, and recovered the business text in bulk.
11. Delivered the complete disassembly, per-function pseudocode, high-level semantic source, Mermaid flowcharts and the formal report.
12. Recomputed the original input hashes and confirmed they were identical before and after the analysis.

## Pitfall record

| Problem | Cause | Solution | Time |
|---|---|---|---|
| Running bootstrap directly in PowerShell was blocked by the execution policy | The system forbids scripts | Use a one-off `powershell.exe -ExecutionPolicy Bypass -File ...` without changing the permanent policy | Low |
| radare2 bootstrap returned GitHub API 403 | API rate limited/refused, but the release page was reachable | Got the official assets and page SHA-256 from the `releases/latest` 302 and `expanded_assets/<tag>`, verified, then extracted | Medium |
| Neither the silent nor the user-scope Rizin winget install landed | Installer scope mismatch | Stopped retrying after two failures and went back to the verified official radare2 ZIP | Low |
| `r2pm -U` stayed in git clone for a long time | Network speed/recursive repository | Dropped the optional plugin route and continued with `pdc` + custom Capstone recovery | High |
| radare2 recognized only the front part of `main`'s CFG | The indirect BR jump table makes regular analysis stop at the dispatcher | Enumerated real blocks by the jump table formula without relying on the default CFG | Medium |
| A direct string scan showed only a few paths | Text uses an independent cyclic XOR per string | Extracted key/output lengths from the decryptor instructions and replayed the algorithm statically | Medium |

## Toolchain findings

- The Python 3.13 standard library handles bzip2 and tar.gz safely enough; `tarfile.extractall` is less safe than writing out each member after validation.
- pyelftools recovers ELF/DYNSYM/RELA, and Capstone suits ARM64 constant propagation and recognition of dedicated decryptors.
- `pdc` in radare2 6.1.8 works on unobfuscated protection library functions but only gives partial pseudocode for a main function flattened with indirect BR.
- A GitHub API 403 does not mean the official release page assets are unreachable; the release page provides the tag, asset names and SHA-256.

## Key code/commands

```python
# General cyclic XOR text layout
key = blob[:key_length]
encrypted = blob[key_length:key_length + output_length]
plain = bytes(value ^ key[index % key_length]
              for index, value in enumerate(encrypted))
```

```python
# Static solving of the indirect jump table
targets = {
    (entry + fixed_delta) & 0xFFFFFFFFFFFFFFFF
    for entry in jump_table_entries
}
```

```powershell
# Read-only retrieval of the latest tag on API 403
curl.exe -sS -I '<official-release-url>/radareorg/radare2/releases/latest'
```

## Improvement suggestions for this package

- Add a route for the "`.sh` self-extracting disguised binary" target type to avoid misjudging it as a pure shell review.
- Windows GitHub Release bootstrap should fall back to the release page/expanded_assets on API 403 and enforce SHA-256 verification.
- A general "ARM64 jump table + cyclic XOR" recovery script template could be added as a low-dependency route without IDA.
- When a tool call outlasts the foreground window, keep the session id and poll, to avoid losing downloads or exports still running.

## Reusable patterns/script snippets

1. Scan for valid compressed streams rather than only magic numbers; fully decompress each candidate offset in memory as a test.
2. Always write self-extracting archives out member by member safely; never execute them directly or trust member paths.
3. When the function length declared in the symbol table is far larger than the length CFG recognition finds, check BR/BLR indirect tables first.
4. Isomorphic decryptors can be identified in bulk through the instruction combination `add x16,x1,#key_len`, `cmp w16,#output_len`, `ldrb/eor/strb`.
5. Local constant propagation over flattened blocks is usually enough to recover indirect function targets and string source addresses without full deflattening first.

## Evolution actions

- [x] Updated the routing matrix
- [x] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added pitfall records
- [ ] No update needed

## Environment information

- OS: Windows
- Tool versions: Python 3.13; radare2 6.1.8; pyelftools; Capstone
- Target platform/version: Android ARM64, NDK r17 / Clang 6.0.2

## Redaction check

- No software name, author name, real domain, real API endpoint, credential, fixed signing material, business package name or local user path is recorded.
- No sample file or sample hash is attached.
- Only public tool names, versions and general algorithm patterns are kept.

## Index sync

Added this record to the "Binary / firmware / CTF" category of `_index.md` and updated the statistics.

---
<!-- [Community contribution] When done, ask the user whether to open a PR to the main repository. The process is in CONTRIBUTE-BACK.md -->
