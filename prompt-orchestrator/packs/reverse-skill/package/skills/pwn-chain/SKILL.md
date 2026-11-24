---
name: pwn-chain
description: |
  Full-chain engineering method from reverse engineering to a working exploit.
  When to use: you have the binary + the vulnerability point + the target environment and need an exploit that works reliably (not a script that only reproduces locally and crashes as soon as it hits the remote).
  Covers three major directions: stack overflow / heap exploitation / kernel pwn. Emphasizes the engineering gap from "works locally in a CTF → works reliably against the real remote": libc version mismatch, heap spray timing, SMEP/SMAP/KASLR, stack alignment, remote buffering.
  Core toolchain: pwntools + GEF/pwndbg + ROPgadget/Ropper + one_gadget + libc-database + qemu-system kernel debugging.
  Trigger keywords: pwn, stack overflow, heap overflow, ROP, ret2libc, ret2csu, one_gadget, libc-database, heap exploitation, tcache, fastbin, unsorted bin, kernel pwn, kROP, SMEP, SMAP, KASLR, modprobe_path, pwntools, GEF, pwndbg.
---

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

# From Vulnerability Point to Working Exploit (Pwn Chain)

## Scope

Use this skill when the task falls into one of these scenarios:

1. **You have the binary + a known vulnerability point**: static analysis/audit/fuzzing already found an overflow/UAF/double free, and you need to go from trigger to shell
2. **The CTF challenge works locally but not remotely**: differences in the remote environment break the script, and it needs stabilizing
3. **Binary exploitation of a real target**: in an SRC / red team scenario a memory corruption vulnerability is identified, and an RCE must be built
4. **ioctl bug in a Linux kernel driver**: triggered from user mode, with the goal of escalating to root

**Precondition**: you already know "where it blows up". This skill does not find vulnerabilities (that is fuzzing / auditing); it only handles "writing the exploit from the vulnerability point".

### Division of work with other skills

| Scenario | What to use |
|------|--------|
| Identify custom VMs / anti-debugging / complex obfuscation | `reverse-engineering/` |
| Open a binary from scratch for static analysis | `ida-reverse/` or `radare2/` |
| **Vulnerability point known, write an exploit that works remotely** | **This skill** |
| Integrate the shell from pwn into a complete attack chain | `attack-chain/` (downstream) |

`reverse-engineering/` focuses on "understanding what the program does" (pattern recognition, protocol reconstruction, solving odd mechanisms in CTF challenges); this skill focuses on "turning an understood vulnerability into an executable attack". The two are often used together, with a clear division of work.

## Core workflow

```text
Step 1: Confirm the vulnerability type + protection mechanisms
   ├─ checksec ./vuln (NX / Canary / PIE / RELRO / Fortify)
   ├─ file ./vuln  + readelf -d ./vuln
   ├─ Vulnerability class: stack overflow / format string / heap (UAF/DF/OF) / integer / race / kernel
   └─ → decide which references/ to follow

Step 2: Choose the exploitation strategy
   ├─ NX off + no ASLR → shellcode directly
   ├─ NX on + libc given → ret2libc / one_gadget
   ├─ NX on + no libc given → leak, then look it up in libc-database
   ├─ Heap → technique matching the glibc version (tcache/fastbin/unsorted/large)
   └─ Kernel → commit_creds / modprobe_path / core_pattern

Step 3: Prepare libc + gadgets
   ├─ libc-database: ./find puts 0x6f0
   ├─ ROPgadget --binary ./libc.so.6 --only "pop|ret"
   ├─ one_gadget ./libc.so.6
   └─ Compute the base: leak_addr - libc.sym['puts']

Step 4: Write the pwntools template (local process)
   ├─ context.binary = ELF('./vuln')
   ├─ p = process('./vuln')  /  p = gdb.debug('./vuln','b *main+xx')
   ├─ payload = cyclic(N) + p64(ret) + ...
   └─ p.interactive()

Step 5: Make it work locally
   ├─ Attach repeatedly + check registers + tune the offset
   ├─ Use pwndbg/GEF vmmap / heap / bins / telescope
   └─ Once it works, switch to remote()

Step 6: Remote stabilization
   ├─ libc offsets: look them up in libc-database with the leak; do not guess
   ├─ Stack alignment: not 16-byte aligned → movaps crashes → add a ret gadget
   ├─ Remote network latency → recvuntil on exact anchor strings; no fuzzy sleeps
   ├─ Remote buffering: sendlineafter is more reliable than sendline
   ├─ Heap spray success rate: increase the spray count + leave padding chunks to prevent coalescing
   └─ Run it many times: write a while True loop to verify a success rate ≥ 95%
```

## Typical scenarios

### Scenario 1: remote 64-bit binary (NX+PIE+canary, libc given)

```text
Have: ./vuln (64-bit ELF, NX, PIE, canary) + ./libc.so.6 + nc host port
Vulnerability: read(buf, 0x200) but buf is only 0x40 bytes → stack overflow
Protections: canary blocks it, PIE randomizes .text

Strategy:
1. Leak the canary first (stack/format string/partial read)
2. Then leak a libc function address (puts@got)
3. Compute the libc base with libc.address = leaked - libc.sym['puts']
4. one_gadget ./libc.so.6 and choose a magic gadget whose constraints can be met
5. payload = padding + canary + saved_rbp + (pop_rdi + bin_sh + system) or one_gadget directly
6. Add a ret gadget to fix stack alignment (critical!)
```

See `references/stack-pwn.md` for the complete template.

### Scenario 2: Linux kernel driver ioctl out-of-bounds write → root

```text
Have: vmlinux + bzImage + initramfs.cpio.gz + custom vuln.ko
Vulnerability: the copy_from_user length in ioctl(0x1337, ptr) is controllable → kernel heap overflow (kmalloc-64 slab)
Protections: SMEP, SMAP, KASLR, KPTI

Strategy:
1. Modify the init script to get a root shell (CTF) or leak the KASLR base first and continue (real)
2. Leak the kernel base through /proc/kallsyms (may be restricted) or an uninitialized heap spray
3. Spray tty_struct / msg_msg / pipe_buffer in the kmalloc-64 slab
4. Overwrite the vtable pointer to point at user mode → fails (SMEP), so use a stack pivot + kernel ROP instead
5. ROP chain: prepare_kernel_cred(0) → commit_creds → swapgs+iretq → user-mode execve("/bin/sh")
6. Or simpler: overwrite modprobe_path with "/tmp/x", write a /tmp/x, then trigger modprobe
```

See `references/kernel-pwn.md` for the complete template.

## On-Demand Bootstrap

### Tool dependencies

| Tool | Purpose | Install method |
|------|------|---------|
| pwntools | Exploit writing framework | `pip install pwntools` |
| GEF | gdb enhancement (recommended for kernel + user mode) | `git clone https://github.com/bata24/gef` (actively maintained fork) |
| pwndbg | gdb enhancement (best heap debugging experience) | `git clone https://github.com/pwndbg/pwndbg && ./setup.sh` |
| ROPgadget | Gadget search | `pip install ropgadget` |
| Ropper | Gadget search (alternative, supports more architectures) | `pip install ropper` |
| one_gadget | libc magic gadget lookup | `gem install one_gadget` (needs ruby) |
| libc-database | libc fingerprint lookup | `git clone https://github.com/niklasb/libc-database && ./get` |
| qemu-system-x86_64 | Kernel challenge debugging | `apt install qemu-system-x86` |
| binwalk / cpio | Unpack initramfs | `apt install binwalk cpio` |
| patchelf | Switch the libc version | `apt install patchelf` |

### Bootstrap check script

```bash
# One-command check + install of the core tools
for t in pwntools ropgadget ropper; do
  pip show $t >/dev/null 2>&1 || pip install $t
done

command -v one_gadget >/dev/null || gem install one_gadget

[ -d ~/tools/libc-database ] || git clone https://github.com/niklasb/libc-database ~/tools/libc-database
[ -d ~/tools/libc-database/db ] || (cd ~/tools/libc-database && ./get ubuntu debian)

[ -d ~/tools/pwndbg ] || (git clone https://github.com/pwndbg/pwndbg ~/tools/pwndbg && cd ~/tools/pwndbg && ./setup.sh)
```

### After the same tool fails to install automatically twice

Stop retrying and print structured manual install steps (pip index / gem source / git mirror in China / apt source) for the user to confirm.

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Trigger condition**: binary + identified vulnerability point, an exploit must be written

**Upstream skills (use them first, then come back to this skill)**:
- You do not yet understand what the binary does → `reverse-engineering/`
- Detailed static analysis needed → `ida-reverse/`
- Quick reconnaissance to confirm architecture/protections → `radare2/`

**Downstream skills (after you have a shell)**:
- Integrate into a complete attack chain (lateral movement, privilege escalation, persistence) → `attack-chain/`

**Submodule navigation**:
- Stack exploitation (ret2libc / ret2csu / one_gadget / stack alignment) → `references/stack-pwn.md`
- Heap exploitation (tcache / fastbin / unsorted / large bin / FILE struct) → `references/heap-pwn.md`
- Kernel pwn (kROP / SMEP-SMAP bypass / KASLR leak / modprobe_path) → `references/kernel-pwn.md`

## Notes

- **Do not call it done when it works locally**: the local libc / ASLR / network environment all differ from the remote; verify stability with 20+ consecutive runs in remote mode
- **The libc version must be confirmed**: look it up with the leak + libc-database; do not assume the default Ubuntu 22.04 libc
- **Stack alignment is a common 64-bit pitfall**: `movaps xmm0, [rsp]` segfaults when rsp is not 16-byte aligned; add an empty `ret` gadget to fix it
- **Heap exploitation is extremely sensitive to the glibc version**: tcache arrived in 2.27, safe-linking in 2.32, hooks were removed in 2.34, and each version has a different exploitation path
- **Kernel pwn must confirm the CPU flags first**: whether the qemu boot arguments include +smep +smap +pku decides how the ROP chain is written
- **One KASLR leak is enough**: once you have one kernel address, every other address is an offset; do not leak repeatedly

## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
