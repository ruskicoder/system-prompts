# Timeline + WorkItem / Coverage

> Replayable operations record (Z3r0 timeline idea) + coverage checkboxes (WorkItem idea).  
> Everything lives in **`work/<case>/`** (gitignored in the repository), not in the skill package body.

## Directory convention

```text
work/<case>/
  scope.md           # contract (ops/scope-contract.md)
  timeline.md        # append-only; changing past entries is forbidden
  workitems.md       # work items and coverage
  evidence/          # raw artifacts (screenshots, pcap, logs)
  notes/
  report/            # final report draft or copy
```

Initialization:

```powershell
powershell -File skills\scripts\case-init.ps1 -Hint "full pentest" -CaseName "acme-2026"
```

## timeline.md format

Every record is **append-only**:

```markdown
## {ISO-8601} | {role} | {phase}
- action:
- command_or_ref:
- result_summary:
- artifacts: []      # relative paths under this case
- evidence_ids: []   # E-xxx when promoted
- decision_delta: [] # only decisions changed since the previous transition
- carry_forward_refs: [scope.md] # unchanged authoritative state is referenced, not re-serialized
- next:
```

**MUST NOT** delete or rewrite existing `##` time blocks (corrections use a new entry + `corrects: {timestamp}`).

### Decision delta boundary

`scope.md`, `workitems.md` and the existing Evidence are the current authoritative state. `timeline.md` records transitions and does not copy the complete snapshot.

- Every real stage/turn transition **MUST** write `decision_delta`; list only the decisions that actually changed from the previous state to the current state and that affect later actions. When nothing changed, write `[]`.
- An unchanged route, auth, scope, network profile, tool capability or existing hypothesis/Evidence **MUST NOT** be spelled out again for the handoff; reference the authoritative file or entry in `carry_forward_refs`.
- The consumer **MUST** resolve `carry_forward_refs` first, then apply `decision_delta` over the working context; it must not treat the delta as the complete state.
- It is a genuine decision boundary only when there are two or more materially different, evidence-supported branches and the user's choice changes the next action; deterministic transitions continue directly without restating context to manufacture a menu.

Representative transition: if auth/scope/route are unchanged for `Triage -> Static`, record only `decision_delta: [phase=triage->static]`, and inherit the remaining state with `carry_forward_refs: [scope.md, evidence/E-triage.md]`.

## workitems.md template

```markdown
# Work Items

| ID | title | role | targets | surface | status | evidence | notes |
|----|-------|------|---------|---------|--------|----------|-------|
| WI-001 | Port scan edge | cie | {ip} | network | done | E-001 | |
| WI-002 | Auth bypass check | cpe | /api/login | web | blocked | | need creds |

status: pending | in_progress | blocked | done | cancelled

## Coverage
- [ ] Recon complete for in_scope assets
- [ ] Critical/High candidates triaged
- [ ] Validated findings have Evidence
- [ ] Path documented (attack/call/solve)
- [ ] Timeline continuous (no silent gaps >1 major phase)
- [ ] Report exported via docs-generator
- [ ] field-journal written (anonymized)
```

## attack-chain / pentest hooks

| Skill | MUST |
|-------|------|
| `attack-chain/` | Multi-phase tasks create the case directory; update workitems + timeline at the end of each phase |
| `pentest-tools/` | At least 1 timeline entry after each tool batch; finding → Evidence draft |
| Other RE skills | Timeline recommended; complete the Evidence chain at least before producing the report |

## Distinctive features

- Agent-friendly plain text, friendly to diff/review  
- Cross-references the command paths in tool-index  
- No dependency on WebSocket live streaming; paste the timeline into the report when needed  
