# Skill: Pull Request Review (Review Pull Request)

## Purpose
Review a GitHub pull request end-to-end using the GitHub CLI (`gh`). Covers diff analysis, commit history review, CI/CD check verification, severity-leveled feedback (Blocking, Suggestion, Nit, Praise), and `gh pr review` submission.

## Installation & Usage Options

### Via LobeHub Market CLI
```bash
# Register agent if not already registered
npx -y @lobehub/market-cli register --name "Antigravity" --source antigravity

# Install to custom skills directory
npx -y @lobehub/market-cli skills install pjt222-development-guides-review-pull-request --dir skills

# Install globally or for specific agent platform
npx -y @lobehub/market-cli skills install pjt222-development-guides-review-pull-request --agent open-claw
```

### Native Orchestrator Loading
```markdown
# IDE Native syntax
#[[file:skills/review-pull-request.md]]

# CLI reference
cat skills/review-pull-request.md
```

## When to Use
- A pull request is assigned for review or ready for inspection
- Performing a self-review before requesting others' input
- Conducting a second review after PR feedback has been addressed
- Auditing a merged PR for post-merge quality assessment
- Differentiating diff-scoped PR review from system-level architecture review

## Inputs
- **Required**: PR identifier (`<number>`, URL, or `owner/repo#number`)
- **Optional**: Review focus (`security`, `performance`, `correctness`, `style`, `architecture`)
- **Optional**: Codebase familiarity level (`familiar`, `somewhat`, `unfamiliar`)
- **Optional**: Time budget for the review (`quick scan`, `standard`, `thorough`)

## Tools & Prerequisites
- GitHub CLI (`gh`) authenticated with repository read/write access (`gh auth status`)
- Git CLI (`git log`, `git diff`, `git checkout`)
- Local linter and test runner when local verification is required

## Step-by-Step Procedure

### Step 1: Understand the Context & Scope
1. Fetch PR metadata:
   ```bash
   gh pr view <number> --json title,body,author,baseRefName,headRefName,labels,additions,deletions,changedFiles,reviewDecision
   ```
2. Read PR title and description:
   - What specific problem does this PR solve?
   - What architectural approach was taken?
   - Are there explicit focus areas requested by the author?
3. Assess PR size and determine review depth:

| Size | Files | Lines | Recommended Review Approach |
|------|-------|-------|-----------------------------|
| **Small** | 1–5 | <100 | Read every line sequentially; fast turnaround |
| **Medium** | 5–15 | 100–500 | Focus on core logic and edge cases; skim boilerplate |
| **Large** | 15–30 | 500–1000 | Review commit-by-commit; prioritize critical paths |
| **XL** | 30+ | 1000+ | Flag for potential decomposition; review security/data boundaries |

4. Review commit history and narrative coherence:
   ```bash
   gh pr view <number> --json commits --jq '.commits[].messageHeadline'
   ```
5. Check CI/CD pipeline and automated test checks:
   ```bash
   gh pr checks <number>
   ```

### Step 2: Systematic Diff Analysis
1. Retrieve full diff or patch:
   ```bash
   gh pr diff <number>
   ```
2. For large PRs, inspect commit by commit:
   ```bash
   gh pr diff <number> --patch
   ```
3. Evaluate each modified file across seven quality dimensions:
   - **Correctness**: Does the code accurately satisfy the PR description?
   - **Edge Cases**: Are nulls, empty states, boundary values, and race conditions handled?
   - **Error Handling**: Are errors caught gracefully without leaking stack traces or silent failures?
   - **Security**: Any injection risks, insecure deserialization, auth bypass, or secret leakage?
   - **Performance**: Any accidental $O(N^2)$ loops, unbounded in-memory allocations, or N+1 query patterns?
   - **Naming & Readability**: Are variables, functions, and modules descriptively named?
   - **Test Coverage**: Are new behaviors backed by regression or unit tests?

### Step 3: Classify Feedback by Severity
Group all review comments into strict severity tiers:

```
🔴 [BLOCKING]
- Critical bugs, data loss risks, severe performance regressions, security vulnerabilities.
- Must be resolved before PR approval and merge.

🟡 [SUGGESTION]
- Maintainability improvements, architectural refactoring, cleaner abstractions.
- Highly recommended, but author has discretion if trade-offs warrant.

🟢 [NIT]
- Minor polish, typos in comments, formatting, cosmetic naming adjustments.
- Non-blocking; author may address or defer.

🟣 [PRAISE]
- Highlighting elegant algorithms, thorough test suites, or exceptionally clean refactors.
```

### Step 4: Construct & Submit Structured Review
1. Format review comments with precise file path, line number, rationale, and diff replacement blocks:
   ```markdown
   **[BLOCKING]** Potential Null Pointer Exception
   In `src/services/auth.ts` at line 42:
   If `user.session` is undefined, accessing `user.session.token` will throw a TypeError.

   ```suggestion
   const token = user.session?.token;
   if (!token) {
     throw new UnauthorizedError('Missing session token');
   }
   ```
   ```
2. Submit the review using `gh pr review`:
   ```bash
   # Approve PR
   gh pr review <number> --approve -b "LGTM. Verified CI checks and test coverage."

   # Request changes with blocking findings
   gh pr review <number> --request-changes -b "Found 2 blocking issues regarding auth token validation and error handling. See inline comments."

   # Submit general comments/suggestions
   gh pr review <number> --comment -b "Review completed with minor suggestions."
   ```

## Review Anti-Patterns to Avoid
- ❌ **Rubber-Stamping**: Approving without reading diffs or verifying CI checks.
- ❌ **Nit Avalanche**: Flooding the review with 20+ trivial styling nits while missing logic bugs.
- ❌ **Scope Creep**: Demanding unrelated refactors outside the PR's stated objective.
- ❌ **Vague Criticism**: Saying "this looks slow" without explaining why or proposing an alternative.
