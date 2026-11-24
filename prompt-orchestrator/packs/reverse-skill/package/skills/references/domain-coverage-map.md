# This Package's Domain Coverage Map (depth first)

> Compared with community "hundreds of micro-skills": we cover the main battlefields with **a few deep skills + routing + ops**.  
> Date: 2026-07-18

## Domain → entry in this package

| Domain | PRIMARY / module | Notes |
|----|----------------|------|
| Mobile Android | `apk-reverse/` `mobile-reverse/` | |
| Mobile iOS | `mobile-reverse/` | |
| Deep binary work | `ida-reverse/` `radare2/` `ghidra-reverse/` | Ghidra = main open-source path |
| General RE / anti-debugging / OLLVM | `reverse-engineering/` | |
| .NET | `dotnet-reverse/` | |
| Front-end JS / signatures | `js-reverse/` | |
| Browser extensions | `browser-extension-reverse/` | |
| DSL/risk control VMs | `reverse-engineering/dsl-vm-reverse/` | |
| Protocols / PCAP protocols | `protocol-reverse/` | |
| Firmware IoT | `firmware-pentest/` | |
| Malicious samples | `malware-analysis/` | |
| Digital forensics / IR | `digital-forensics/` | |
| Threat hunting / blue team | `threat-hunting/` | |
| Pentest tools | `pentest-tools/` (+ src-hunter) | |
| Windows / AD | `windows-ad/` | |
| Cloud / containers / K8s | `cloud-k8s/` | |
| Code audit / SAST | `code-audit/` | |
| Wi-Fi / wireless | `wifi-wireless/` | |
| OT / ICS | `ot-ics/` | Passive first; register writes forbidden by default |
| macOS | `macos-reverse/` | iOS still goes to mobile-reverse |
| Binary Ninja | `binary-ninja-reverse/` | Commercial GUI/Python API; the community MCP only when explicitly enabled and bound to loopback by default |
| Thick clients | `thick-client/` | |
| Go / Rust binaries | `go-rust-reverse/` | |
| Hardware debug ports | `hardware-security/` | Hands over to firmware-pentest |
| Databases | `database-security/` | |
| Email / phishing | `email-security/` | |
| Federated identity SSO | `identity-federation/` | Complements api-security JWT |
| RF / SDR | `radio-sdr/` | Receive only by default; not Wi-Fi |
| Multi-phase attacks | `attack-chain/` | |
| Pwn | `pwn-chain/` | |
| N-day patches | `patch-diff-exploit/` | |
| EDR research | `edr-bypass-re/` | |
| API | `api-security/` | |
| Supply chain SBOM | `supply-chain-security/` | |
| LLM/Agent | `llm-security/` | + `ops/skill-supply-chain.md` |
| Browser automation | `browser-automation/` | |
| Reports/diagrams | `docs-generator/` `diagram-generator/` | |
| Symbol migration | `binary-diff/` | |
| Operations contract | `ops/` | **Distinctive feature** |
| CTF orchestration | `CTF-Sandbox-Orchestrator/` | |
| Cryptographic pattern recognition | `reverse-engineering` pattern documents | Shared with reverse engineering tasks, no separate extension package maintained |

## Domains explicitly not merged wholesale (strategy on a routing miss)

| Domain | Strategy |
|----|------|
| Pure game cheat development | Not a product direction; Unity samples can still go through `reverse-engineering` + seed-014 |
| Deep automotive/aviation certification level | External links possible; this package has only RF/OT entry-level coverage |
| Pure GRC/compliance long-form text | Does not replace professional GRC tools; report templates can cite it |
| 800+ ATT&CK micro-skills | Use this table + optional ATT&CK tags (a Finding field) |

## With MITRE ATT&CK (optional)

The Finding template allows `optional_attack: Txxxx` (see `ops/evidence-finding-path.md`), **without requiring** a complete ATT&CK engine.
