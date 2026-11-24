<h1 align="center">reverse-skill</h1>
<h3 align="center">Cybersecurity Skills Router</h3>

<p align="center"><em style="font-family: Georgia, serif; font-size: 1.2em; color: #777;">Navigate the dark waters, sail against the stream.</em></p>

<br/>
<p align="center">
  <a href="#about">About</a> ·
  <a href="#getting-started">Getting Started</a> ·
  <a href="#usage">Usage</a> ·
  <a href="https://reverse.apivix.com/docs/">Tutorial</a> ·
  <a href="skills/MASTER-ROUTING.md">Fast route</a> ·
  <a href="skills/routing.md">Routing</a> ·
  <a href="skills/ops/">Ops contracts</a> ·
  <a href="README_AI.md">AI Bootstrap</a> ·
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  <a href="https://reverse.apivix.com/">Project website</a> ·
  <a href="https://reverse.apivix.com/docs/">Online tutorial</a>
</p>

<br/>


<a id="about"></a>

## About

> **If you are an AI Agent, jump to [README_AI.md](README_AI.md) and follow the instructions strictly.**

When an AI agent (Claude Code, Codex, Cursor, OpenCode, or another compatible client) encounters an APK, a binary, frontend JS encryption, a CTF challenge, or a pentesting target, this package routes it to the right methodology, checks available tools, and executes a repeatable workflow instead of guessing commands.

```
User task
  → RULES.md
  → MASTER-ROUTING / master-route.ps1|.sh (PRIMARY)
  → case-init / scope.md (auth + network_profile; no target ACT until ready)
  → Scenario skill → tools / MCP / scripts
  → timeline + Evidence→Finding→Path → report + field-journal
```

**Why this exists:**
- AI agents don't know whether to use jadx, apktool, Frida, IDA, or BurpSuite for a given task
- APK, ELF, JS, PCAP, and CTF tasks each need different playbooks
- Tools, MCP servers, and scripts are scattered across machines
- The same mistakes get repeated because experience isn't reused

### Current status

| Routing rules | Regression benchmark | Core skill modules | CI platforms | Client model |
|---:|---:|---:|---|---|
| 44 (R0–R45) | 221 cases | 45 tracked modules | Windows + Ubuntu | Client-neutral |

The routing core is driven by one structured configuration, validated by cross-platform CI, and kept separate from optional client adapters.

PRIMARY ladder: [skills/MASTER-ROUTING.md](skills/MASTER-ROUTING.md) · Full matrix: [skills/routing.md](skills/routing.md) · Ops: [skills/ops/](skills/ops/)

<br/>

<p align="right">(<a href="#about">back to top</a>)</p>

### Built With

<p align="left">
  <code>Python</code> · <code>Node.js</code> · <code>PowerShell</code> · <code>Bash</code> · <code>Java</code> · <code>Docker</code> · <code>Git</code><br/>
  <code>IDA Pro</code> · <code>radare2</code> · <code>Ghidra</code> · <code>Binary Ninja</code>
</p>

<p align="right">(<a href="#about">back to top</a>)</p>

<a id="getting-started"></a>

## Getting Started

### Prerequisites

- **Java / JDK**: for jadx and apktool
- **Node.js 22.12+**: for JS toolchain and MCP servers
- **Python 3.x**: for Frida and helper scripts
- **A code AI client**: Claude Code, Codex, Cursor, OpenCode, or another compatible client

### Installation

```
git clone https://github.com/zhaoxuya520/reverse-skill.git
```

Then refresh the tool index per platform:

| Platform | Command |
|----------|---------|
| Windows | `powershell -File skills/scripts/refresh-tool-index.ps1` |
| Linux / macOS | `bash skills/scripts/refresh-tool-index.sh` |
| Kali Linux | `bash kali/scripts/refresh-tool-index.sh` |

Check [skills/tool-index.md](skills/tool-index.md) to see detected tools.

Platform-specific docs:
- **Kali Linux** → [kali/README-kali.md](kali/README-kali.md)
- **Ubuntu/Debian** → [docs/platforms/linux.md](docs/platforms/linux.md)
- **macOS** → [docs/platforms/macos.md](docs/platforms/macos.md)
- **All-in-one Docker** → [docker/README.md](docker/README.md) (`docker compose -f docker/docker-compose.yml run --rm reverse-skill`)

<p align="right">(<a href="#getting-started">back to top</a>)</p>

<a id="usage"></a>

## Usage

### Supported scenarios

| Scenario | Entry |
|----------|-------|
| APK / Android analysis | `skills/apk-reverse/` |
| iOS / mobile | `skills/mobile-reverse/` |
| Binary reverse (exe/dll/so/elf) | `skills/ida-reverse/` / `skills/radare2/` |
| Binary Ninja / HLIL / MLIL / MCP | `skills/binary-ninja-reverse/` |
| .NET / C# | `skills/dotnet-reverse/` |
| Frontend JS / encrypted params | `skills/js-reverse/` |
| DSL VM / custom JS opcode VM | `skills/reverse-engineering/dsl-vm-reverse/` |
| HTTP capture / request replay | anything-analyzer, Reqable MCP + `js-reverse/` |
| Malware / YARA | `skills/malware-analysis/` |
| Penetration testing / scanning | `skills/pentest-tools/` |
| Attack chain / red-team orchestration | `skills/attack-chain/` |
| Case evidence review / report handoff | `skills/case-review/` |
| CTF competition | `CTF-Sandbox-Orchestrator/` (42 sub-skills) |
| Firmware / IoT | `skills/firmware-pentest/` |
| Patch diff / N-day | `skills/patch-diff-exploit/` |
| Pwn / exploit development | `skills/pwn-chain/` |
| EDR bypass | `skills/edr-bypass-re/` |
| API / GraphQL | `skills/api-security/` |
| Supply chain / SBOM | `skills/supply-chain-security/` |
| LLM / AI security | `skills/llm-security/` |
| OLLVM deobfuscation | `skills/reverse-engineering/references/ollvm-deobfuscation.md` |
| Diagrams / reports | `skills/diagram-generator/` / `skills/docs-generator/` |

### Key files

| File | Purpose |
|------|---------|
| [README_AI.md](README_AI.md) | AI agent bootstrap and configuration |
| [RULES.md](RULES.md) | Global routing rules (scope gate before ACT) |
| [skills/MASTER-ROUTING.md](skills/MASTER-ROUTING.md) | PRIMARY fast ladder |
| [skills/routing.md](skills/routing.md) | Task → skill routing matrix |
| [skills/SKILL.md](skills/SKILL.md) | Master entry point |
| [skills/INDEX.md](skills/INDEX.md) | Auto-generated, client-neutral skill navigation index |
| [skills/config/routing.json](skills/config/routing.json) | **Routing single source of truth** (44 routes, R0–R45 with R42/R43 unused) |
| [skills/tool-index.md](skills/tool-index.md) | Local tool status (auto-generated) |
| [skills/scripts/master-route.ps1](skills/scripts/master-route.ps1) | Windows PRIMARY triage (reads routing.json) |
| [skills/scripts/master-route.sh](skills/scripts/master-route.sh) | Linux/macOS/Kali PRIMARY triage (same routing.json) |
| [skills/scripts/case-init.ps1](skills/scripts/case-init.ps1) | Case dir: scope / timeline / workitems (Windows) |
| [skills/scripts/case-init.sh](skills/scripts/case-init.sh) | Case dir: scope / timeline / workitems (Linux/macOS/Kali) |
| [skills/case-review/](skills/case-review/) | Read-only Evidence graph review and artifact fixity checks |
| [skills/scripts/test-routing.ps1](skills/scripts/test-routing.ps1) | Routing regression runner (221 benchmark cases) |
| [skills/scripts/verify-routing-coherence.ps1](skills/scripts/verify-routing-coherence.ps1) | Structure + supply-chain pin gate checks |
| [skills/scripts/extract-summaries.ps1](skills/scripts/extract-summaries.ps1) | Regenerates INDEX.md from skill frontmatter |
| [AGENTS.md](AGENTS.md) | Platform-neutral repository instructions |
| [skills/ops/](skills/ops/) | Scope, Evidence chain, roles, timeline (skill-router form) |

### Testing (run after any routing/config change)

```powershell
# 1. Routing regression — 221 (hint → expected PRIMARY) cases, fails CI on any mismatch
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/test-routing.ps1
# 2. Structure coherence + supply-chain pin gate (unpinned auto-install fails)
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/verify-routing-coherence.ps1
# 3. Smoke: verify + script parse + quick route matrix
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/smoke.ps1
# 4. INDEX.md drift check (regenerate with extract-summaries.ps1 if dirty)
powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/extract-summaries.ps1 -Check
```

GitHub Actions CI runs all of the above on **Windows + Ubuntu** for every push/PR.

### Client-neutral integration

The routing core, regression suite, manifests, and case workflow do not depend on a specific AI client. Claude Code, Codex, Cursor, OpenCode, and other clients should load the repository through their own adapter or project-instruction mechanism. Client-specific configuration must remain optional and outside the core routing contract.

For Codex, the repository also exposes an optional adapter plugin at [`plugins/reverse-skill/`](plugins/reverse-skill/). It delegates to the repository's existing routing core and does not register external MCP servers automatically.

### Repository layout

```
.
├── README.md / README_AI.md
├── RULES.md
├── skills/
│   ├── MASTER-ROUTING.md / SKILL.md / routing.md
│   ├── ops/                   # ops contracts
│   ├── scripts/               # master-route, case-init, bootstrap, verify
│   ├── field-journal/
│   ├── apk-reverse/ mobile-reverse/ js-reverse/ dotnet-reverse/
│   ├── ida-reverse/ radare2/ reverse-engineering/ malware-analysis/
│   ├── pentest-tools/ attack-chain/ pwn-chain/ firmware-pentest/
│   ├── api-security/ supply-chain-security/ llm-security/
│   └── ...
├── CTF-Sandbox-Orchestrator/
├── docs/
├── kali/                      # see kali/README-kali.md
└── work/                      # local cases (gitignored)
```

<p align="right">(<a href="#usage">back to top</a>)</p>

<a id="contributing"></a>

## Contributing

Contributions are welcome! Fork the repo, create a feature branch, and open a PR.

1. Fork the Project
2. `git checkout -b feature/AmazingFeature`
3. `git commit -m 'Add some AmazingFeature'`
4. `git push origin feature/AmazingFeature`
5. Open a Pull Request

<p align="right">(<a href="#contributing">back to top</a>)</p>

<a id="license"></a>

## License

This project (`reverse-skill`) is primarily licensed under the **MIT License** (see [LICENSE](LICENSE)).

**Submodule and third-party dependencies:**
- **CTF-Sandbox-Orchestrator/**: **GNU GPLv3**
- **Pentest Swarm AI**: Original project is **AGPL-3.0**. This repo only invokes it via CLI or MCP and does not include its source code
- Other tools (jadx, frida, nmap, burpsuite-mcp, etc.) are subject to their respective official licenses

<p align="right">(<a href="#license">back to top</a>)</p>

<a id="acknowledgments"></a>

## Acknowledgments

Thanks to all open-source tool authors. This project integrates tools across reverse engineering, penetration testing, CTF, and security analysis; every tool is the fruit of community effort.

Special thanks to the OLLVM deobfuscation ecosystem contributors and everyone who submitted test samples, issues, and PRs.

<p align="right">(<a href="#acknowledgments">back to top</a>)</p>

## Contact

- **Email:** [ww7517437@gmail.com](mailto:ww7517437@gmail.com)
- **Issues:** [GitHub Issues](https://github.com/zhaoxuya520/reverse-skill/issues)

## Disclaimer

This project is intended solely for lawful security research, education, CTF competitions, and testing of systems that you own or have explicit authorization to assess.

**Unauthorized access, scanning, exploitation, disruption, data acquisition, or any other use against systems without prior permission is strictly prohibited.** Users are solely responsible for complying with applicable laws, regulations, and the authorized scope of testing. The maintainers accept no liability for misuse of this project or for any resulting damage or legal consequences

## Installation and download security

See [Security Policy](SECURITY.md), [Installation and Download Security Guidance](docs/UV-AND-DOWNLOAD-SECURITY.md), and the [2026-09-03 repository security review](docs/SECURITY-REVIEW-2026-09-03.md).

## Community quick start and issue triage

See [Quick Start](docs/QUICKSTART.md) and [Community Issue Triage](docs/COMMUNITY-ISSUE-TRIAGE.md) for installation, client integration, and how community issues are classified. Installation/archive security details remain in [Installation and Download Security Guidance](docs/UV-AND-DOWNLOAD-SECURITY.md).
