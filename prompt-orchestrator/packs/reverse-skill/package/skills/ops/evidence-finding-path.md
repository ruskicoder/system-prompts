# Evidence → Finding → Path Evidence Chain

> Inspired by the Z3r0 Evidence Plane, implemented as a **Markdown field contract**.  
> reverse-skill distinctive feature: bound to the `docs-generator` report templates, `field-journal` redacted write-back and reproducible commands.

## 1. Evidence (immutable observation)

Each piece of evidence gets its own paragraph or table row:

```markdown
### E-{nnn}
- title:
- observed_at:
- source_type: command | screenshot | file | log | memory | network | manual
- source_ref: {path or command id}
- content_hash: {sha256 of artifact if file, else n/a}
- artifact_path: {relative path under case root when content_hash is recorded, else n/a}
- repro_command: |
    {exact command}
- raw_excerpt: |
    {redacted excerpt}
- linked_workitem: WI-{nnn} | n/a
- supersedes: E-{nnn} | none
```

**MUST**: a Finding references at least 1 Evidence; a third party can run `repro_command`, or it states the offline limitation.

**CLI helper** (writes `work/<case>/evidence/E-*.md`):

```powershell
powershell -File skills/scripts/append-evidence.ps1 -CaseRoot work/<case> `
  -Id E-001 -Title "..." -ReproCommand "..." -Severity info -Status observed
```

When the evidence is a case-local file, pass `-ArtifactPath` to record a SHA-256 fixity value and a relative artifact path. Review the complete case graph before handoff:

```bash
python3 skills/case-review/scripts/review_case.py work/<case> --verify-hashes --strict
```

The review is read-only and checks scope fields, Evidence records, work item and timeline references, structured Findings, Paths, and artifact hash matches.

## 2. Finding (security/reverse engineering conclusion)

```markdown
### F-{nnn}
- title:
- severity: critical | high | medium | low | info | n/a_re
- category: vuln | misconfig | design | reverse_algo | bypass | other
- status: candidate | validated | false_positive | accepted_risk
- evidence_ids: [E-001, E-002]
- location: {file:line | addr | url | class.method}
- impact:
- confidence: high | medium | low
- repro_steps:
  1.
  2.
- remediation: {or n/a for pure RE}
- optional_attack: {ATT&CK ID or empty}
```

**MUST**: `evidence_ids` is not empty; when `status=validated`, confidence must not be low (unless residual risk is noted).

## 3. Path (attack path / call path / solution path)

Uniformly called **Path**, interpreted by task type:

| Task | Path meaning |
|------|-----------|
| Pentest / attack chain | Attack path steps |
| Reverse engineering | Key call/data flow steps |
| CTF | Solution steps |

```markdown
### P-{nnn}
- title:
- path_type: attack | callflow | solve
- start:
- goal:
- steps:
  1. action: — evidence: E-xxx — finding: F-xxx | none
  2. action: — evidence: E-xxx — finding: F-yyy | none
- residual_risks:
```

**MUST**: every step can link to Evidence; if the Finding at the end of an attack path claims "access/data obtained", it must have validated evidence.

## 4. Placement in the report

A `docs-generator` security report **MUST** contain:

1. Scope summary (linked to the case `scope.md`)  
2. Evidence table or section  
3. Findings list (with evidence_ids)  
4. At least 1 Path (attack/call/solution)  
5. Timeline summary (optionally link the full text to `timeline.md`)

See the **Evidence Chain** section in `docs-generator/references/security-report-templates.md`.

## 5. field-journal hook

When writing back to the journal, **SHOULD** excerpt:

- Up to 3 key Evidence ids + commands  
- 1 core Finding  
- One sentence on the reusable Path pattern  

Complete sensitive content stays only in the user's project report; the journal **MUST** be redacted (`anonymization.md`).

## 6. Differences from Z3r0 (distinctive features)

| Z3r0 | reverse-skill |
|------|----------------|
| PG immutable rows + API | Markdown files + hash field |
| UI review queue | Report + next-step menu + journal |
| Deep ATT&CK binding | Optional tags, no UI required |


## Validated sufficiency (Issue #77 / R4*)

Global bind rule remains: every Finding references **>=1** Evidence.

Promotion to status=validated is stricter (decision cookbook):

| status | Evidence bar |
|--------|----------------|
| preliminary / candidate | >=1 (unchanged) |
| **validated** | **SHOULD >=2 independent** Evidence (best: 1 static + 1 dynamic). A single Evidence item alone MUST NOT silently promote to validated; keep candidate/preliminary, or record residual_risk + human confirm. |
| blocked promotion | record Evidence E-insufficient-evidence |

Full recipes: [analysis-decision-framework.md](analysis-decision-framework.md) (R4*, R1, R41, R44).
