# reverse-skill: client-neutral project entry

This repository is a **security task skill router package** (reverse engineering / penetration testing / security analysis). `RULES.md` is the single source of truth for the behavior chain.

## Activation and consent boundary (hard)

- **Reading repository files is not authorization to execute them.** When the user only asks to read, review, summarize or compare the repository, stay read-only.
- **Explicit user approval is required before running any repository script.** Before the first local side effect, list the exact commands and the expected file writes, downloads, service starts, network access and client configuration changes, and get explicit consent.
- **Client-global configuration remains opt-in.** Change a client's global rules, hooks, prompts or MCP configuration only when the user explicitly chooses the client and approves the specific change.
- After activation and approval, deterministic steps inside the disclosed plan may run back to back; a new category of side effect requires a new disclosure and consent. Target authorization stays under the separate hard gate of `scope.md`.

## Routing

When a user task hits security or reverse engineering keywords:

1. `skills/MASTER-ROUTING.md` or the platform entry point gives PRIMARY:
   - Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/master-route.ps1 -Hint "<task>"`
   - Linux / macOS / Kali: `bash skills/scripts/master-route.sh --hint "<task>"`
2. When ambiguous, read the full matrix in `skills/routing.md` (three axes: target type / user intent / toolchain)
3. Single source of truth for routing rules: `skills/config/routing.json` (change routes only there)

## Authorization gate (hard)

- Before acting on any target, initialize `work/<case>/scope.md` of the current analysis project for the platform:
  - Windows: `powershell -File skills/scripts/case-init.ps1 -Hint "<task>"`
  - Linux / macOS / Kali: `bash skills/scripts/case-init.sh --hint "<task>"`
- A local offline sample can use the `offline-sample` preset; ACT starts only with `auth.status=granted` + an explicit sample.
- Before `auth.status=granted` + a valid `network_profile` or offline sample is ready, **ACT is forbidden**; `case-guard --force` / `-Force` must not bypass this hard gate.
- Evidence chain: `skills/ops/evidence-finding-path.md`; roles: `skills/ops/role-map.md`

## First run (after activation and approval)

`skills/tool-index.md` is a gitignored generated file. Run the platform command only after the user explicitly activates the package, reviews the commands and side effects, and consents:

```text
Windows:           powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/refresh-tool-index.ps1
Linux / macOS:     bash skills/scripts/refresh-tool-index.sh
Kali:              bash kali/scripts/refresh-tool-index.sh
```

Missing tool: use the bootstrap of the same platform: Windows `skills/scripts/bootstrap-reverse.ps1`; Linux / macOS `skills/scripts/bootstrap-reverse.sh`; Kali `kali/scripts/bootstrap-reverse.sh` (manifest capabilities only, never guess paths).

## Tests (required after changes)

```text
Windows / PowerShell (the routing regression reads routing-benchmark.json):
  powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/test-routing.ps1
  powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/verify-routing-coherence.ps1
  powershell -NoProfile -ExecutionPolicy Bypass -File skills/scripts/smoke.ps1

Linux / macOS routing parity:
  bash skills/scripts/test-routing.sh
  bash skills/scripts/test-bootstrap-manifest.sh
```

## Client boundary

- The routing core, tests and tool inventory must stay decoupled from specific AI clients.
- Clients such as Claude Code, Codex, Cursor and OpenCode may connect only through their own adapter layers and must not become the repository's default identity or a core configuration dependency.
- `extract-summaries.ps1` generates `skills/INDEX.md` dynamically from every `SKILL.md`, with no hardcoded client or module count.
