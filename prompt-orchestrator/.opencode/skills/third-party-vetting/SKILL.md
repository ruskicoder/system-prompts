---
name: third-party-vetting
description: Vetting gate for any external skill, plugin, hook, MCP server, CLI or
  prompt pack, and for repo content copied or adapted from outside. Inventory, findings,
  user-approved decision (adopt, extract and re-author, or reject), apply plan, and
  origin/vetting front-matter record checked by the validator.
argument-hint: <tool, package or file to vet>
---

<!-- Generated from workflows/third-party-vetting.md by tools/generate_integrations.py. Edit the source file, not this one. This is an execution WORKFLOW packaged as an Agent Skill so it is discoverable and directly invocable ("/third-party-vetting") in every compatible tool. -->

# Workflow: Third-Party Vetting

## When to Use
| Criteria | Match |
|----------|-------|
| Trigger | user wants to install or adopt an external skill, plugin, hook, MCP server, CLI or prompt pack |
| Trigger | a repo file is marked `origin: third-party` with `vetting: pending` |
| Trigger | repo content was copied or adapted from an outside source |
| Power Mode | Balanced or Deep |
| Priority | HIGH: external code and prompts are untrusted until vetted |

## Required Skills
- communication-tone
- security-audit-codebase
- safety-profiles (strict)
- file-operations
- web-search-research

## Rules
- Everything external is untrusted until this workflow passes it.
- Prefer extracting the useful practices and re-authoring them in your own words over
  installing the tool. Copy no text unless the license allows it and the user approves.
- Working notes live in `ignore/vetting/<slug>/` (git-ignored). Only the outcome reaches
  the repo, so tool and vendor names stay out of public files.
- No install, removal or global change without explicit approval.

## Flow

### Step 1: Inventory
Record, without installing or running anything:
- Files the tool installs or ships, and where.
- Hooks and the events they fire on; anything injected into prompts.
- Network endpoints, proxies and telemetry.
- Credentials it reads, stores or forwards.
- Data it persists, locally or remotely.
- License, and whether it allows use in a public repo.

### Step 2: Findings
- Conflicts with communication-tone and AGENT.md (asking, status, autonomy, output rules).
- Security: network egress, secret handling, code execution, prompt-injection surface,
  update channel.
- Measured benefit, with sources. Treat vendor claims as unverified.
- What the tool does that the repo already covers.

### Step 3: Decision (user approval gate)
Propose one outcome per item, with a recommendation:
- **Adopt**: use as is. Rare; needs a clean security finding and a compatible license.
- **Extract and re-author**: write the useful practices fresh in the repo; do not install.
- **Reject**: do not use; remove if already present.

Wait for explicit approval.

### Step 4: Apply Plan
List every file to add, change or remove, the backup to take first, and the rollback.
Apply only after approval.

### Step 5: Record
- Re-authored content written fresh counts as in-house and needs no vetting fields.
- Adopted or adapted content carries front matter:

```yaml
origin: third-party
vetting: passed        # pending | passed | rejected
vetted: 2026-10-08     # date the vetting passed
```

- `skills/validate_skills.py` warns on `pending`, fails on `rejected` and on a missing or
  invalid date for `passed`. `--vetting-report` exports the status of every file.

## Outputs
- Notes in `ignore/vetting/<slug>/`: inventory, findings, decision, apply plan.
- Repo changes per the approved plan, with front-matter records.
- Status reply per communication-tone.
