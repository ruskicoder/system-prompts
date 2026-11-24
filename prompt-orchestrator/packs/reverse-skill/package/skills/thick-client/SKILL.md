---
name: thick-client
description: Use for authorized security testing of desktop thick clients including local storage, update channels, IPC, traffic, and client-side trust boundaries.
---

# Thick Client Security Testing

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-pentest.md`
2. `NOW`: confirm that the target is a **desktop thick client** (Win/macOS/Linux GUI or a companion service), not pure web
3. `NOW`: case-init; write the installer source and test accounts into scope
4. `NEXT`: tools (Burp upstream proxy, process monitoring, reverse engineering tools)
5. `ACT`: trust boundary diagram → local surface → network surface → update/supply chain

## When to use

- C/S architecture clients, Electron/Qt/.NET WinForms/WPF
- Local configuration/credential storage, IPC, named pipes
- Research on bypassing client-enforced checks (authorized)
- Automatic update channel and code signing verification

## Workflow

### 1. Build the boundary

```text
□ Process tree, child processes, drivers/services
□ Listening ports and outbound domains
□ Local sensitive paths: %APPDATA%, Keychain, registry
```

### 2. Local attack surface

```text
□ Plaintext configuration, hard-coded keys, debug switches
□ DLL hijacking/search order (Windows)
□ Database file (SQLite) permissions and encryption
□ IPC: who can connect? Is it authenticated?
```

### 3. Network surface

```text
□ System proxy / application custom TLS
□ Certificate pinning → combine with mobile/js methodology or Frida
□ API privilege bypass: admin interfaces hidden by the client
```

### 4. Reverse engineering verification

```text
□ .NET → dotnet-reverse; native → ida/ghidra; Electron → asar + js-reverse
```

## Toolchain

| Tool | Purpose |
|------|------|
| Process Monitor / API Monitor | Behavior |
| Burp / mitmproxy | Traffic |
| dnSpy / IDA / Ghidra | Reverse engineering |
| Sysinternals | Windows surface |
| asar / nexe detection | Electron |

## References

- `references/thick-client-checklist.md`
- `../dotnet-reverse/` `../ida-reverse/` `../js-reverse/` `../api-security/`

## Routing context

**Upstream**: MASTER R32  
**Downstream**: pure protocol `protocol-reverse`; supply chain updates `supply-chain-security`

## Task completion self-check

- [ ] Did I draw the trust boundary?
- [ ] Are both the local and network surfaces covered?
- [ ] Checklist?