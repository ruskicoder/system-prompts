# Kernel Driver Reverse Engineering Reference

> Covers Windows/Linux kernel driver reverse engineering, rootkit analysis, C/C++ binary pattern recognition.

---

## Windows driver reverse engineering

### Driver types

| Type | Traits | Analysis focus |
|------|------|---------|
| WDM (Windows Driver Model) | Old-style driver, manual IRP management | DriverEntry → device creation → Dispatch routines |
| KMDF (Kernel Mode Driver Framework) | Modern framework, event driven | EvtDriverDeviceAdd → Queue → I/O callbacks |
| WDF (Windows Driver Foundation) | Umbrella name for KMDF + UMDF | Look at the WdfDriverCreate call |
| Minifilter | Filesystem filter driver | FltRegisterFilter → Pre/Post callbacks |

### WDM driver analysis flow

```text
1. Find DriverEntry (the entry point)
   - IDA identifies it automatically, or search for IoCreateDevice / IoCreateSymbolicLink

2. Find the device name and symbolic link
   - IoCreateDevice → DeviceName (such as \Device\MyDriver)
   - IoCreateSymbolicLink → SymLink (such as \DosDevices\MyDriver)

3. Find the Dispatch routines
   - DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DispatchIoctl
   - This is the entry user mode calls through DeviceIoControl

4. Analyze IOCTL handling
   - switch(IoControlCode) dispatches the different functions
   - IOCTL encoding: CTL_CODE(DeviceType, Function, Method, Access)
   - Method: METHOD_BUFFERED / METHOD_IN_DIRECT / METHOD_OUT_DIRECT / METHOD_NEITHER

5. Find vulnerabilities
   - User-controlled buffer without length validation → overflow
   - METHOD_NEITHER uses user pointers directly → arbitrary read/write
   - IOCTL permissions not checked → callable by unprivileged users
```

### IOCTL code parsing

```python
# Parse the IOCTL code
def decode_ioctl(code):
    device_type = (code >> 16) & 0xFFFF
    access = (code >> 14) & 0x3
    function = (code >> 2) & 0xFFF
    method = code & 0x3
    
    methods = {0: "BUFFERED", 1: "IN_DIRECT", 2: "OUT_DIRECT", 3: "NEITHER"}
    access_types = {0: "ANY", 1: "READ", 2: "WRITE", 3: "READ|WRITE"}
    
    return f"DevType=0x{device_type:X} Func=0x{function:X} Method={methods[method]} Access={access_types[access]}"

# Example
decode_ioctl(0x80002034)
# DevType=0x8000 Func=0x80D Method=BUFFERED Access=ANY
```

### IDA plugins

| Plugin | Purpose | Link |
|------|------|------|
| **Driver Buddy Reloaded** | Identifies IOCTLs, Dispatch routines and device names automatically | https://github.com/VoidSec/DriverBuddyReloaded |
| **WinDbg + IDA** | Kernel debugging + static analysis together | Built in |
| **FLIRT/Lumina** | Identify WDK library functions | Built into IDA |

### Reference articles

- [Windows Drivers RE Methodology (VoidSec)](https://voidsec.com/windows-drivers-reverse-engineering-methodology/): the most complete WDM driver reverse engineering methodology
- [Driver Reversing 101](https://eversinc33.com/posts/driver-reversing.html): WDM vs KMDF comparison
- [Methodology of Reversing Vulnerable Killer Drivers](https://whiteknightlabs.com/2025/10/28/methodology-of-reversing-vulnerable-killer-drivers/): vulnerable driver analysis

---

## Linux kernel module reverse engineering

### LKM (Loadable Kernel Module) structure

```text
Key functions:
- init_module / module_init → runs when the module loads
- cleanup_module / module_exit → runs when the module unloads

Key structures:
- struct file_operations → open/read/write/ioctl of a character device
- struct net_device_ops → network device operations
- struct block_device_operations → block device operations
```

### Analysis flow

```text
1. Confirm it is a kernel module
   file module.ko → "ELF 64-bit ... relocatable" (note: relocatable, not executable)

2. Find the init/exit functions
   readelf -s module.ko | grep -E "init_module|cleanup_module"
   Or find the module information in the .modinfo section

3. Find the file_operations structure
   Search for register_chrdev / cdev_add / misc_register
   → find the fops struct → locate the ioctl/read/write handlers

4. Analyze the ioctl handling
   unlocked_ioctl / compat_ioctl functions
   → switch(cmd) dispatch

5. Find rootkit behavior
   - Modifying sys_call_table → syscall hook
   - Modifying the /proc filesystem → hide processes/files
   - Registering netfilter hooks → hide network connections
   - Modifying the VFS layer → hide files
```

### Common rootkit techniques

| Technique | Trait | Detection method |
|------|------|---------|
| syscall table hook | Modifies `sys_call_table` entries | Compare the in-memory table with the vmlinux on disk |
| VFS hook | Modifies `file_operations` function pointers | Check whether fops pointers point outside the kernel code segment |
| Netfilter hook | `nf_register_net_hook` | Walk the netfilter hook list |
| kprobe/ftrace hook | Registers kprobe or ftrace callbacks | Check the ftrace registration list |
| eBPF rootkit | Loads malicious BPF programs | `bpftool prog list` |
| DKOM | Directly modifies kernel objects (the process list) | Walk the task_struct list and compare with /proc |

### Tools

| Tool | Purpose |
|------|------|
| `crash` | Kernel dump analysis |
| `volatility3` | Memory forensics (Linux profile) |
| `dmesg` / `journalctl` | Kernel logs |
| `lsmod` / `/proc/modules` | Loaded module list |
| `modinfo` | Module metadata |
| `strace` | System call tracing (user-mode view) |

---

## C/C++ reverse engineering pattern recognition

### Common C patterns

| Source pattern | Disassembly trait |
|---------|-----------|
| `if-else` | `cmp` + `jcc` (conditional jump) |
| `switch-case` | Jump table (`jmp [rax*8 + table]`) or consecutive `cmp` |
| `for` loop | `cmp` + `jl/jle` + loop body + `inc/add` + `jmp` back |
| `while` loop | Condition check at the top of the loop |
| `do-while` | Condition check at the bottom of the loop |
| Function pointer call | `call rax` or `call [reg+offset]` |
| `struct` access | `[reg+fixed offset]` (such as `[rdi+0x10]`) |
| `malloc` + use | `call malloc` → return value stored in a register → later accesses through that register + offset |
| String comparison | `call strcmp` or `repe cmpsb` |

### C++-specific patterns

| Source pattern | Disassembly trait |
|---------|-----------|
| **Virtual function call** | `mov rax, [rcx]` (fetch the vtable) → `call [rax+offset]` (call the virtual function) |
| **Constructor** | Allocate memory → write the vtable pointer → initialize members |
| **Destructor** | Clean up members → may call `operator delete` |
| **this pointer** | The first argument (rcx/rdi) is the object pointer |
| **Inheritance** | The vtable contains parent virtual functions + child overrides |
| **Multiple inheritance** | Several vtable pointers inside the object (at different offsets) |
| **RTTI** | A `type_info` pointer before the vtable |
| **Exception handling** | `__cxa_throw` / `_CxxThrowException` |
| **STL containers** | `std::vector`: a three-pointer `{begin, end, capacity}` structure |
| **std::string** | Small string optimization (SSO): short strings inline, long strings heap allocated |

### vtable reverse engineering method

```text
1. Find the vtable
   - Search for contiguous function pointer arrays (in the .rodata or .rdata segment)
   - The constructor writes the vtable pointer with `mov [rcx], offset vtable`

2. Determine the class hierarchy
   - At offset -8 before the vtable there is usually the RTTI pointer (if not stripped)
   - Several vtables sharing the first entries → inheritance

3. Annotate the virtual functions
   - vtable[0] is usually the destructor (or deleting destructor)
   - Annotate the rest by offset: vtable[1] = func1, vtable[2] = func2...

4. In IDA
   - Create a struct at the vtable address (each field a function pointer)
   - Comment `call [rax+offset]` with the virtual function it calls
```

### Struct recovery

```text
Method 1: infer from access patterns
  mov eax, [rdi+0x00]  → field_0: int/ptr (4/8 bytes)
  mov ecx, [rdi+0x08]  → field_8: int/ptr
  movss xmm0, [rdi+0x10] → field_10: float

Method 2: infer from sizeof
  call malloc(0x30) → struct size 0x30 (48 bytes)
  
Method 3: infer from the constructor
  The constructor initializes every field → field types and offsets are clear at a glance

Method 4: use IDA's "Create struct" feature
  Select the access pattern → Edit → Struct → Create struct from selection
```

---

## Common compiler traits

| Compiler | Identification traits |
|--------|---------|
| MSVC | `_security_cookie` checks, `__fastcall` calling convention, Rich Header |
| GCC | `__stack_chk_fail`, `-fstack-protector`, `.note.GNU-stack` |
| Clang/LLVM | Similar to GCC but with different optimization patterns, `__asan_*` (if a sanitizer is on) |
| MinGW | GCC traits + Windows API calls |
| AOSP Clang | Android-specific `__android_log_print`, PGO markers |

### Optimization level identification

| Optimization level | Traits |
|---------|------|
| -O0 | Many redundant movs, every variable on the stack, no inlining |
| -O1 | Basic optimization, some variables in registers |
| -O2 | Loop unrolling, function inlining, tail call optimization |
| -O3 / -Os | Aggressive inlining, vectorization (SIMD), hard-to-read code |
| PGO | Hot path optimization, cold code split into `.text.cold` |
| LTO | Cross-module inlining, global dead code elimination |

---

## Kernel debugging environment

### Windows

```text
Debugger: WinDbg Preview
Connection: network debugging (recommended) or serial

Debuggee setup:
bcdedit /debug on
bcdedit /dbgsettings net hostip:192.168.x.x port:50000

Debugger connection:
WinDbg → File → Attach to Kernel → Net → Port:50000 Key:xxx

Common commands:
!analyze -v          # analyze the crash automatically
lm                   # list loaded modules
!drvobj \Driver\xxx  # view the driver object
dt nt!_DRIVER_OBJECT # display the struct
bp module!function   # set a breakpoint
```

### Linux

```text
Debugger: GDB + QEMU or kgdb

QEMU kernel debugging:
qemu-system-x86_64 -kernel bzImage -s -S ...
gdb vmlinux -ex "target remote :1234"

Common commands:
info threads         # kernel threads
lx-symbols           # load kernel symbols (needs scripts/gdb/)
p init_task          # view the init process
lx-dmesg             # kernel log
```

---

## Agent action anchors (Issue #65 U–AV)

Aligned with §5 of `references/nonpe-format-cookbook.md` (short table, does not replace the flow above):

| ID | Action | Evidence |
|----|------|----------|
| AG | Short `DriverEntry` → scan the non-empty `MajorFunction` slots, prioritize DEVICE_CONTROL/CREATE | `E-driver-irp-handlers` |
| AH | Build the IOCTL control code → handler table with METHOD_* | `E-driver-ioctl` |
| AI | Suspected BYOVD: compare against public vulnerable driver lists; record name/hash/signature and call intent; **write no exploit steps** | `E-driver-byovd` |

## Reference resources

| Resource | Description | Link |
|------|------|------|
| VoidSec driver reverse engineering methodology | Complete Windows WDM driver analysis flow | https://voidsec.com/windows-drivers-reverse-engineering-methodology/ |
| Elastic Rootkit series | Linux rootkit classification + detection | https://security-labs.elastic.co/security-labs/linux-rootkits-1-hooked-on-linux |
| Driver Buddy Reloaded | IDA driver analysis plugin | https://github.com/VoidSec/DriverBuddyReloaded |
| LOLDrivers | List of known vulnerable drivers | https://www.loldrivers.io/ |
| Windows Driver Samples | Official Microsoft driver samples | https://github.com/microsoft/Windows-driver-samples |
| Linux Kernel Module Programming | Kernel module development tutorial | https://sysprog21.github.io/lkmpg/ |
| Trail of Bits - Devirtualizing C++ | vtable reverse engineering method | https://blog.trailofbits.com/2017/02/13/devirtualizing-c-with-binary-ninja/ |
