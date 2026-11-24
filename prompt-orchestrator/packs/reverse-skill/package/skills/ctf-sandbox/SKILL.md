---
name: ctf-sandbox
description: Thin PRIMARY for CTF / AWD / cyber range multi-type orchestration. Hands off to the sidecar CTF-Sandbox-Orchestrator. Use when the user says CTF, AWD, cyber range, or competition challenge and no more specific pwn/APK/IDA route already won.
---

# CTF sandbox entry (sidecar, not a second router)

## ACTION REQUIRED (execute right after reading)

1. `NOW`: run `../scripts/case-init.ps1`; ACT against the real internet is forbidden before `auth.status=granted`. For competitions/cyber ranges use `-NetworkProfile lab` or `offline`.
2. `NOW`: open `../../CTF-Sandbox-Orchestrator/ctf-sandbox-orchestrator/SKILL.md` under the package root and continue under its sandbox assumptions.
3. `MUST NOT` write the 40+ `competition-*` sub-skills into `routing.json`. This entry is only one PRIMARY gate.
4. `ACT`: the orchestrator picks one downstream `competition-*`. When the specific challenge type is clear (pwn/ROP, APK, IDA), a rule earlier in `routing.json` should already have won; do not take it over.

## Why a separate layer

`CTF-Sandbox-Orchestrator/` is a **GPL sidecar package** whose authorization defaults to the sandbox interior. The core routing package stays MIT + the `scope.md` gate. This skill is only a keyword entry and does not merge the competition tree into the core.

## Task completion self-check (MUST pass before claiming completion)

- [ ] Did I run case-init / scope first, instead of treating "the user said CTF" as authorization for the internet?
- [ ] Did I open the sidecar orchestrator, instead of treating 40 sub-skills as PRIMARY?
- [ ] If the task is actually pwn/APK/IDA, did I let the more specific PRIMARY take over?
