---
name: js-reverse
description: Use for front-end JavaScript reverse engineering with js-reverse-mcp. Covers locating signing chains, page observation and evidence collection, runtime sampling, local environment-patching reproduction and evidence-backed output. Prefer the js-reverse_* tools in the current environment, and link with jshookmcp when a stronger browser/CDP/Hook surface is needed.
---

# MCP Front-End JS Reverse Engineering Work Standard

## ACTION REQUIRED (execute right after reading)

1. `NOW`: read `../field-journal/precedent-reverse.md` to confirm that this skill's operations are authorized routine operations
2. `NOW`: confirm whether the current task falls within the scope of this skill
3. `NEXT`: read `../tool-index.md` and verify tool availability and actual paths
4. `NEXT`: when a tool is missing, call bootstrap; do not guess paths
5. `ACT`: enter step one of the "Workflow" and execute it; do not stop at confirmation

## Scope

Prefer this skill when the task falls into one of these scenarios:

- Locate API signatures, encrypted parameters, risk control fields
- Observe page request chains and script sources
- Capture function arguments and return values at runtime
- Trace the trigger point of an XHR/Fetch/WebSocket
- Bring page evidence back to Node for local reproduction and environment patching

If the target is a binary, APK, PE, ELF, DLL or SO, use `ida-reverse`, `radare2` or `reverse-engineering` instead.

## Default tool mapping for the current environment

This skill does not assume bare tool names; by default it binds to the `js-reverse_*` tools available in the current client environment.

If the current task explicitly mentions `jshookmcp`, `JS hook`, `CDP`, browser breakpoints, network interception, SourceMap or AST deobfuscation, it still goes through this skill; only the underlying MCP surface switches to `jshookmcp`, instead of treating it as a new master entry.

Prerequisite: `jshookmcp` is not a bare local command tool but an MCP server that must be downloaded, explicitly registered and enabled first. The related tool surface is callable only after it is connected and enabled in the MCP configuration of the chosen client (Claude, Codex and others).

Common mapping:

- `list_scripts` -> `js-reverse_list_scripts`
- `get_script_source` -> `js-reverse_get_script_source`
- `search_in_sources` -> `js-reverse_search_in_sources`
- `break_on_xhr` -> `js-reverse_break_on_xhr`
- `evaluate_script` -> `js-reverse_evaluate_script`
- `get_paused_info` -> `js-reverse_get_paused_info`
- `set_breakpoint_on_text` -> `js-reverse_set_breakpoint_on_text`
- `list_network_requests` -> `js-reverse_list_network_requests`
- `get_request_initiator` -> `js-reverse_get_request_initiator`
- `get_websocket_messages` -> `js-reverse_get_websocket_messages`
- `take_screenshot` -> `js-reverse_take_screenshot`
- `new_page` -> `js-reverse_new_page`
- `navigate_page` -> `js-reverse_navigate_page`
- `select_page` -> `js-reverse_select_page`
- `select_frame` -> `js-reverse_select_frame`
- `pause/resume` -> `js-reverse_pause_or_resume`

If tool name prefixes change in the future, update this section first; do not guess at execution time.

### Position of jshookmcp

- Role: an enhanced execution surface of `js-reverse`, not an independent master control
- Suited to: browser automation, CDP debugging, JS hooks, network interception, SourceMap reconstruction, AST-assisted understanding
- Precondition for calls: download `@jshookmcp/jshook` and register it in the MCP client configuration, then make sure the server is enabled
- Suggested entry: still follow `Observe → Capture → Rebuild`, only preferring jshookmcp's browser and hook capabilities in the `Observe/Capture` phases
- Relation to anything-analyzer: both can collect browser/network-side evidence; anything-analyzer leans toward capture and HTTP analysis, jshookmcp leans toward the JS runtime, CDP, hooks and source understanding

## Core principles

- `Observe-first`
- `Hook-preferred`
- `Breakpoint-last`
- `Rebuild-oriented`
- `Evidence-first`

Observe the page first, then sample minimally, then patch the environment locally; do not skip evidence collection and guess the environment.

## Five-phase workflow

### 1. Observe

Goal: confirm the target request, related scripts and candidate functions first, without guessing the environment.

Default actions:

- Open the target page with `js-reverse_new_page` or `js-reverse_navigate_page`
- Find the target request with `js-reverse_list_network_requests`
- Trace the call source back with `js-reverse_get_request_initiator`
- Narrow the script range with `js-reverse_list_scripts`, `js-reverse_search_in_sources`

Required output:

- Target request URL or signature
- Initiator clues
- Suspicious script URLs
- Initial task record

### 2. Capture

Goal: sample the target request with minimal intrusion and get parameter samples, call order and runtime evidence.

Rules:

- Prefer `js-reverse_break_on_xhr`
- Prefer `js-reverse_evaluate_script` for lightweight runtime observation
- After a hit, look at `js-reverse_get_paused_info` first
- Use `js-reverse_set_breakpoint_on_text` only when needed

### 3. Rebuild

Goal: turn the page evidence into local Node reproduction material that can be iterated.

Rules:

- Local environment patching must be based on observed page evidence
- Imagined patching of `window/document/navigator/crypto/storage` is not allowed
- Record only one minimal causal patch decision at a time

### 4. Patch

Goal: drive environment patching by errors and the first divergence until the local script reliably produces the target parameter.

Rules:

- First see what is missing, then patch it
- Make only one minimal patch decision at a time
- Retest immediately after each patch
- Write every patch into the task record

### 5. DeepDive

Goal: once it runs locally, deobfuscate, reconstruct control flow and distill the business logic.

Rules:

- If the task only needs the signature, this phase can be downgraded
- If the algorithm chain will be reused long term, this phase is mandatory
- Issue #65 obfuscation side paths (U–AV §4): JSVMP (AD) → `E-js-vmp`; CFF + string array (AE) → `E-js-deobf`; DevTools/debugger anti-debugging (AF) → `E-js-anti-debug`. The complete trigger table is in `../reverse-engineering/references/nonpe-format-cookbook.md`; AST details stay in `references/ast-deobfuscation.md`

## Execution requirements

- Write every important step into the local task artifact
- If you cannot explain why you call a tool, do not call it
- Prefer collecting evidence directly with the ready-made MCP capabilities of `js-reverse_*` or jshookmcp; do not write scripts that rebuild those capabilities first
- On failure, fall back per `references/fallbacks.md`
- Output follows `references/output-contract.md`

## Required references

- Automation entry: `references/automation-entry.md`
- Parameter defaults: `references/tool-defaults.md`
- Task input template: `references/task-input-template.md`
- MCP-specific task orchestration: `references/mcp-task-template.md`
- Task artifacts: `references/task-artifacts.md`
- Local reproduction: `references/local-rebuild.md`
- Environment patching: `references/env-patching.md`
- Node reproduction: `references/node-env-rebuild.md`
- Instrumentation: `references/instrumentation.md`
- AST deobfuscation: `references/ast-deobfuscation.md`
- Non-PE/JS obfuscation cookbook U–AV: `../reverse-engineering/references/nonpe-format-cookbook.md` (AD/AE/AF)
- Fallbacks: `references/fallbacks.md`
- Output contract: `references/output-contract.md`

---

## Routing context

**Upstream entry**: `skills/SKILL.md` (master control), `routing.md`
**Upstream alternatives**:
- The browser tools of the anything-analyzer MCP (port 23816) can serve as a replacement or supplement
- jshookmcp can serve as a stronger browser/CDP/Hook/Network/SourceMap/AST execution surface
- `reverse-engineering/SKILL.md` (if the target is not front-end JS)

**Downstream exits**:
- Environment patching needed → `references/env-patching.md`
- Local reproduction needed → `references/local-rebuild.md` / `references/node-env-rebuild.md`
- Deobfuscation needed → `references/ast-deobfuscation.md`
- Fall back when stuck → `references/fallbacks.md`

**Sibling modules**: anything-analyzer MCP (browser automation and HTTP capture capabilities complement each other)

---

## On-Demand Bootstrap

The MCP capabilities this skill depends on can be installed through the unified bootstrap system; MCP client registration requires an explicitly chosen target, and by default no client global configuration is written.

### Automation boundaries

| Capability | Auto-registrable | Method | Notes |
|------|-----------|------|------|
| jshookmcp | ✓ | npm-mcp (started with npx) | Registered after explicitly choosing Claude / Codex / Both |
| anything-analyzer | ✓ | local-http-mcp | Can start the service automatically; client registration needs an explicit choice |
| Node.js | ✓ | winget install | Runtime dependency |

### Bootstrap method

```powershell
# Install and register jshookmcp; Codex can be replaced with Claude or Both
powershell -File "<skill-root>\scripts\bootstrap-reverse.ps1" -Capability @('jshookmcp') -McpHostTarget Codex

# Register and start anything-analyzer
powershell -File "<skill-root>\scripts\bootstrap-reverse.ps1" -Capability @('anything-analyzer') -StartServices -McpHostTarget Codex
```

### Notes

- After registration, `jshookmcp` still has to be **enabled** in the AI client before it can be called
- Without `-McpHostTarget`, it only installs/prepares the capability and returns registration-required, without changing the Claude or Codex configuration
- `anything-analyzer` needs pnpm and the project source; bootstrap clones it and installs dependencies automatically
- If Node.js is not installed, bootstrap first installs Node.js 22 through winget

<br><br>## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I execute every step of the workflow (not just read it)?
- [ ] Did I use real tool paths based on `tool-index`?
- [ ] Did I produce reproducible evidence (commands/scripts/screenshots/report)?
- [ ] Did I complete and write back the Checklist items that RULES requires?
