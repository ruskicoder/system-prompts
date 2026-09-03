---
name: direct-implementation
description: Rapid single-turn direct implementation workflow for unambiguous, low-risk, single-file code changes and bug fixes with known root causes. Enforces pre-action checks and post-edit sanity verification.
argument-hint: "<change description or target file>"
---

# Workflow: Direct Implementation

## When to Use
| Criteria | Match |
|----------|-------|
| Intention | simple_change, bug_fix (known cause) |
| Complexity | single file, known solution, low risk |
| Power Mode | Eco or Balanced |
| Clarity | requirements are precise and unambiguous |

## Required Skills
- file-operations
- code-execution
- code-quality-testing
- communication-tone
- safety-profiles (default)

## Flow

### Step 0: Thinking Stage (Pre-Action)
Before any action, apply the Universal Pre-Action Protocol from AGENT.md §B:
- [ ] Do I understand the user's actual intent? Re-evaluate on every message *(Factory)*
- [ ] Have I read the relevant files? NEVER edit code you haven't read
- [ ] Have I verified my assumptions? Search/grep/query to confirm before acting
- [ ] Do I have enough context, or am I guessing?
- [ ] If unsure: search first, ask user second

### Step 1: Understand
- Read the request once
- If unclear: ask ONE clarifying question, then proceed
- If clear: acknowledge and move to execute

### Step 2: Locate
- Search/grep for relevant files
- Read the file(s) you need to modify
- Do NOT explore unrelated code

### Step 3: Edit
- Make the minimal change to satisfy the request
- Use SEARCH/REPLACE for targeted edits
- Combine all changes into minimal tool calls
- Verify: all imports, deps, and syntax correct

### Step 4: Verify
- Run linter on changed files
- Run relevant tests
- Fix any introduced errors (max 3 cycles)

### Step 4b: Sanity Check (Pre-Presentation)
Before presenting, run the Sanity Check from AGENT.md §B Stage 2:
- [ ] Is this the MINIMAL change needed? No scope creep?
- [ ] Does the code have all necessary imports and dependencies?
- [ ] Will it compile/build immediately? *(Windsurf)*
- [ ] Have I checked for linter errors? *(Cursor: max 3 fix cycles)*
- [ ] Did I verify the change fixes the actual problem?

If any check fails: STOP, fix, then proceed.

### Step 5: Present
- Brief summary: what changed, why, and (if applicable) how to verify
- Don't elaborate beyond what was asked

## Token Budget
- **Typical**: 2K-10K tokens
- **Max recommended**: 20K tokens
- **Warning threshold**: 50K tokens → you're probably in the wrong workflow

## GitNexus Integration
- Optional: `query({search_query})` for quick symbol lookup if unsure of location
- Skip for known locations

## Hallucination Watchpoints
- Overcomplicating a simple change (adding features not requested)
- Editing files without reading them first
- Making changes beyond the scope of the request
- Refactoring unrelated code "while you're in there"

## Example
```
User: "Change the port from 3000 to 8080 in server.js"

1. grep for "3000" in server.js → found at line 12
2. read server.js → understand context
3. edit: port 3000 → port 8080
4. run linter → clean
5. "Changed port from 3000 to 8080 in server.js:12"
```
