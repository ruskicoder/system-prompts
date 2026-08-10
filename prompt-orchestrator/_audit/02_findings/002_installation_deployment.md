# Finding 002 — Installation & Deployment Framework (`install/*` vs `DEPLOYMENT.md`, `QUICKSTART.md`)

## Status
matched

## Folder1 Content Summary
[install/](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/install) contains target platform installation scripts:
- `install-all.sh`: runs all platform installers
- `install-antigravity.sh`: installs orchestrator to Antigravity global context
- `install-codex.sh`: installs to Codex config
- `install-cursor.sh`: installs to Cursor (`.cursorrules`)
- `install-gemini.sh`: installs to Gemini prompt directory
- `install-opencode.sh`: installs to OpenCode directory

## Folder2 Content Summary
`openclaw-operator` provides host-level deployment via `DEPLOYMENT.md`, `QUICKSTART.md`, systemd user services (`systemd/orchestrator.service`), Docker Compose, and environment verification.

## Comparison
- **Pros of folder1**: Modular, lightweight bash target installers for multiple major AI IDEs / CLI tools (Cursor, Gemini, Codex, Antigravity, OpenCode).
- **Cons of folder1**: Missing an installer script for OpenClaw platform targets; lacks systemd user service template for persistent background background task / cron agent operation.
- **Pros of folder2**: Excellent systemd user service configuration, healthcheck liveness endpoints, container support.
- **Cons of folder2**: Heavyweight Node.js / Docker stack required for full deployment.

## Web Verification
- **Question checked**: Standard directory location for OpenClaw workspace instructions.
- **Result**: OpenClaw reads prompt specifications from workspace root (`AGENTS.md` / `AGENT.md`) and `.openclaw/` or custom workspace files.
- **Source**: OpenClaw Documentation (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**: 
1. Create `install/install-openclaw.sh` in folder1 to officially support OpenClaw as a target platform.
2. Add `install/systemd/prompt-orchestrator.service` template for running persistent agent daemon processes under systemd user mode.
3. Update `install/install-all.sh` to include `install-openclaw.sh`.

**Confidence**: high
**Status of implementation**: applied
