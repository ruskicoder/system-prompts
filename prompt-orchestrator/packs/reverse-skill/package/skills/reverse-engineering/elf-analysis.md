# ELF Binary In-Depth Analysis Reference

> Structure parsing, anti-analysis identification and analysis techniques for reversing Linux/Android ELF files.

---

## ELF structure quick reference

### File header (ELF Header)

```text
Offset  Size  Field              Description
0x00  4    e_ident[EI_MAG]   Magic: 7f 45 4c 46 ("\x7fELF")
0x04  1    e_ident[EI_CLASS] 1=32bit, 2=64bit
0x05  1    e_ident[EI_DATA]  1=LE, 2=BE
0x10  2    e_type            2=EXEC, 3=DYN(PIE/SO), 4=CORE
0x12  2    e_machine         0x03=x86, 0x3E=x86_64, 0xB7=AArch64, 0x28=ARM
0x18  8    e_entry           entry point virtual address
0x20  8    e_phoff           program header table offset
0x28  8    e_shoff           section header table offset (may be 0 after strip)
0x38  2    e_phnum           number of program headers
0x3C  2    e_shnum           number of section headers
```

### Program Header

```text
Type value  Name       Description
0x01   PT_LOAD    loadable segment (code/data)
0x02   PT_DYNAMIC dynamic linking information
0x03   PT_INTERP  interpreter path (/lib/ld-linux.so)
0x04   PT_NOTE    auxiliary information
0x06   PT_PHDR    the program header table itself
0x6474e550 PT_GNU_EH_FRAME  exception handling
0x6474e551 PT_GNU_STACK     stack executable flag
0x6474e552 PT_GNU_RELRO     read-only relocations
```

### Common sections

| Section name | Description |
|------|------|
| `.text` | Code segment |
| `.rodata` | Read-only data (string constants) |
| `.data` | Initialized global variables |
| `.bss` | Uninitialized global variables |
| `.plt` / `.got` | Dynamic linking jump tables |
| `.init_array` | Constructor pointer array |
| `.fini_array` | Destructor pointer array |
| `.dynamic` | Dynamic linking information |
| `.symtab` / `.dynsym` | Symbol tables |
| `.strtab` / `.dynstr` | String tables |

---

## Identifying anti-analysis techniques

### Common ELF anti-analysis techniques

| Technique | Trait | Countermeasure |
|------|------|---------|
| Corrupted program headers | PHDR filled with junk data (such as 0x0a) | Repair manually or ignore the corrupted PHDR |
| No section header | `e_shoff = 0`, `e_shnum = 0` | Rely only on program header analysis, not on sections |
| Stripped symbols (strip) | No `.symtab`, all function names lost | GoReSym(Go) / signature matching / FLIRT |
| Static linking | No `.dynamic`, very large | Identify library functions with FLIRT/Lumina |
| Disguised file type | Extension .sh/.txt/.jpg | Decide with the `file` command / magic bytes |
| UPX packing | Contains the `UPX!` marker | Unpack with `upx -d` |
| Custom packer | The entry point jumps to decompression code | Run dynamically to the OEP and dump |
| Anti-debugging | ptrace(TRACEME) | LD_PRELOAD hook / patch |
| Anti-VM | Checks /proc/cpuinfo | Modify cpuinfo or hook the read |
| Code encryption | .text decrypted at runtime | Break after decryption and dump |

### Identifying self-extracting/self-modifying code

```text
Traits:
1. An mmap(PROT_READ|PROT_WRITE|PROT_EXEC) call near the entry point
2. Immediately followed by memcpy or a copy loop
3. Then mprotect changes the permissions
4. Finally br/jmp to the newly mapped address

Analysis strategy:
1. Find the mmap call → record the returned address
2. Set a breakpoint after mprotect(PROT_EXEC)
3. Dump the decompressed memory region
4. Analyze it as a new binary
```

---

## ARM64 (AArch64) reverse engineering quick reference

### Registers

| Register | Purpose |
|--------|------|
| x0-x7 | Arguments/return value |
| x8 | Indirect result (syscall number) |
| x9-x15 | Temporary registers |
| x16-x17 | IP0/IP1 (PLT jumps) |
| x18 | Platform register (Android: shadow call stack) |
| x19-x28 | Callee-saved |
| x29 (FP) | Frame pointer |
| x30 (LR) | Link register (return address) |
| SP | Stack pointer |
| PC | Program counter |

### Common instruction patterns

```text
Function prologue:
  stp x29, x30, [sp, #-N]!    # save FP and LR
  mov x29, sp                  # set the frame pointer

Function epilogue:
  ldp x29, x30, [sp], #N      # restore FP and LR
  ret                          # return (br x30)

System call:
  mov x8, #NR                  # syscall number
  svc #0                       # trigger the syscall

Conditional branches:
  cmp x0, #0
  b.eq label                   # jump if equal
  b.ne label                   # jump if not equal
  cbz x0, label                # jump if x0 == 0
  cbnz x0, label               # jump if x0 != 0

Address loading:
  adrp x0, page                # load the high bits of the page address
  add x0, x0, #offset          # add the low 12-bit offset
  ldr x0, [x1, #offset]        # load from memory
```

### Linux ARM64 system call numbers

| Number | Name | Description |
|------|------|------|
| 56 | openat | Open a file |
| 63 | read | Read |
| 64 | write | Write |
| 57 | close | Close |
| 222 | mmap | Memory mapping |
| 226 | mprotect | Change memory permissions |
| 117 | ptrace | Process tracing |
| 220 | clone | Create a process/thread |
| 221 | execve | Execute a program |
| 93 | exit | Exit |
| 94 | exit_group | Exit the process group |

---

## Identifying common compression/packing algorithms

| Algorithm | Identification traits | Decompression |
|------|---------|---------|
| **LZSS** | Bit stream + literal/match markers | Custom decompressor (as in this report) |
| **ZLIB/Deflate** | Magic: `78 01`/`78 9C`/`78 DA` | `zlib.decompress()` |
| **GZIP** | Magic: `1F 8B` | `gzip -d` / `gunzip` |
| **LZ4** | Magic: `04 22 4D 18` | `lz4 -d` |
| **LZMA/XZ** | Magic: `FD 37 7A 58 5A 00` (XZ) | `xz -d` / `lzma -d` |
| **Brotli** | No fixed magic, judge by context | `brotli -d` |
| **Zstandard** | Magic: `28 B5 2F FD` | `zstd -d` |
| **UPX** | String `UPX!` | `upx -d` |
| **Custom** | Decompression loop at the entry point | Reverse the algorithm, then write a decompressor |

### Clues of custom compression

```text
1. A loop + bit operations (shift, AND, OR) near the entry point
2. A "sliding window" back-copy (reading back from the output buffer) → LZ family
3. A frequency table/Huffman tree construction → Deflate/Huffman
4. Fixed-size block processing → block compression (LZ4/Snappy)
5. Arithmetic coding traits (interval narrowing) → LZMA/ANS
```

---

## Linux process injection techniques

### mmap + code injection

```text
Flow:
1. mmap(NULL, size, PROT_READ|PROT_WRITE, MAP_ANON|MAP_PRIVATE, -1, 0)
2. Write the shellcode/payload into the mapped region
3. mprotect(addr, size, PROT_READ|PROT_EXEC)  # make it executable
4. Jump to the mapped address and execute

Traits:
- The mmap return value is saved
- Immediately followed by memcpy or a write loop
- Then mprotect changes the permissions
- Finally br/blr to that address
```

### ptrace injection

```text
Flow:
1. ptrace(PTRACE_ATTACH, target_pid)
2. waitpid(target_pid)
3. ptrace(PTRACE_GETREGS, target_pid, &regs)
4. Modify regs.pc to point at the injected code
5. ptrace(PTRACE_SETREGS, target_pid, &regs)
6. ptrace(PTRACE_CONT, target_pid)

Traits:
- Open /proc/<pid>/mem or use ptrace
- Read/modify the target process registers
- Write shellcode into the target process space
```

### /proc/self/mem self-modification

```text
Flow:
1. open("/proc/self/mem", O_RDWR)
2. lseek(fd, target_addr, SEEK_SET)
3. write(fd, new_code, size)

Purpose:
- Bypasses W^X protection (mmap pages cannot be W+X at the same time)
- Modifies its own code segment (.text is usually read-only)
- Patches instructions at runtime
```

---

## Strategy for analyzing large ELFs

For large binaries of 5MB+:

```text
1. Quick reconnaissance (5 minutes)
   - file / rabin2 -I → architecture, type, protections
   - strings | grep -i "error\|fail\|http\|/proc\|/dev" → key strings
   - rabin2 -i → imported functions (if any)
   - rabin2 -E → exported functions

2. Structure analysis (10 minutes)
   - readelf -l → program headers (LOAD segment layout)
   - Code near the entry point → any decompression/decryption
   - Find .init_array → constructors (may contain anti-debugging)

3. Locate the key logic
   - Start from string cross-references
   - Start from system calls (mmap/ptrace/open)
   - Start from network functions (connect/send/recv)

4. Divide and conquer
   - If it is self-extracting → decompress first, analyze the payload
   - If it has several modules → analyze by functional block
   - Compare different versions with binary-diff
```

---

## Tool command quick reference

```bash
# Basic information
file binary
readelf -h binary          # ELF header
readelf -l binary          # program headers
readelf -S binary          # section headers (if any)
rabin2 -I binary           # combined information

# Strings
strings -a binary | less
rabin2 -z binary           # data section strings
rabin2 -zz binary          # whole-file strings

# Disassembly
r2 -A binary               # radare2 analysis
objdump -d binary          # GNU disassembly
aarch64-linux-gnu-objdump -d binary  # ARM64 cross disassembly

# Dynamic analysis
strace -f ./binary         # system call tracing
ltrace -f ./binary         # library call tracing
qemu-aarch64 -strace ./binary  # ARM64 emulated execution

# Memory dump
gdb -p <pid> -ex "dump memory out.bin 0xADDR 0xADDR+SIZE" -ex quit

# Repair a corrupted ELF
# Manually change e_phnum or patch the corrupted PHDR
python -c "
import struct
with open('binary', 'r+b') as f:
    f.seek(0x38)  # e_phnum offset (64-bit)
    f.write(struct.pack('<H', 2))  # change to the correct PHDR count
"
```
