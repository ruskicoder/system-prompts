# [seed] Reverse Engineering an ELF Self-Extracting Loader

## Scenario classification
Binary analysis

## Target overview
Analyze an ARM64 ELF self-extracting loader disguised as a .sh script, recovering its decompression algorithm and payload injection flow.

## Complete execution chain

1. The `file` command confirms the real type (ELF, not a shell script)
2. `readelf -l` shows the program headers → the 3rd PHDR is deliberately corrupted (filled with 0x0a)
3. `rabin2 -I` gets the architecture (AArch64), entry point and compiler information
4. Load in IDA/Ghidra → analyze from the entry point
5. Identify the LZSS decompression loop (bit stream operations + sliding window back-copy)
6. Identify the injection flow mmap → decompress → mprotect → jump
7. Rewrite the decompressor in Python and dump the payload
8. Analyze the payload content (contains a /proc/self/exe reference, indicating a process injector)

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| readelf errors and cannot parse | The 3rd PHDR is deliberately filled with 0x0a | Ignore the corrupted PHDR and look only at the first 2 LOAD segments | 10min |
| IDA decompilation output unreadable | Dense ARM64 bit operations, poorly optimized by Hex-Rays | Switch to the disassembly view and analyze manually | 30min |
| The Python decompressor outputs wrong data | The pop_bit refill path return value was wrong (adcs vs adds) | Compare carefully with the assembly; on refill it returns bit31 of the newly loaded word | 2h |
| Unsure of the payload entry offset | The meaning of the entry_offset field in the data table is unclear | Follow the loader's `br mmap_base + 0x14` to confirm the entry is at +0x14 | 20min |

## Toolchain findings

- The `file` command is the first step; never trust the file extension
- `rabin2 -I` is more fault-tolerant than `readelf` (handles corrupted PHDRs)
- For code dense with ARM64 bit operations, reading the assembly directly beats the decompiler
- The Python struct module + a hand-written decompressor is the standard method for analyzing custom compression

## Key code/commands

```bash
# confirm the file type
file LinYuDriverLoader4.9.sh
# ELF 64-bit LSB executable, ARM aarch64

# view the program headers
readelf -l binary 2>/dev/null | head -20

# extract the compressed data
dd if=binary bs=1 skip=$((0xa6a24)) count=1981 of=compressed.bin

# compute the file offset
# vaddr 0x3d66bc → file_offset = 0x3d66bc - 0x330000 = 0xa66bc
```

```python
# LZSS decompressor core (simplified)
def decompress(data):
    shift_reg = 0x80000000
    # ... bit stream reading + literal/match branches
```

## Improvement suggestions for this package

- `elf-analysis.md` should add more features for "identifying custom compression algorithms"
- The ARM64 syscall table should include notes on cache maintenance instructions (dc cvau / ic ivau)
- Suggest adding a general methodology for "rewriting assembly algorithms in Python"

## Reusable patterns/script snippets

**Standard pattern for identifying a self-extracting ELF**:
```text
entry point → little initialization → call the decompression function → mmap(RW) → decompress into the mmap region → mprotect(RX) → jump
```

**General pattern for ARM64 bit stream reading**:
```text
lsl w4, w4, #1    # shift left (extract the top bit into carry)
cbz w4, refill    # if shifted empty, load a new 32 bits from the input
```

## Evolution actions
- [x] Updated sub-skill documentation (elf-analysis.md added)
- [ ] No routing matrix update needed
- [ ] No bootstrap-manifest update needed

## Environment information
- OS: Linux/Android ARM64 target
- Tool versions: IDA Pro / Ghidra + radare2
- Target platform: Android ARM64 (AArch64)

## Redaction requirements
This entry is seed data, written from public technical patterns, with no real target involved.

---
<!-- [Community contribution] Seed data, no PR needed -->
