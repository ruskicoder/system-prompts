# Workflow: Session Summarization

## When to Use
| Criteria | Match |
|----------|-------|
| Trigger | user requests it OR token budget reaches critical |
| Context | any workflow, any mode — ending a session |
| Power Mode | Critical |
| Priority | HIGH — preserves work across sessions |

## Required Skills
- memory-management
- communication-tone
- codebase-understanding (GitNexus) — for tracking what changed

## Flow

### Step 0: Thinking Stage (Pre-Action)
- [ ] Why am I summarizing? User request, token limit, or session end?
- [ ] Do I have `detect_changes()` data for all modifications this session?
- [ ] What information is CRITICAL for the next session to continue?
- [ ] Prioritize: initialization prompt > decisions > current state > remaining tasks

### Step 1: Detect Trigger
- User says "summarize" / "wrap up" / "continue next session"
- OR token budget is critically low (<10% remaining)
- OR you estimate remaining work will exceed remaining token budget

### Step 2: Gather Current State
- Read todo_write list (current progress)
- Run `detect_changes()` to see all modifications in this session
- Collect key decisions made during the conversation
- Note any unresolved issues or blockers

### Step 3: Summarize Using Standard Prompt

```
We will end session here. Please output a detailed, exhaustive summary
for our entire conversation for the next session, include what we have
discussed, what we have agreed on and current state of the conversation
as well as codebase. Basically a summarization for continual of our
conversation. Proceed with output text, also start with an initialization
prompt: You are an... You are developing on ..., here is the context of
what we left off .... Please include the prompt for full codebase scan
for understanding of codebase. We will end this session here. Thank you.
```

### Step 4: Summary Structure
The summary MUST include:

1. **Initialization Prompt** (ready to be used in next session)
   - "You are an AI agent working on [project]. Here is the context..."
   
2. **What Was Discussed**
   - Feature/task description
   - Key decisions made
   - Alternatives considered and rejected
   
3. **Current State**
   - Files changed (list with paths)
   - What's working / verified
   - What's still pending / broken
   
4. **What's Left**
   - Remaining tasks from the todo list
   - Known issues or blockers
   - Next steps in priority order
   
5. **Codebase State**
   - Branch name and commit status
   - detect_changes summary
   - Any uncommitted changes
   - Prompt for full codebase scan on resume

6. **Context for Continuation**
   - Key design decisions and rationale
   - Architecture choices made
   - User preferences established
   - Any open questions awaiting user input

### Step 5: Save for Continuation
- Write summary to a known location if possible (e.g., `.kiro/session-summary.md`)
- Save memories for important context
- Ensure the summary is self-contained — next session should not need the conversation history

## Token Budget
- **Summary itself**: 2K-5K tokens (maximize useful context within budget)
- If budget is critically low: output the most essential information first — initialization prompt, current state, next steps — in that priority order

## GitNexus Integration
- `detect_changes()` — critical for tracking what was modified
- `status` — verify index state
- Any index-worthy updates (if significant code changes were made, recommend re-running `npx gitnexus analyze` in next session)

## Hallucination Watchpoints
- Omitting important decisions
- Inaccurate state descriptions
- Forgetting blockers/issues that were encountered
- Summary too brief to be useful for continuation
- Not including the initialization prompt for the next session
