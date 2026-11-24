# Cybersecurity Skills Router: Kali Linux Edition

> This directory is the optimized adaptation layer for Kali Linux 2026.1. It is tuned for Kali 2026.1 (kernel 6.18), released in March 2026.
> The core knowledge base (skills/, CTF-Sandbox-Orchestrator/) is shared with the Windows edition; the Kali-specific README and Bash entry points must cover the Windows core capability names and also provide native Kali tool and MCP capabilities.  
> The root [README-kali.md](../README-kali.md) is only a short redirect; **this file is authoritative**.

---

## AI: after reading

```text
1. Detect the package root (the repository root that contains skills/ and kali/)
2. Read kali/RULES-kali.md → global injection and tool scan
3. bash kali/scripts/refresh-tool-index.sh
4. Share the operations chain with the main package:
   - skills/MASTER-ROUTING.md (or pwsh skills/scripts/master-route.ps1)
   - skills/scripts/case-init.ps1 → work/<case>/scope.md
   - ACT against targets only after auth.status=granted + network_profile
   - skills/ops/ (evidence chain / roles / timeline / IDENTITY)
5. Report the configuration result to the user
```

General agent guidance is in the repository root [README_AI.md](../README_AI.md) (read this file when Kali is detected).

---

## 0. Relationship with the Windows edition (capability name alignment)

```text
project root/
├── skills/                    # shared: SKILL, routing, MASTER-ROUTING, ops, scripts, field-journal
├── CTF-Sandbox-Orchestrator/  # shared: 40+ CTF sub-skills
├── kali/                      # ← you are here
│   ├── scripts/
│   │   ├── bootstrap-reverse.sh
│   │   ├── refresh-tool-index.sh
│   │   ├── bootstrap-manifest.json
│   │   └── lib/
│   │       └── tool-discovery.sh
│   ├── RULES-kali.md
│   └── README-kali.md
├── RULES.md                   # Windows edition rules
└── Readme.md                  # Windows edition description
```


### 0.1 Alignment principle

The Kali entry is not a plain copy of the Windows README; it is **the same core capability names + extra Kali capabilities**:

- Windows: `skills/scripts/bootstrap-reverse.ps1`
- Kali: `kali/scripts/bootstrap-reverse.sh`
- Plain Linux/macOS: `skills/scripts/bootstrap-reverse.sh`

JEB Pro is a commercial tool that the user licenses and installs; Reqable MCP uses the officially pinned `reqable-mcp-server`, but still requires the Reqable desktop client to be installed separately.

Kali scripts should cover the core capability names of the Windows manifest, such as `jadx`, `apktool`, `frida`, `jshookmcp`, `xquik-mcp`, `anything-analyzer`, `idapro`, `r2`, `adb`, `ghidra-mcp`, `seclists`, `burpsuite-mcp`, `nmap`, `pentestswarm`; they may also support native Kali tools such as `mcp-kali-server`, `metasploitmcp`, `hexstrike-ai`, `sstimap`, `xsstrike` and `netexec`.

**Shared parts** (no changes needed):
- Every `SKILL.md`, `routing.md`, `MASTER-ROUTING.md`
- The `skills/ops/` operations contract (scope / evidence chain / roles / timeline)
- Every `references/` knowledge base
- The `field-journal/` self-evolution mechanism
- All of `CTF-Sandbox-Orchestrator/`
- `docs-generator/`, `diagram-generator/`
- `skills/scripts/case-init.ps1`, `master-route.ps1` (callable with pwsh)

**Kali-specific parts**:
- All scripts are bash (`.sh`)
- Package management uses `apt`
- Paths follow Linux conventions (`/opt/`, `~/tools/`, `/usr/bin/`)
- Kali preinstalls many tools, so the bootstrap logic is much simpler

---

## 1. Natural advantages of Kali

The following tools work **out of the box** in Kali 2026.1 (no bootstrap needed):

### Classic preinstalled tools

| Tool | Kali package | State |
|------|----------|------|
| nmap | nmap | Preinstalled |
| sqlmap | sqlmap | Preinstalled |
| hashcat | hashcat | Preinstalled |
| john | john | Preinstalled |
| hydra | hydra | Preinstalled |
| metasploit | metasploit-framework | Preinstalled |
| gobuster | gobuster | Preinstalled |
| ffuf | ffuf | Preinstalled |
| radare2 | radare2 | Preinstalled |
| binwalk | binwalk | Preinstalled |
| frida | python3-frida-tools | Preinstalled or pip |
| burpsuite | burpsuite | Preinstalled |
| wireshark | wireshark | Preinstalled |
| nikto | nikto | Preinstalled |
| wfuzz | wfuzz | Preinstalled |
| impacket | impacket-scripts | Preinstalled |
| netexec | netexec | Preinstalled |
| responder | responder | Preinstalled |
| aircrack-ng | aircrack-ng | Preinstalled |
| bloodhound | bloodhound | Installable with apt |
| ghidra | ghidra | Installable with apt |

### Tools new in Kali 2026.1 (March 2026)

| Tool | Package | Purpose |
|------|------|------|
| AdaptixC2 | adaptixc2 | Post-exploitation and adversary emulation framework |
| Atomic-Operator | atomic-operator | Cross-platform Atomic Red Team test execution |
| Fluxion | fluxion | WiFi security audit and social engineering |
| GEF | gef | Modern enhanced GDB debugging framework |
| MetasploitMCP | metasploitmcp | MCP server interface for Metasploit |
| SSTImap | sstimap | Automatic server-side template injection detection and exploitation |
| WPProbe | wpprobe | Fast WordPress plugin enumeration |
| XSStrike | xsstrike | Advanced XSS scanner |

### Tools new in Kali 2025.4 (December 2025)

| Tool | Package | Purpose |
|------|------|------|
| evil-winrm-py | evil-winrm-py | Python WinRM remote command execution |
| hexstrike-ai | hexstrike-ai | AI MCP security automation platform (150+ tools) |
| bpf-linker | bpf-linker | BPF static linker |

### Native Kali MCP tools (main focus)

| Tool | Package | Purpose | Install |
|------|------|------|------|
| mcp-kali-server | mcp-kali-server | Official Kali MCP; the AI calls terminal tools directly | `apt install mcp-kali-server` |
| MetasploitMCP | metasploitmcp | Metasploit MCP interface | `apt install metasploitmcp` |
| HexStrike AI | hexstrike-ai | MCP automation of 150+ security tools | `apt install hexstrike-ai` |

> **This is the biggest advantage of the Kali edition over the Windows edition**: the three MCP tools install directly with apt, with no manual GitHub/npm/Docker configuration.

This means `bootstrap-reverse.sh` has far less work on Kali than the Windows edition.

---

## 2. Quick start

### 2.0 One-step initialization (recommended for new systems)

```bash
# One-step configuration of a fresh Kali 2026.1 system (needs root)
sudo bash kali/scripts/quick-setup.sh

# Skip the system update (on slow networks)
sudo bash kali/scripts/quick-setup.sh --skip-update

# Minimal install (no AD or internal network tools)
sudo bash kali/scripts/quick-setup.sh --minimal
```

The script automatically completes: system update → install the 2026.1 tools → configure the native MCPs → install reverse engineering tools → refresh the index → print the report.

### 2.1 First configuration

```bash
# 1. Enter the project root
cd /path/to/cybersecurity-skills-router

# 2. Make the scripts executable
chmod +x kali/scripts/*.sh kali/scripts/lib/*.sh

# 3. Refresh the tool index (detect the local tool state)
bash kali/scripts/refresh-tool-index.sh

# 4. View the result
cat skills/tool-index.md
```

### 2.2 Set up the native Kali MCPs in one step (strongly recommended)

```bash
# Install the three official Kali MCPs
bash kali/scripts/bootstrap-reverse.sh mcp-kali-server metasploitmcp hexstrike-ai

# After install, the MCP configuration is written to ~/.claude/mcp.json automatically
# If you use Kiro, copy it manually to ~/.kiro/settings/mcp.json
```

### 2.3 Install the new 2026.1 tools

```bash
# Install all the new tools in one step
bash kali/scripts/bootstrap-reverse.sh adaptixc2 atomic-operator sstimap xsstrike wpprobe fluxion gef

# AD and internal network pentest suite
bash kali/scripts/bootstrap-reverse.sh coercer evil-winrm-py netexec responder bloodhound certipy
```

### 2.4 Install missing tools

```bash
# Install one tool
bash kali/scripts/bootstrap-reverse.sh jadx

# Install several tools
bash kali/scripts/bootstrap-reverse.sh jadx apktool frida jshookmcp

# Install and start services
bash kali/scripts/bootstrap-reverse.sh idapro --start-services
```

### 2.5 Let the AI client route automatically

Tell your AI client to read `kali/RULES-kali.md`; it completes the global injection automatically.

---

## 3. Path conventions

| Purpose | Kali path |
|------|----------|
| Tool install directory | `~/tools/` or `/opt/` |
| jadx | `/opt/jadx/` or `~/tools/jadx/` |
| apktool | `/usr/local/bin/apktool` (apt) or `~/tools/apktool/` |
| Ghidra | `/opt/ghidra/` or `~/tools/ghidra/` |
| IDA Pro | `/opt/idapro/` (if you have the Linux version) |
| Android SDK | `~/Android/Sdk/` |
| SecLists | `/usr/share/seclists/` (apt) or `~/tools/SecLists/` |
| Node.js | `/usr/bin/node` (apt/nvm) |
| Python | `/usr/bin/python3` (system default) |
| MCP configuration | `~/.claude/mcp.json` or `~/.kiro/settings/mcp.json` |

---

## 4. Summary of differences from the Windows edition

| Dimension | Windows edition | Kali edition |
|------|-----------|---------|
| Script language | PowerShell (.ps1) | Bash (.sh) |
| Package management | winget / GitHub Release ZIP | apt / pip / npm / GitHub Release tar.gz |
| Path separator | `\` | `/` |
| Environment variables | `%USERPROFILE%` | `$HOME` |
| Preinstalled tools | Almost none | Many security tools preinstalled |
| IDA start | `start.ps1` | Start the Linux IDA manually; the scripts only register and check MCP, unless you added a launcher locally |
| MCP configuration path | `%USERPROFILE%\.claude\mcp.json` | `~/.claude/mcp.json` |
| Port check | `TcpClient` | `nc -z` or `ss` |

---

## 5. Verification checklist

```bash
# ─── Basic commands ───
java -version
python3 --version
pip3 --version
node -v
npx -v

# ─── Reverse engineering tools ───
jadx --version
apktool --version
adb version
frida --version
r2 -v
gdb --version          # GEF loads automatically

# ─── Pentest tools (preinstalled on Kali) ───
nmap --version
sqlmap --version
hashcat --version
hydra -h | head -1
msfconsole --version
gobuster version
ffuf -V
nuclei -version

# ─── New Kali 2026.1 tools ───
sstimap -h 2>&1 | head -3
xsstrike -h 2>&1 | head -3
wpprobe --help 2>&1 | head -3
coercer -h 2>&1 | head -3
evil-winrm-py -h 2>&1 | head -3

# ─── AD and internal network tools ───
netexec --help 2>&1 | head -3
responder -h 2>&1 | head -3
certipy --version 2>&1 | head -1

# ─── Native Kali MCPs ───
which kali-server-mcp && echo "mcp-kali-server OK"
which metasploitmcp && echo "metasploitmcp OK"
which hexstrike-ai && echo "hexstrike-ai OK"

# ─── Refresh the tool index ───
bash kali/scripts/refresh-tool-index.sh

# ─── Check the MCP services (if configured) ───
nc -z 127.0.0.1 5000 && echo "mcp-kali-server OK" || echo "mcp-kali-server offline"
nc -z 127.0.0.1 8085 && echo "metasploitmcp OK" || echo "metasploitmcp offline"
nc -z 127.0.0.1 13337 && echo "IDA MCP OK" || echo "IDA MCP offline"
nc -z 127.0.0.1 23816 && echo "anything-analyzer OK" || echo "anything-analyzer offline"
```

---

## 6. Frequently asked questions

### Q: What if the radare2 shipped with Kali is too old?

```bash
# Install the latest version from the official source
bash kali/scripts/bootstrap-reverse.sh r2
# The Kali edition prefers installing or completing radare2 with apt by default; for the latest version, switch to GitHub or source per the platform docs
```

### Q: I use Parrot OS / BlackArch. Does it work?

Yes. The scripts check whether commands exist and are not bound to a specific distribution. Only the automatic installs that use `apt` may need to change to `pacman` (BlackArch).

### Q: How do I configure IDA Pro for Linux?

Install IDA to `/opt/idapro/`, then change the `startScript` path of `idapro` in `kali/scripts/bootstrap-manifest.json`.

### Q: I want to use this system on both Windows and Kali

No problem. Sync the `skills/` directory through Git, and both sides share the `field-journal/` experience. Only the scripts differ: Windows uses `skills/scripts/*.ps1` and Kali uses `kali/scripts/*.sh`.

