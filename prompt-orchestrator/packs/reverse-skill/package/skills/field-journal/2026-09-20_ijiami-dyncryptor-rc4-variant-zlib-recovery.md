# 2026-09-20 Recovering the iJiami Packer dyncryptor RC4 Variant + zlib Decryption Chain

## Scenario classification

APK reverse engineering (recovering the custom decryption chain of a commercial packer)

## Target overview

Offline static reverse engineering of an owner-authorized Bazi chart Android APK ({target_package}, sha256 {sample_sha256}): confirmed whether the Java business layer is recoverable, recovered the packer's custom decryption pipeline, and collected the UI contract for a native rebuild by the authorizing party. A single sample offline throughout, never touching production.

## Scope summary (redacted)

- auth_basis: owner-authorized sample + authorized rebuild context, offline static analysis only
- network_profile: offline
- asset_types: [Android APK (~89 MB), native .so (arm32/x64), DEX overlay encrypted region, encrypted blobs, asset dataset]

## Roles

- lead_role: lead (case management, evidence registration, report closeout)
- specialists: [cre (static reverse engineering), doc (closeout documentation)]

## Complete execution chain

1. case-init + scope (offline / anonymize / low), set three goals and the red lines.
2. apktool baseline decode (E-001): Application=`s.h.e.l.l.S`, 124 activities, no business Java; libjgdtc / libijmDataEncryption{,_x64}.so → initial packer verdict.
3. Picked up the iJiami metadata blob left from the first round (E-002, 208 B marker prefix).
4. r2 recon of the x64 loader (E-003/E-004/E-007): stripped PIE, NX partial-RELRO, zlib/dlopen imports, no network imports; a 6-byte indirect thunk `fcn.00002de0: jmp qword [0x3ff48]` → VMP signs (F-004 candidate).
5. UI collection on a real device (E-016): dumpLayout pinned the launch Activity and the root node contract.
6. arm32 chain (E-005/E-006/E-012): overlay magic xrefs located the JNI chain fcn.00012e60 → KSA fcn.00012788 → PRGA fcn.00012834; identified a computed-jump opcode dispatch interpreter (VMP-style).
7. Manual overlay parsing (E-008): a 21,499,724 B overlay after stub_end 0x3a70, 3 records (r1 2,420,690 B @0x4020 entropy 7.999927; r2 19,037,852 B; r3 39,708 B), magic `71680001`, shared prefix `632337b8`.
8. **Full dyncryptor decryption (E-009/E-010/E-011)**: RC4 variant KSA (i=3, j=5, i+=2, j+=state[i]+1) + KEY {key_hex} + zlib to EOF; arm32 678,676 B → 1,260,533 B, x64 926,149 B → 2,257,585 B, verified independently on both architectures (F-003 validated/high).
9. Detour one: assets/bttets (698 files) was first judged an algorithm dataset; full hash fingerprinting confirmed that every file is a 1-byte 0x20 placeholder (E-013) → conclusion that the Java layer is unrecoverable (F-002 / F-005).
10. Detour two: dynamic confirmation with unidbg (E-017) captured 0 bytes, older than the source mtime → recorded truthfully as INCOMPLETE (F-007 candidate/low); the static conclusions stand on their own.
11. Closeout: 17 evidence entries registered immutably (append-evidence.ps1), 7 findings + 2 paths, 10 timeline entries, a 5-section English report, this journal.

## Evidence chain summary (redacted)

| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|---|---|---|---|---|---|
| E-009 | info | observed | command | A home-made unpacking script RC4-variant decrypts the blob + zlib to EOF; the output sha256 is on record | F-003 |
| E-011 | info | observed | command | After r2 `-A`, `pdf @ KSA function` extracts the stepping (i+=2 / j+=state[i]+1 / initial values 3,5) | F-003 |
| E-013 | info | observed | command | A full sha256/crc32 histogram identifies the placeholder dataset (698 × the same hash → 0x20 placeholder) | F-005 |

> Contract alignment: all 17 evidence entries were registered immutably through `append-evidence.ps1` (severity=info / status=observed / source_type=command; the actual severity is carried by the findings); this table lists only the 3 most important entries of the decryption chain; see the case `evidence/INDEX.md` for the full set.

## Finding / Path summary

- top_finding: F-003: the dyncryptor pipeline (RC4 variant KSA/PRGA + zlib) fully recovered, validated / high
- path_type: solve
- path_one_liner: manual overlay parsing locates the encrypted blob → read the KSA variant stepping and KEY statically → a home-made script reproduces the decryption offline on both architectures (P-002)

## Pitfall record

| Problem | Cause | Solution | Time |
|---|---|---|---|
| bttets misjudged as a Bazi algorithm dataset | All 698 files are same-size 1-byte 0x20 placeholders; single-file spot checks are unreliable | A full sha256/crc32 histogram + comparison of the whole payload_hex set nailed the placeholders | ~0.5h |
| unidbg captured 0 bytes | The capture timestamp was older than the harness source mtime; the run aborted before producing observable output | Recorded truthfully as INCOMPLETE (F-007) without blocking the static conclusions; lesson: verify that a capture file is non-empty + check its mtime before trusting it | ~1h |
| apktool stopped before the iJiami overlay | The custom overlay layout is not a standard zip/dex structure | A home-made parser cut it manually by magic + record header (offset/size) | ~1h |

## Toolchain findings

- radare2 6.2.2 is stable on an 89 MB APK + 21 MB overlay; batch output of `recon.ps1` can go straight into evidence.
- apktool does not parse the iJiami overlay: the baseline decode (manifest/res) still works, but the encrypted region must be handled manually.
- Immutable registration with `append-evidence.ps1` + contract checks with `review_case.py` make the evidence chain machine-auditable; worth keeping.
- unidbg easily fails silently when resolving the default file system for the iJiami packer; no output ≠ success.

## Key code/commands

(Illustration of identifying features, not runnable; the authoritative implementation is in the case evidence E-008..E-011 and the report)

```python
# Identifying features of the iJiami dyncryptor RC4 variant (arm32 KSA fcn.00012788, x64 isomorphic)
i, j = 3, 5                          # non-standard initial values (textbook RC4 uses 0, 0)
while i < 256:
    j = (j + state[i] + 1) & 0xFF    # non-standard stepping (textbook RC4 uses j + state[i])
    i += 2                           # non-standard step size
    state[i], state[j] = state[j], state[i]
# KEY is a 10-byte hard-coded {key_hex}
# the keystream is then zlib-decompressed to EOF
# Dual-architecture verification: arm32 blob@0x44514 678,676 B → 1,260,533 B; x64 blob@0x343b0 926,149 B → 2,257,585 B
```

## Improvement suggestions for this package

1. `append-evidence.ps1` should validate the evidence-relative path prefix of repro_command (the repro of E-003..E-006 in this case lacks the `evidence\` prefix, and immutable registration makes it impossible to fix afterwards).
2. For unidbg / dynamic tools, add a "capture validity must-check" to pitfalls: the output is non-empty + the capture mtime is later than the source mtime.
3. Use neutral wording for workitems coverage statements (for example "Report via docs-generator" → "Report authored per closeout contract"), so the checked items do not contradict the facts.

## Reusable patterns/script snippets

1. **Manual overlay parsing pattern for packers**: when apktool stops at the encrypted region, read the offset at the end of the DEX stub (stub_end) → scan for the magic → cut by record header (offset/size) → confirm encryption by entropy. In this case stub_end=0x3a70, magic=0x71680001.
2. **RC4 variant signals**: i+=2, j+=state[i]+1, initial values i=3/j=5 in the KSA/PRGA mean a variant; rewrite from the actual instructions instead of applying the textbook implementation.
3. **Hash fingerprinting of placeholder datasets**: for masses of small files, build a full sha256 histogram first; the same hash × N means placeholders, which spares manual analysis file by file.

## Evolution actions

- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [ ] Added a pitfalls record
- [x] No update needed

## Environment information

- OS: Windows + PowerShell 5.1
- Tool versions: radare2 6.2.2 (commit ad27058…), apktool, Python 3 (home-made parsing/unpacking scripts), unidbg (tentative use)
- Target platform/version: Android APK; iJiami commercial packer; UI collection on a real Android device (API 26)

## Redaction requirements

This file is redacted per [`anonymization.md`](anonymization.md):

- Placeholders: {target_package} / {sample_sha256} / {key_hex}
- Not included: device model/serial number, real package name/bundleName, the full KEY, plaintext blob sha256 values, any real user data
- Kept: tool names + versions, function names/offsets, magic/structural features, pattern conclusions (public technical information)

## Index sync

- [x] Added an entry under "By scenario → APK / Android reverse engineering"
- [x] Added an "Android packer custom decryption chain" subsection to "Frequent success patterns"
- [x] Added an "iJiami packed APK" subsection to the "Entity inverted index"
- [x] Updated "Cumulative statistics" (real projects 22 / total entries 39 / last updated 2026-09-20)

---

<!-- [Evolution statistics] Projects completed by this package: 22 | New patterns this time: 1 | Toolchain problems fixed this time: 0 -->
