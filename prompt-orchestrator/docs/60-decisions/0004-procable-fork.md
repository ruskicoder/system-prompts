---
id: decisions.procable-fork
type: adr
status: approved
owner: Do Dang Khoa
summary: "Adopt Impeccable's design skill and hooks as procable, an offline, renamed fork maintained in ruskicoder/procable and installed by prompt-orchestrator, with communication-tone above its directives."
superseded_by: none
---

# Decision

## Context
Vetting (2026-11-02) found Impeccable the strongest design skill available, with hooks worth
keeping. It also sends telemetry and update checks to its vendor, fetches design directions and
images from a hosted service, downloads its engine on first run, and injects directives that
conflict with communication-tone (autonomy, subagent authorisation, self-written ignores).

## Decision
- Fork it as procable (Apache-2.0, upstream attribution kept), maintained in `ruskicoder/procable`.
- procable runs fully offline once installed: one egress guard allows loopback only; telemetry,
  update check, catalog roll, card images, image API and every download path are removed.
- Rename fully (crates, binary, env vars, folders, skill and command) with a re-runnable
  transform so upstream fixes can still be merged and re-vetted.
- communication-tone and the harness overlay take precedence over every procable directive; every
  change procable makes on its own is reported.
- Add a WCAG 2.2 AA `a11y` command; prompt-orchestrator's `accessibility-review` points to it.
- Engine binaries are built in the fork's CI (Windows unsigned) and installed by
  `install/install_procable.py` from a release pinned by digest.

## Alternatives
- Install upstream as is: rejected, telemetry and network calls, conflicting directives.
- Re-author only the practices, no hooks: rejected by the user, who wants the hooks.
- Rename user-facing names only: rejected by the user in favour of a full rename.

## Consequences
- Upstream updates arrive only through a deliberate sync, the rename transform and a re-vet.
- New-work direction rounds use the local degraded path (no hosted catalog).
- Windows may show a SmartScreen warning for the unsigned engine.
