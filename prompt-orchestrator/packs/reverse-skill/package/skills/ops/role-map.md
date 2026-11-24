# Specialist Role → Skill Mapping (No Multi-Agent Server)

> The role codes are inspired by the Z3r0 specialist team; the **implementation** is reverse-skill routing and a handoff protocol, not process orchestration.

## Role table

| Code | Name (localizable) | Responsibilities | PRIMARY / tool skill |
|------|------------------|------|----------------------|
| **lead** | Lead / commander | Split tasks, set scope, gate phases, compile the report | `attack-chain/` or the current PRIMARY hub; end → `docs-generator/` |
| **cie** | Intelligence gathering | Asset discovery, exposure surface, relationships | `pentest-tools/` (recon); browser → `browser-automation/`; cloud surface → `cloud-k8s/` |
| **cpe** | Penetration verification | Scanning, exploitation verification, impact confirmation | `pentest-tools/`; API → `api-security/`; AD → `windows-ad/`; wireless → `wifi-wireless/`; database → `database-security/`; SSO → `identity-federation/`; OT → `ot-ics/` |
| **cre** | Reverse engineering | Binary/firmware/mobile/front-end logic | `ida-reverse/` `ghidra-reverse/` `binary-ninja-reverse/` `radare2/` `apk-reverse/` `mobile-reverse/` `macos-reverse/` `js-reverse/` `browser-extension-reverse/` `dotnet-reverse/` `go-rust-reverse/` `firmware-pentest/` `hardware-security/` `malware-analysis/` `protocol-reverse/` `thick-client/` `reverse-engineering/` |
| **cae** | Code audit | Source/dependencies/supply chain | `code-audit/` + `supply-chain-security/` |
| **cbe** | Blue team/forensics | Hunting, detection, IR artifacts | `threat-hunting/` `digital-forensics/` |
| **cce** | Cryptography | Algorithm/protocol/key misuse | `reverse-engineering` pattern documents |
| **llm** | AI security | Prompt/Agent | `llm-security/` |
| **doc** | Documentation officer | Report/writeup/diagrams | `docs-generator/` + `diagram-generator/` |

## Lead mandatory protocol

```text
1. Output PRIMARY (master-route) + lead_role=lead
2. Write scope.md (ops/scope-contract)
3. Specify specialist_roles[] and handoff conditions
4. At the end of each phase: update timeline + workitems; decide to continue/switch roles/produce the report
5. Skipping scope and going straight to cpe scans of production is forbidden
```

## Handoff rules

| From → to | Trigger | Deliverable |
|---------|------|--------|
| lead → cie | Asset surface needed | scope + known domains/IPs |
| cie → cpe | Live surface/services exist | Asset list + ports/URLs |
| cpe → cre | Reverse verification/client logic needed | Sample path + suspicious points |
| cre → cpe | Protocol/key/check reconstructed | Algorithm description + reproduction commands |
| any → doc | Phase or task complete | Evidence/Finding/Path draft |
| any → lead | Blocked/out of authorization/path change | timeline note + blocked reason |

## How a single agent uses it (distinctive feature)

No need to start 6 real agents:

```text
Within one session:
  [lead] plan
  [cie] run the reconnaissance skill
  [cpe] switch to pentest-tools
  …
Use role prefix tags in output so the timeline is easy to search:
  [cpe] nuclei high findings → E-003
```

## Relation to master-route

- `master-route` sets the **PRIMARY skill**  
- `role-map` sets **who is responsible in the current phase** (can be written in scope.md)  
- For multi-phase tasks PRIMARY is often `attack-chain/`, and lead dispatches from there  

## MUST NOT

- Do not assume a Z3r0 session API exists  
- Do not start extra scans of unauthorized targets for a role  
