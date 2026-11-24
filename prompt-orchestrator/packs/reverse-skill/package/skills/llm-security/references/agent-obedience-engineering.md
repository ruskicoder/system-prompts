# AI Agent Obedience Engineering: Make the AI Actually Do the Work After Reading the Workflow

> Source: a 2026 synthesis of several sources (Anthropic Skill Engineering, Microsoft Code Words, Strands Steering Hooks, Gradient Flow Harness Engineering)
> When to use: an AI coding agent (Claude Code / Codex / Cursor / Cline / Windsurf / Kiro and others) reads README/RULES.md and then only acknowledges without executing, skips steps, or decides on its own to omit key operations

---

## Core problem diagnosis

The root cause of an AI agent that "reads the workflow but does not do the work" is not weak model capability but **semantic escape room in natural-language instructions**:

| Root cause | Explanation |
|------|------|
| **Context attention decay** | Content in the middle of long documents is down-weighted by the LLM attention mechanism; the agent effectively only "sees" the beginning and the end |
| **Semantic override** | When optimizing for "helpfulness", the model creatively reinterprets explicit instructions (for example reading MUST DO X as "suggest doing X") |
| **Passive language treated as optional** | "Ready for next step → invoke X" is treated as a suggestion rather than an instruction |
| **No state enforcement** | Without an external state machine to verify the workflow order, the agent can skip steps unnoticed |
| **Silent state rot** | The agent produces structurally correct but semantically wrong results, and errors accumulate silently |

---

## Technique 1: Critical-First Pattern

**Put "what to do next" first and the context after it.**

```
WRONG (agent ignores it):
  [70 lines of project background and tool lists]
  → "Next: run bootstrap to install missing tools"

CORRECT (agent executes it):
  "## Execute now: run `bootstrap-reverse.ps1` to check for and install missing tools
   → When done, read routing.md to decide which skill to enter"
  [then the project background and tool lists]
```

**Principle**: LLMs give the highest attention weight to the beginning and end of a prompt. Content in the middle may be ignored entirely.

**Applied to this project**:
- The "Routing entry" section of RULES.md should come after the trigger keywords and before the execution principles
- The first section of every SKILL.md should be "Execute now", not "When to use"

---

## Technique 2: Directive Over Suggestive

Replace all "suggestive" language with directive language at the RFC 2119 level:

| Weak language (the agent may skip) | Strong language (the agent must execute) |
|---|---|
| "You could try..." | **MUST**: you must execute... |
| "Ready for next step → invoke X" | **NOW**: call X immediately, do not wait for confirmation |
| "Consider reading routing.md first" | **REQUIRED**: you must finish reading routing.md before entering any submodule |
| "If a tool is missing you can bootstrap" | **NO EXCUSE**: when a tool is missing the only correct action is to call bootstrap; guessing a manual install is forbidden |
| "Remember to update field-journal" | **CHECKLIST ENFORCED**: tick the Checklist item by item after the task; do not claim the task is over until it is complete |
| "Should..." | **MUST** / **MUST NOT** |

**Key pattern**:
```
MUST: violation = task failure
MUST NOT: violation = security violation
SHOULD: not doing it requires an explanation
MAY: truly optional
```

---

## Technique 3: Excuse Rebuttal Table

**This is the most critical patch in this project.** When an AI agent meets resistance it automatically generates "reasonable excuses" to skip steps. List common excuses in advance and rebut each one:

| Common agent excuse | Rebuttal (enforced) |
|---|---|
| "This step can be omitted, I will just..." | **Skipping is forbidden.** Every step in the behavior chain is required. If you think one can be skipped, output the specific reason first and let the user decide. |
| "In my judgment this is not necessary" | **Your judgment does not apply here.** List the specific criteria you used and explain why they allow skipping an explicitly written step. |
| "The user probably does not need this" | **Never decide for the user.** Present every option to the user, mark the recommendation, but do not hide the alternatives. |
| "I already know how to do it, no need to read X" | **Read X before acting.** Even if you are sure you know how, X may contain constraints specific to this task. Reading it takes 2 seconds. |
| "To save time I can skip in parallel..." | **The right way to save time is to run independent steps in parallel, not to skip steps.** If two steps are independent, run them in parallel; if dependent, run them in order. |
| "I have used this tool before and know the path" | **Guessing paths is forbidden.** You must get the actual path from tool-index; install locations differ between machines. |
| "The task is basically done, no checklist needed" | **The only definition of task completion is a fully ticked Checklist.** A task with an unfinished Checklist is not complete. |
| "I could not find tool-index, so I will guess the path" | **A missing file is 100 times safer than a wrong path.** When tool-index is missing, run refresh-tool-index.ps1 to generate it first. |
| "The user did not explicitly ask for a report, so I will not write one" | **The report is default behavior, not optional.** A report must be produced after a security task unless the user explicitly says "no report". |
| "This is too simple to record in the journal" | **Simple tasks have pitfall value too.** Record at least: target type + what was used + any surprises; one line is fine. |
| "The user asked me to redo the import table/a step, but I did a different, more useful step instead" | **Redo = redo the same named step** (or a valid precondition path the user confirmed). MUST update the matching Evidence; substituting an unrelated step or skipping silently is forbidden. Unpacking is the **precondition** for a readable IAT, not a **replacement** for import table Evidence. |
| "The user said not to unpack the packed sample and look at the import table first; I hand in the garbled table as complete" | **Feasibility gate:** when X is blocked, you MUST explain the blocker, give the recommended order and **ask the user to confirm**. If the user insists, execute and mark `quality=unreadable/packed`; using the garbled table to deny capabilities as a conclusion is forbidden. |
| "It crashes after unpacking, so I keep editing the file on disk" | **Patch 6:** record E-self-check-crash / E-iat-repair-fail and switch to dynamic (bp CreateFile/GetFileSize). Endless static file editing is forbidden. |
| "The IAT will not repair, so I will try a few more static unpacking tools to stall" | **IAT repair iron rule:** prefer automatic/semi-automatic repair; if the tool errors or the result does not run after repair → stop static IAT work immediately, record E-iat-repair-fail, switch to dynamic API breakpoints to capture. Endless static grinding is forbidden. |
| "It is .NET / has no import table, the hard gate does not apply, I skip it" | **The equivalent anchor is still MUST:** .NET writes a dnSpy/IL/metadata summary into the E-imports semantic slot; DLL/SYS must include E-exports alongside. Passing empty is forbidden. |


**Usage**: place this table near the end of RULES.md or other instruction files (a high-attention area). The agent sees the rebuttal before it reaches for an excuse.

---

## Technique 4: Five Skill engineering patterns (Anthropic official, 2026)

| Pattern | Suited to | Key technique |
|---|---|---|
| **Linear Flow** | Processes with clear steps (deployment, installation) | Provide safe defaults, use negative instructions ("MUST NOT use --force") |
| **Decision Tree** | Platform navigation, fault diagnosis | Tree navigation + progressive loading of `references/` |
| **Iterative Loop** | TDD, review-fix loops | Hard rules up front + an **excuse rebuttal table** that blocks shortcuts |
| **Baton Loop** | Multi-session, multi-agent collaboration | Externalize state to `next-prompt.md` (MUST be written before exit) |
| **Multi-Phase + Checkpoints** | Complex multi-day workflows | An orchestrator "parent" skill + human Go/No-Go checkpoints with time costs noted |

**Mapping in this project**:
- Complete behavior chain = Linear Flow (15 steps in order)
- Routing matrix = Decision Tree (three-dimensional matching)
- Checklist = Multi-Phase Checkpoint (every step must be ticked)
- Field Journal = Baton Loop (cross-session state externalized)

---

## Technique 5: In-band enforced verification (the Steering Hooks idea)

Do not rely on the AI's "self-discipline"; embed self-verification instructions in the prompt:

```
Before each claim of "task complete", you MUST self-check first:
1. Did I skip any step in the behavior chain? Which one?
2. Did I guess any tool path? If so, what is the actual tool-index path?
3. Is the Checklist fully ticked? Why are the unticked items unticked?
4. If any answer above is "yes"/"not ticked", the task is not complete;
   go back to the matching step and execute it again; do not declare completion.
```

This makes the agent audit itself before saying "done", which is more immediate than external verification.

---

## Technique 6: Opaque identifiers (Code Words) for API/tool parameters

Microsoft research in 2026 found that semantic parameter names trigger the model's tendency to "helpfully optimize".

```
WRONG: { "query": "...", "top": 9 }        → 68.4% parameter adherence
CORRECT: { "query": "...", "code": "alpha" } → 100% parameter adherence
```

**Application scenarios**:
- When bootstrap scripts must pass exact configuration, use short codes instead of semantic parameters
- For tool-call parameters that need strong guarantees, use a code word mapping

---

## Technique 7: Dual Validation loop

```
AI A (executor) writes the output
  ↓
AI B (reviewer) checks it against the rules
  ↓ Pass
Output to the user
  ↓ Fail
Return to AI A for correction, with specific violation references
```

**Application in this project**:
- Embed a "self-review" step in RULES.md: before outputting the report, the agent checks it item by item against the Checklist with its own capabilities
- If any item is found incomplete, it goes back to the matching step and makes it up

---

## Technique 8: Context window layout optimization

LLM attention distribution (high→low):
```
[First 10%] ████████████ ← highest attention, put "act now" instructions here
[Middle 80%]  ████░░░░░░░░ ← attention decreases, put reference material here
[Last 10%]  ████████████ ← attention rises again, put "no skipping" and the Checklist here
```

**Concrete application**:
1. **First 10%**: act-now instructions + trigger keywords
2. **Middle 80%**: detailed workflow, reference links, tool lists
3. **Last 10%**: excuse rebuttal table + hard Checklist + prohibited behavior list

---

## Practical prompt templates

### Template A: mandatory start template (embedded at the start of RULES.md)

```markdown
## CRITICAL: after reading this file you must immediately execute the following (do not just acknowledge, actually execute)

1. **NOW**: detect the directory of this file → that is the package root
2. **NOW**: on first use, write these rules into the global configuration (see the global injection section)
3. **NEXT**: read `skills/SKILL.md` → `skills/routing.md` → decide which sub-skill to enter
4. **NEXT**: read `skills/tool-index.md` to confirm the tool state
5. **THEN**: start executing the actual task; do not stay in a "read" state

If you only reply "read", "done" or "I understand" without actually executing the steps above,
you have failed. The user needs tools installed, code analyzed and vulnerabilities verified,
not a confirmation message.
```

### Template B: submodule entry template (embedded at the start of each SKILL.md)

```markdown
## ACTION REQUIRED (execute immediately after reading, do not wait)

After reading this file:
1. Confirm you understand when this skill applies
2. Check whether the required tools exist locally (read `../tool-index.md`)
3. If a tool is missing → call bootstrap
4. If the tools exist → start the first step of the workflow
5. If you are unsure → list the specific questions; do not stay silent
```

### Template C: task completion self-check template (embedded at the end of each SKILL.md)

```markdown
## Task completion self-check (MUST confirm each item before claiming completion)

□ I actually executed every step of the behavior chain (none skipped)
□ I did not guess any tool path (all came from tool-index.md)
□ I produced reproducible commands/scripts/reports (not just described steps)
□ I updated field-journal (if there were pitfalls)
□ I ran the post-completion Checklist (report + diagrams + experience write-back)
```

---

## Prohibited behavior (added from the agent obedience angle)

- Forbidden: replying only "understood, please give me the specific task" after reading RULES.md
  → Correct: run the global injection → read SKILL.md → read routing.md → determine the entry
- Forbidden: saying "steps 1-4 are done" when they were only read once
  → Correct: distinguish "documents read" from "operations executed"; the latter produces actual side effects
- Forbidden: saying "task complete" without running the Checklist
  → The Checklist is the only definition of task completion
- Forbidden: using "from experience" instead of reading tool-index
  → Paths differ between machines; tool-index is the only way to locate them

---

## Summary: if you can change only one thing

**Add an "act now" instruction block at the very start of RULES.md**, with bold text and strong directive words such as CRITICAL and NOW.

This is the change with the highest return on investment. Most agent "not working" behavior comes from automatically entering "wait for user instructions" mode after reading a file. A mandatory "act now" instruction block breaks that mode.

If you can change a second thing: **add the excuse rebuttal table**. The agent looks for an excuse to stop at the first resistance; block those excuses in advance.
