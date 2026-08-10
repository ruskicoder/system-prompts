# Finding 007 — Security, Safety & Governance Protocols (`skills/safety-profiles.md` vs `security/`, `governance/`)

## Status
matched

## Folder1 Content Summary
[skills/safety-profiles.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/skills/safety-profiles.md) is a 115-line skill specification detailing 3 safety levels (Default, Strict, Relaxed), safety selection logic, evenhandedness, and user wellbeing guidelines.

## Folder2 Content Summary
`openclaw-operator` enforces runtime security posture (`security/` policies):
- Fail-closed credential verification
- HMAC signature verification for webhooks
- Child agent environment isolation (isolated env allowlist instead of full parent env inherit)

## Comparison
- **Pros of folder1**: Deeply comprehensive LLM safety level classifications (Default, Strict, Relaxed) and evenhandedness rules.
- **Cons of folder1**: Focuses primarily on prompt-level safety; misses explicit rules for child environment isolation and fail-closed secret verification.
- **Pros of folder2**: Excellent runtime security enforcement (fail-closed secret handling, environment isolation).
- **Cons of folder2**: Tied to NestJS runtime implementation rather than prompt specifications.

## Web Verification
- **Question checked**: Best practice for LLM agent environment security and secret handling.
- **Result**: Subagent execution environments MUST run in isolated sub-environments with strict variable allowlists, failing closed if mandatory credentials are missing.
- **Source**: OWASP Top 10 for LLM Applications (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**: Incorporate folder2's runtime security principles into [skills/safety-profiles.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/skills/safety-profiles.md):
1. Add **Child Agent Environment Isolation** rules (allowlisted env variables only, prevent leak of parent secrets).
2. Add **Fail-Closed Secret Validation** rules.

**Confidence**: high
**Status of implementation**: applied
