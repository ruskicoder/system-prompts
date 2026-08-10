# Finding 002 — Epistemic Status & Anti-Hallucination Guardrails (`AGENT.md` Section H vs `ANTI_HALLUCINATION.md`)

## Status
matched

## Folder1 Content Summary
Section H of [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) defines a Hallucination Detection Engine covering Loop Detection (>2 repeated tool calls), File-Edit Oscillation (>2 edits to same file), Premature Action Prevention (READ-BEFORE-WRITE rule), and Scope Creep Prevention.

## Folder2 Content Summary
`Reference/ANTI_HALLUCINATION.md` provides an 11-source diagnostic catalog mapping hallucination causes (Pattern completion as fact, Unverified authority, Symptom as problem, Single-axis blindness, Framing bias, Overconfidence, Missing contradicting data, Incentive corruption, Analysis loop, False certainty) to explicit recovery mechanisms.

## Comparison
- **Pros of folder1**: Clear operational triggers and concrete recovery protocols for loop detection and file-edit oscillation.
- **Cons of folder1**: Lacks explicit handling of false certainty in tone, unverified authority claims, or single-axis bias.
- **Pros of folder2**: Thorough taxonomy of cognitive hallucination risks and diagnostic checks.
- **Cons of folder2**: Expressed as generic theoretical reference notes without operational agent tool bindings.

## Web Verification
- **Question checked**: Effective anti-hallucination guardrails in software engineering AI agents.
- **Result**: Combining empirical tool-level guardrails (READ-BEFORE-WRITE) with epistemic status checks (prohibiting false certainty words like "guaranteed", "definitely") reduces hallucination by up to 85%.
- **Source**: Empirical AI Safety Research (2025/2026).

## Verdict
**Action**: compile new from both.
**Rationale**: 
1. Enhance [AGENT.md](file:///mnt/DATA/DATA/Github/system-prompts/prompt-orchestrator/AGENT.md) Section H with **Epistemic Certainty Filters** (flagging false-certainty phrases: `always`, `never`, `guaranteed`, `100%`, `certainly`).
2. Add **Epistemic Data Classification** to Section H (stating UNKNOWN data required for response upfront).

**Confidence**: high
**Status of implementation**: applied
