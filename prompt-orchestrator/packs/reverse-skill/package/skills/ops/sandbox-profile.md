# Optional Sandbox Tool Profile (compared with bootstrap-manifest)

> Z3r0's default image is fully tooled; reverse-skill **bundles no image** and uses this table for a "coverage comparison" and optional Docker suggestions.

## Capabilities reverse-skill can bootstrap automatically

Source: `skills/scripts/bootstrap-manifest.json` (the file is authoritative):

| Capability | Typical scenario |
|------|----------|
| jadx / apktool / adb / frida / frida-ps | Android |
| r2 / rabin2 | Binary CLI |
| idalib-mcp / idapro | IDA MCP |
| jeb-pro | Commercial Android / ARM decompiler (manual licensed install) |
| jshookmcp / reqable-mcp / anything-analyzer / agent-browser | Web/JS/capture/browser |
| ghidra-mcp | Ghidra |
| nmap / seclists / proxycat / burpsuite-mcp / pentestswarm | Pentest |
| binwalk / pwntools / yara | Firmware/pwn/malware |

```powershell
powershell -File skills\scripts\bootstrap-reverse.ps1 -Capability @('jadx','nmap','yara') -StartServices
powershell -File skills\scripts\refresh-tool-index.ps1
```

## Common in the Z3r0 sandbox but not installed automatically by this package's manifest

| Tool | reverse-skill strategy |
|------|-------------------|
| subfinder / amass / httpx / ffuf / nuclei / sqlmap | Documented install / Kali script / external MCP; **do not pretend bootstrap has them** |
| Full Ghidra GUI | ghidra-mcp capability + manual plugin steps |
| gdb / pwndbg | Manual per platform documentation; pwntools can be bootstrapped |
| hydra / hashcat | Manual or Kali |
| JEB Pro | Manual install after the user holds a license; third-party MCP bridges must pass a supply chain review first |
| Reqable desktop client | User installs manually; `reqable-mcp` only registers the MCP runtime pinned to the official version |
| SecLists | seclists capability |

## Recommended "lightweight Docker operations" profile (optional, not a dependency)

Only when the user **themselves** has Docker and an authorized lab:

```text
Minimal: nmap + nuclei + sqlmap containers or a pentestMCP-type image
Mobile: jadx + apktool + frida on the host
Reverse engineering: IDA/r2 on the host + tool-index
```

**MUST NOT** require the user to install Z3r0 to use reverse-skill.

## network_profile link

Scans inside the sandbox are still constrained by the `network_profile` in the case `scope.md`:

- `offline` → starting outbound scan containers is not recommended  
- `authorized_target_only` → containers may also only hit in_scope  
