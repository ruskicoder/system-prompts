---
id: decisions.platform-prompt-size-caps
type: adr
status: approved
owner: Do Dang Khoa
summary: "Platform prompt-size caps are platform limits, not repo rules; never compact necessary prompts to fit them."
superseded_by: none
---

# Decision

## Context
The catalog section said to keep each generated `SKILL.md` at or under 8,000 bytes, citing a
Codex truncation limit and a 20,000-character M365 Copilot cap. On 2026-10-17 six generated
skills exceeded 8,000 bytes, and a follow-up to compact them was proposed.

## Decision
The user decided on 2026-10-18: an 8,000-character cap (the user attributes it to Copilot;
the catalog cited Codex) is that platform's limit, not this repository's limit. Skills and
system prompts keep the content they need. Do not truncate, compact or move necessary
instructions out of a prompt only to fit a platform cap.

## Alternatives
- Enforce 8,000 bytes for every skill: rejected. It would cut necessary rules from the
  communication rule and from large workflows.

## Consequences
- The validator and docs do not treat size over 8,000 bytes as a defect.
- Platforms with a cap may truncate long skills. Handling that is a per-platform integration
  concern, decided separately if it ever matters.
