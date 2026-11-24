# EDR Hook Survey Quick Reference

> Only for authorized red team / adversary exercises / testing your own products; use against unauthorized targets is forbidden.

This document summarizes the user-mode and kernel-mode monitoring points of mainstream EDRs / AVs, so the red team can quickly locate "what to deal with" during reconnaissance.

## 1. Mainstream EDR fingerprints and hook patterns

| Vendor / product | User-mode components | Kernel drivers | Main monitoring surfaces |
|------------|-----------|---------|-----------|
| CrowdStrike Falcon | `CSFalconService.exe`, `CSAgent.sys` injected into target processes | `CSAgent.sys`, `CSBoot.sys` | Heavy kernel callbacks + ETW-TI; fewer user-mode hooks (cloud checks) |
| Microsoft Defender for Endpoint (MDE) | `MsMpEng.exe`, `MpClient.dll` | `WdFilter.sys`, `WdBoot.sys`, `WdNisDrv.sys` | AMSI + ETW-TI + ntdll inline hooks + kernel callbacks, comprehensive |
| SentinelOne | `SentinelAgent.exe`, `SentinelHelperService.exe` | `SentinelMonitor.sys`, `SentinelDeviceControl.sys` | Heavy ntdll user-mode hooks + kernel callbacks + its own ETW provider |
| Elastic Defend (formerly Endpoint Security) | `elastic-endpoint.exe` | `elastic-endpoint-driver.sys` | Mainly ETW + a few ntdll hooks, uploaded through the Elastic Agent |
| ESET | `ekrn.exe`, `eamsi.dll` | `eamonm.sys`, `epfwwfp.sys` | Very many user-mode hooks (NtCreateFile / NtOpenProcess and others) |
| Sophos Intercept X | `SophosFileScanner.exe`, `SophosNtpService.exe` | `SophosED.sys`, `hmpalert.sys` | ntdll hooks + HMPA memory protection + kernel callbacks |
| Kaspersky | `avp.exe`, `klif.sys` | `klif.sys`, `klhk.sys` | Heavy user-mode hooks + its own KLIF minifilter + network filter driver |
| Trend Micro Apex One | `TmListen.exe`, `TmCCSF.dll` | `tmcomm.sys`, `tmactmon.sys` | User-mode hooks + behavior monitoring driver |
| Carbon Black | `RepMgr.exe`, `RepWAV.exe` | `ParityDriver.sys` | Leans on kernel callbacks + ETW |

### Quick fingerprint script

```powershell
$edrSigs = @{
    'CSAgent'           = 'CrowdStrike Falcon'
    'SentinelAgent'     = 'SentinelOne'
    'elastic-endpoint'  = 'Elastic Defend'
    'ekrn'              = 'ESET'
    'MsMpEng'           = 'Microsoft Defender'
    'SophosFileScanner' = 'Sophos Intercept X'
    'avp'               = 'Kaspersky'
    'TmListen'          = 'Trend Micro Apex One'
    'cb'                = 'Carbon Black'
}

Get-Process | ForEach-Object {
    foreach ($k in $edrSigs.Keys) {
        if ($_.ProcessName -match $k) {
            "[+] $($edrSigs[$k]) detected: $($_.ProcessName) (PID $($_.Id))"
        }
    }
}

Get-ChildItem 'C:\Windows\System32\drivers\*.sys' |
    Where-Object { $_.Name -match 'CSAgent|Sentinel|elastic|eam|WdFilter|Sophos|klif|tmcomm|Parity' } |
    Select-Object Name, VersionInfo
```

## 2. Key user-mode ntdll hook functions

`ntdll.dll` exports that EDRs almost always hook (grouped by ATT&CK behavior):

| Function | Monitored behavior | ATT&CK |
|------|-----------|--------|
| `NtCreateThreadEx` | Remote thread injection, QueueUserAPC injection | T1055.002 / T1055.004 |
| `NtAllocateVirtualMemory` | Shellcode allocates RWX memory | T1055 |
| `NtAllocateVirtualMemoryEx` | Cross-process memory allocation (new API in Win10+) | T1055 |
| `NtProtectVirtualMemory` | Change page protection RW→RX | T1055 |
| `NtWriteVirtualMemory` | Cross-process shellcode writes | T1055.012 |
| `NtMapViewOfSection` | Section-based injection (Process Doppelganging / Ghosting) | T1055.013 |
| `NtCreateSection` | Paired with MapViewOfSection | T1055.013 |
| `NtOpenProcess` | Open the target process for a handle | T1057 |
| `NtQueueApcThread` / `NtQueueApcThreadEx` | APC injection | T1055.004 |
| `NtCreateProcess` / `NtCreateProcessEx` / `NtCreateUserProcess` | Create child processes (including PPID spoof) | T1106 |
| `NtSetContextThread` | Change thread context (thread hijacking injection) | T1055.003 |
| `NtResumeThread` | Resume the thread after injection | T1055 |
| `NtQuerySystemInformation` | Enumerate processes / drivers / handles | T1057 / T1082 |
| `NtAdjustPrivilegesToken` | Privilege escalation to obtain SeDebugPrivilege and others | T1134 |
| `NtLoadDriver` | Load a kernel driver (BYOVD) | T1543.003 |

### Verify whether a hook exists

```powershell
# Simple: diff the disassembly of the on-disk ntdll and the current process's ntdll
# 1. Get the on-disk ntdll
copy C:\Windows\System32\ntdll.dll C:\temp\ntdll_clean.dll

# 2. Attach to any process in windbg and export the .text section of the current ntdll
# .writemem c:\temp\ntdll_live.bin ntdll!.text L?<size>

# 3. Disassemble NtAllocateVirtualMemory with IDA / radare2; normally it should be:
#    mov r10, rcx
#    mov eax, <SSN>
#    test byte ptr [...]
#    jne ...
#    syscall
#    ret
# If the first instruction became jmp <some address>, it is a hook
```

## 3. Kernel callback monitoring points

Common kernel callbacks registered by EDRs (all can be unregistered through the BYOVD route in `attack-chain`, at a high cost):

| API | When the registered callback fires | Defender use |
|-----|--------------|-----------|
| `PsSetCreateProcessNotifyRoutineEx` | Process creation / exit | Block suspicious child processes |
| `PsSetCreateThreadNotifyRoutine` | Thread creation / exit | Detect remote thread injection |
| `PsSetLoadImageNotifyRoutine` | DLL / EXE loaded into any process | Module integrity / block unsigned |
| `CmRegisterCallback` / `CmRegisterCallbackEx` | Registry operations | Persistence detection |
| `ObRegisterCallbacks` | `OpenProcess` / `OpenThread` handle requests | Prevent LSASS handle acquisition (T1003.001) |
| `MmRegisterPhysicalMemoryCallback` | Physical memory mapping | Prevent DMA / memory forensics |
| `IoRegisterFsRegistrationChange` | Filesystem registration | Minifilter coordination |
| `KeRegisterNmiCallback` | NMI (very few EDRs use it) | Anomaly monitoring |
| `EtwRegister` (kernel side) | Kernel ETW reporting | Coexists with ETW-TI |

### Enumerate registered callbacks with windbg

```text
0: kd> dx -r1 nt!PspCreateProcessNotifyRoutine
0: kd> dx -r1 nt!PspCreateThreadNotifyRoutine
0: kd> dx -r1 nt!PspLoadImageNotifyRoutine

0: kd> !object \Callback
0: kd> !object \Callback\ProcessObject
```

Or use tools such as PChunter / DRVHV to view the callback list visually as a regular user.

## 4. Static hook table dump (IDA + windbg flow)

### Flow A: single-process comparison

```text
1. Find a process that the EDR user-mode component has been injected into (any live process)
2. windbg attach (-pn target.exe)
3. lm m ntdll  → get the module base address
4. .writemem c:\temp\ntdll_live.bin ntdll+0x0 L?<image size>
5. Copy C:\Windows\System32\ntdll.dll to c:\temp\ntdll_disk.dll
6. Load both files in IDA and jump to NtAllocateVirtualMemory:
     - disk: standard prologue
     - live: first instruction jmp <0x7FFE000000xx>
7. Follow the jmp target address → that is the EDR trampoline; dump it
8. Step into the trampoline to see which DLL it finally lands in and confirm the EDR module name
```

### Flow B: batch hook table generation

Use `HookHunter` or your own script:

```powershell
# pseudo workflow; see the scripts mentioned in references
$disk = Get-Content C:\Windows\System32\ntdll.dll -Encoding Byte
$live = # obtained through OpenProcess + ReadProcessMemory
# Compare the first 16 bytes of each export in the .text section
```

## 5. Automatic detection with pe-sieve

`pe-sieve` is the first choice for surveying EDR hooks and for implant self-checks:

```powershell
# Basic scan
pe-sieve64.exe /pid 1234

# Recommended combination (with shellcode and hook detection)
pe-sieve64.exe /pid 1234 /shellc 3 /modules 3 /imp 3 /data 3 /dir hooks_dump

# Key parameters:
#   /shellc N    shellcode scan level (0-3)
#   /modules N   module integrity check (0-3)
#   /imp N       IAT hook check
#   /data N      data section scan
#   /dir <path>  dump output directory
```

The output produces `*.tag` files under `hooks_dump/<pid>.<name>/` that list hook addresses:

```text
modified_modules.tag example:
71f10000;ntdll.dll
71f1a3b0;hook;jmp_far
71f1c020;hook;jmp_near
```

Feed it directly to IDA and jump to the matching RVA for further analysis.

### Embedding pe-sieve in the implant (self-check)

In practice `pe-sieve` is often compiled as a library (`libpe-sieve`) so the implant checks itself at startup: if ntdll is hooked, trigger the unhook flow; if it finds itself hooked, be careful, as it may be in a sandbox.

## 6. Dynamic observation with API Monitor v2

API Monitor v2 (Rohitab) is suited to seeing in the lab when and where the EDR inserts hooks:

```text
1. Start API Monitor v2 (administrator)
2. Tick in the API Filter:
     - NT Native API → Memory Management
     - NT Native API → Process and Thread
     - Windows Defender / AMSI (if visible)
3. Monitor New Process → choose the implant test sample
4. Observe:
     - The NtAllocateVirtualMemory call order
     - Whether calls are relayed through an EDR DLL
5. In the Modules tab, see which EDR DLLs are injected through LoadLibrary
```

## 7. Common EDR DLLs (user mode) quick reference

| DLL | Vendor | Notes |
|-----|------|------|
| `umppc*.dll` | Microsoft Defender | MpClient userland |
| `mpoav.dll` | Microsoft Defender | AMSI provider |
| `aswAMSI.dll` | Avast | AMSI provider |
| `eamsi.dll` | ESET | AMSI provider |
| `IDPMServiceClient.dll` | Sophos | HMPA injection |
| `klsihk64.dll` | Kaspersky | Injected into target processes |
| `CrowdStrike.Sensor.dll` | CrowdStrike | Old versions; new versions rely mainly on the kernel |
| `SentinelInjection64.dll` | SentinelOne | User-mode injection |
| `TmUmEvt64.dll` | Trend Micro | Behavior monitoring |

Once the target EDR is confirmed, decide which DLL to reverse for the hook table.

## Reference links

- pe-sieve: <https://github.com/hasherezade/pe-sieve>
- HollowsHunter: <https://github.com/hasherezade/hollows_hunter>
- API Monitor v2: <http://www.rohitab.com/apimonitor>
- MITRE ATT&CK T1562: <https://attack.mitre.org/techniques/T1562/>
- MITRE ATT&CK T1055: <https://attack.mitre.org/techniques/T1055/>
- ired.team EDR notes: <https://www.ired.team/offensive-security/defense-evasion>

## Routing callback

After the hook survey, return to Step 3 of `SKILL.md` to choose the bypass technique combination, then execute per `references/unhook-techniques.md` and `references/telemetry-blinding.md`.
