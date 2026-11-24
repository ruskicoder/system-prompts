# 2026-07-20 Complete Bootstrap of a Windows Reverse Engineering Toolchain

## Scenario classification

Other / toolchain and environment

## Target overview

Installed and verified a reverse engineering toolchain covering native, managed, Android, firmware, protocol, forensics, browser and MCP on a Windows 24H2 host.

## Complete execution chain

1. Read the shared tool-index and reused installed tools first.
2. Ran the general PATH probe and filled gaps in static, dynamic, firmware and protocol tools.
3. For large files, extracted URLs and SHA-256 from trusted manifests and downloaded directly with aria2 with IPv6 disabled.
4. Created a unified entry `{user_profile}\Tools\reverse-bin` for portable tools.
5. Built and registered the Ghidra, IDA, JS, browser traffic and Burp MCPs.
6. Verified the tools with real PE/APK/.NET/PYC/WASM/firmware fixtures, not just version commands.
7. Refreshed the shared tool-index and produced the formal install report and flowchart.

## Pitfall record

| Problem | Cause | Solution | Time |
|---|---|---|---|
| winget large file downloads made no progress for a long time | Delivery Optimization and the default IPv6 path were unstable | Took the official URL/hash from the winget metadata and used `aria2c --disable-ipv6=true` | High |
| anything-analyzer SQLite ABI mismatch | A plain `pnpm rebuild better-sqlite3` builds for the Node ABI, while Electron needs the Electron ABI | Use the project's `pnpm run postinstall` | Medium |
| WSL service 1053, system feature missing | The Windows image stripped the WSL, VirtualMachinePlatform and Hyper-V feature packages | Kept the real Linux command gap and switched to native Windows tools and QEMU full-system | Medium |
| Dr. Memory version normal but injection crashes | Compatibility problem with Windows 11 24H2 build 26100 | Recorded the upstream issue, used AppVerifier/PageHeap/UMDH/CDB/Frida | Medium |
| Codex TOML failed to load | Garbled historical project paths caused missing quotes, invalid escapes and duplicate keys | Fixed only the table header syntax and verified with `codex mcp list` | Low |
| Burp MCP registered but no tools | The Burp GUI had not loaded the extension yet, 9876 not listening | Built a fixed JAR and recorded the GUI load condition | Low |

## Toolchain findings

- The general probe finally reached 57/64; all 7 gaps are Linux user-mode or kernel capabilities.
- The Windows SDK Debugging Tools are an important supplement when Dr. Memory is incompatible: CDB, GFlags, UMDH, NTSD, KD.
- MCPs should be verified separately for "stdio/HTTP initialization" and "GUI back end online"; a successful registration does not mean the tools are callable.
- IDA Free works for local interactive analysis but cannot replace the idalib/Hex-Rays MCP back end of a legitimate IDA Pro.

## Key code/commands

```powershell
python "{skill_root}\scripts\toolchain_probe.py" --format markdown
aria2c --disable-ipv6=true --max-connection-per-server=16 --split=16 "{official_url}"
powershell -NoProfile -ExecutionPolicy Bypass -File "{package_root}\skills\scripts\refresh-tool-index.ps1"
codex mcp list
cdb -g -G C:\Windows\System32\where.exe cmd
```

## Improvement suggestions for this package

- Add Dr. Memory, CDB, GFlags, UMDH, DTC, SquashFS, flashrom and Frida Trace to the Windows tool-index catalog.
- Capability states should distinguish `installed`, `bridge-ready`, `backend-online`, `runtime-verified`.
- Add an explicit Linux-only gap note for stripped Windows editions instead of generating fake same-named wrappers.

## Reusable patterns/script snippets

Fixed pattern for large file downloads: first check the version, URL and SHA-256 against the official package metadata, then download with aria2 with IPv6 disabled; after downloading, verify both the hash and Authenticode (where applicable).

## Evolution actions

- [ ] Updated the routing matrix
- [x] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added pitfall records
- [ ] No update needed

## Environment information

- OS: Windows NT build 26100.4946, 24H2, x64
- Tool versions: see the local formal install report and tool-index
- Target platform/version: native Windows toolchain, also covering Android, Linux/ELF static analysis and full-system emulation

## Redaction requirements

This record contains no real targets, credentials, tokens, internal URLs or usernames; every path uses placeholders.

## Index sync

Updated the statistics and the "Toolchain and environment" category of `_index.md`.

---
<!-- [Community contribution] Local record completed. -->
