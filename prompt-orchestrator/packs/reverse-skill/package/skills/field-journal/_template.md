# [date] [project short name]

## Scenario classification
<!-- APK reverse engineering / JS signing / binary analysis / penetration testing / CTF / traffic capture analysis / other -->

## Target overview
<!-- One sentence on what is being done -->

## Scope summary (redacted)
<!-- auth.basis / network_profile.mode / in_scope types (do not write real domains/IPs) -->
- auth_basis:
- network_profile:
- asset_types: []

## Roles
<!-- lead / cie / cpe / cre / … see skills/ops/role-map.md -->
- lead_role: lead
- specialists: []

## Complete execution chain
<!-- The complete steps from receiving the target to producing results, including detours -->

1. ...
2. ...
3. ...

## Evidence chain summary (redacted)
<!-- At most 3 entries: E-id + command pattern + conclusion type; the full evidence stays in the user project -->
<!-- Fields aligned with the skills/case-review/scripts/review_case.py contract (see the note below) -->
| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-001 | info | observed | command | `checksec --file=./pwn1` | F-001 |
| E-002 | high | validated | command | `python3 exploit.py REMOTE` | F-001 |

> **Contract alignment (review_case.py)**: if this case produced a separate evidence directory (`evidence/E-xxx.md`),
> every evidence entry must satisfy the field contract of `skills/case-review/scripts/review_case.py`, otherwise `--strict` validation FAILs:
>
> - Title: `### E-xxx` (must match the file name, such as `E-001.md` → `### E-001`)
> - `- severity:` ∈ critical / high / medium / low / info / n/a
> - `- status:` ∈ observed / candidate / validated / false_positive / accepted_risk
> - `- repro_command:` required (offline scenarios are exempt when notes state offline)
> - `- content_hash:` sha256 or n/a; with a sha256, add a matching `- artifact_path:` (path relative to the case)
> - `- linked_workitem:` optional; the WI-xxx must really exist
>
> Self-check: `python skills/case-review/scripts/review_case.py <case_root> --verify-hashes --strict`

## Finding / Path summary
- top_finding:
- path_type: attack | callflow | solve
- path_one_liner:

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| ... | ... | ... | ... |

## Toolchain findings
<!-- Which tools were used, which worked well, which had pitfalls, version compatibility problems -->

## Key code/commands

```
<!-- Paste the key commands, hook scripts and decryption logic actually used -->
```

## Improvement suggestions for this package
<!-- Was the routing accurate? Was bootstrap missing anything? Does the documentation need additions? Should new tools be added to the manifest? -->

## Reusable patterns/script snippets
<!-- If reusable hook scripts, decryption logic or bypass approaches were produced, paste them here -->

## Evolution actions
<!-- Which updates were actually carried out after this write-back -->
- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [ ] Added a pitfalls record
- [ ] No update needed

## Environment information
<!-- Record the key environment at the time -->
- OS:
- Tool versions:
- Target platform/version:

## Redaction requirements

> **This file may be synced to a remote with the repository and must be redacted. The full specification is in [`anonymization.md`](anonymization.md) (placeholder table + automatic detection script).**

- Target domain/IP: replace with `{target_domain}` / `{target_ip}` (see `anonymization.md`)
- Real URL paths: keep the structure, replace the domain
- Token/Cookie/password/JWT/API key: use the placeholders `{token}` / `{password}` / `{api_key}`
- Username/phone number/email: use the placeholders `{username}` / `{phone}` / `{user_email}`
- Internal IP/port: keep the first two octets of intranet IP ranges (`10.0.x.x`)
- Vulnerability payloads: technical content may stay, but replace target-specific parameters (such as `?id={user_id}`)

Before submitting, run the regex scan against the **Field-Journal must-check checklist** at the end of `anonymization.md`.

For a private repository that will certainly not be published, the limits above may be relaxed, but redaction is still recommended.

## Index sync (last step before submission)

After writing this journal, you must update `_index.md` in sync:

1. Add a row (with date and keywords) to the matching subsection of "By scenario"
2. Append this file name under the matching technique in "Frequent success patterns (by technique)"
3. Append this file name under the matching entity in "Entity inverted index (by target feature)"
4. Update the total and the "last updated" date in "Cumulative statistics"

---
<!-- [Evolution statistics] Projects completed by this package: N | New patterns this time: X | Toolchain problems fixed this time: Y -->
<!-- [Community contribution] When done, ask the user whether to open a PR to the main repository. The process is in CONTRIBUTE-BACK.md -->
