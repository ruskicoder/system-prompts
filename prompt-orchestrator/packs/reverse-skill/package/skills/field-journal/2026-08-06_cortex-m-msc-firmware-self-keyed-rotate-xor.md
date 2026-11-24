# 2026-08-06 Self-Keyed Rotate/XOR Wrapping of Cortex-M Virtual Disk Update Firmware

## Scenario classification

Binary / firmware reverse engineering

## Target overview

Analyzed the update package of a Cortex-M debugging tool, identified its custom wrapping algorithm, and separated the application image in the update package from the USB Mass Storage bootloader resident on the device.

## Scope summary (redacted)

- auth_basis: own_system
- network_profile: authorized_target_only (actually a local offline sample)
- asset_types: [firmware_container, cortex_m_application, usb_msc_updater]

## Roles

- lead_role: lead
- specialists: [cre, cce, doc]

## Complete execution chain

1. Ran length, entropy, tail period and per-block statistics on the original package and found that the file size is a multiple of 1 KiB and the tail has a 7-byte period.
2. Starting from the Cortex-M vector table constraints, enumerated single-byte rotate/XOR relations and recovered the first block.
3. Found that each 1 KiB block resets the rotation phase and that the first ciphertext byte of each block can serve directly as that block's XOR mask.
4. Decoded each block with `P[i] = ROR8(C[i], (3*i) mod 7) XOR C[0]` and rebuilt the original package byte for byte with the inverse transform.
5. Cross-verified with a second official firmware of the same family: the same format recovered a valid vector table, version strings and readable code; the first plaintext byte of every block is zero.
6. Derived the application base address from the vector target addresses and file offsets, confirming that the update package does not include the preceding bootloader.
7. Combined with the official "enter bootloader / emulate a USB drive" instructions, reconstructed the external flow from MSC file copy to Flash write, and marked the bootloader internals as inference.
8. Tested common CRCs, STM32 hardware CRC, Adler and sums against the 32-bit tail field without a match, and kept it as an unresolved integrity field.

## Evidence chain summary (redacted)

| E-id | source_type | Reusable command pattern | Related Finding |
|---|---|---|---|
| E-001 | local_binary | Per-block entropy, periodic tail, vector constraints | F-001 |
| E-002 | derived_algorithm | Block-head mask + ROR/XOR + round-trip | F-001 |
| E-003 | static_analysis | Vectors, strings, Thumb disassembly | F-002 |

## Finding / Path summary

- top_finding: some high-entropy firmware packages are only self-keyed ROR/XOR obfuscation that resets every 1 KiB and should not be classified as standard encryption too early.
- path_type: solve/callflow
- path_one_liner: period and block structure → vector table crib → first block recovery → block boundary reset → cross-verification with a second firmware → application/bootloader boundary → external MSC update flow.

## Pitfall record

| Problem | Cause | Solution | Time |
|---|---|---|---|
| Using each block's "most common byte after unrotation" as the mask left a few blocks garbled | The most common plaintext byte of text-dense blocks is not necessarily zero | Compared with the block-head byte model; the garbling disappeared and reproduced on the second firmware | Medium |
| A single whole-file XOR/rotation worked only at the start | The rotation phase and mask reset every 1 KiB | Split explicitly into `0x400` blocks | Low |
| IDA and radare2 failed to start | No IDA path locally, r2 bootstrap installer error | Verified the Cortex-M entry with Python + Capstone | Medium |
| Seeing `firmware_crc32` and assuming the tail is a standard CRC32 | The string is a metadata key and does not prove the tail parameters or coverage | Excluded the common families systematically and kept it unknown without forcing a name | Low |

## Toolchain findings

- Python suits bitwise transform enumeration, round-trips and cross-sample invariant verification.
- Capstone is enough to verify Cortex-M vector entries and local control flow when IDA/Ghidra/radare2 are missing.
- String recovery quality is a strong signal when comparing candidate mask models, but it must be combined with absolute pointers and disassembly instead of relying only on "it looks readable".

## Key algorithm

```text
block_size = 0x400
mask = packed_block[0]
rotation(i) = (3 * i) mod 7
plain[i] = ROR8(packed[i], rotation(i)) XOR mask
```

The inverse transform uses `ROL8`; the verification standard is that the encoded result is byte-identical to the original package.

## Improvement suggestions for this package

- Add a check for "whether the period resets at block boundaries" to the container identification phase of firmware-pentest.
- When the heuristic zero-byte crib fails on a few blocks, test self-describing masks at the block head/tail first.
- When "the update package contains only the application", the report must label bootloader internal behavior separately from behavior the protocol layer necessarily implies.

## Reusable patterns

1. First check whether the period resets at common Flash/transfer block sizes (256, 512, 1024, 2048, 4096).
2. Use the Cortex-M SRAM stack pointer and the Thumb Reset Vector as strong cribs.
3. Run three verifications on each candidate model: whole-file round-trip, reproduction on a second sample, consistent absolute address references.
4. When the tail field does not match common checksums, do not treat variable names or strings as algorithm evidence.

## Evolution actions

- [x] Added a field-journal record
- [x] Updated the field-journal index
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation

## Environment information

- OS: Windows
- Tool versions: Python 3.12, Capstone 5.0.6
- Target platform/version: Cortex-M3 / F1-compatible MCU, application area firmware

## Redaction check

- [x] No real domains, IPs, credentials, tokens, PII
- [x] No local absolute paths
- [x] No sample file or sample hash
- [x] Vendor, product and version information generalized
