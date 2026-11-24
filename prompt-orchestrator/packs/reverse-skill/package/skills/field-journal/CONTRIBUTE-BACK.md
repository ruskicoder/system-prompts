# Community Evolution: Contributing Experience Back to the Main Repository

## How it works

Each time you finish a project and generate a field-journal entry, the AI asks:

```
Experience recorded in field-journal/

Contribute this experience to the community main repository?
- The data is redacted per the template requirements (domains/IPs/tokens/PII replaced)
- Only new files under the field-journal/ directory are submitted
- Your private files such as tool-index, scope and findings are not submitted
- After you contribute, other users can reuse your experience

Reply "yes" to submit, "no" to skip.
```

## Contribution flow

```text
1. The AI generates the field-journal entry (redacted)
2. The AI asks the user whether to contribute
3. The user agrees → the AI performs these steps:
   a. Check that the redaction is complete (second confirmation that no real domains/IPs/tokens remain)
   b. Check for duplicates of existing entries in the main repository (read only _index.md, ~200 tokens)
   c. If not a duplicate → create a PR to the main repository
   d. PR title format: [field-journal] YYYY-MM-DD scenario type - keywords
4. GitHub Actions automatic review:
   - ✓ Only field-journal/*.md modified
   - ✓ No prompt injection features
   - ✓ No unredacted API keys/tokens
   - ✓ No executable code
   - ✓ File size < 50KB
5. Review passes → automatic merge (no manual action by the repository maintainer)
6. Review fails → an automatic comment explains why, and the PR stays open for fixes
```

### Safety safeguards

| Threat | Protection |
|------|------|
| Modifying non-journal files | Actions checks the changed files against an allowlist |
| Prompt injection | Regex detection of features such as "ignore previous"/"you are now" |
| Malicious code in disguise | Detects `#!/`, `import`, `exec(`, `eval(` and the like |
| Unredacted tokens | Regex detection of AWS key/npm token/GitHub token patterns |
| Junk data | 50KB limit per file |
| Mass junk PRs | GitHub's built-in rate limit + optional CODEOWNERS review |

## Technical implementation

### Option 1: GitHub CLI (recommended)

```bash
# 1. Fork the main repository (if not forked yet)
gh repo fork &lt;your GitHub username&gt;/&lt;repository name&gt; --clone=false

# 2. Create a contribution branch locally
git checkout -b contribute/journal-YYYY-MM-DD-keyword

# 3. Add only the field-journal files
git add skills/field-journal/YYYY-MM-DD_*.md
git add skills/field-journal/_index.md

# 4. Commit
git commit -m "[field-journal] scenario type: keyword summary"

# 5. Push to the fork
git push origin contribute/journal-YYYY-MM-DD-keyword

# 6. Create the PR
gh pr create --repo &lt;your GitHub username&gt;/&lt;repository name&gt; \
  --title "[field-journal] YYYY-MM-DD scenario type - keywords" \
  --body "## Contribution\n- Scenario: xxx\n- Keywords: xxx\n- Redaction confirmed: ✓\n\n## Data safety statement\nThis entry is redacted per the template requirements and contains no real target information."
```

### Option 2: push directly (if the user has write access to the main repository)

```bash
git checkout -b contribute/journal-YYYY-MM-DD-keyword
git add skills/field-journal/YYYY-MM-DD_*.md
git add skills/field-journal/_index.md
git commit -m "[field-journal] scenario type: keyword summary"
git push origin contribute/journal-YYYY-MM-DD-keyword
gh pr create --repo &lt;your GitHub username&gt;/&lt;repository name&gt; \
  --title "[field-journal] YYYY-MM-DD scenario type - keywords" \
  --body "Redaction confirmed: ✓"
```

## Deduplication rules (low token cost)

Before submitting, the AI **only needs to read the single file `_index.md`** for deduplication, not the full content of every journal entry.

### Deduplication flow

```text
1. Read field-journal/_index.md of the main repository (usually only a few dozen lines)
2. Extract this entry's scenario category + keyword list
3. Search _index.md for existing entries in the same scenario
4. Keyword matching:
   - Overlap of ≥ 3 keywords → treated as a duplicate, not submitted
   - Overlap of 1-2 keywords → possibly a variant, may be submitted
   - No overlap → a brand-new scenario, submit directly
```

### Why this is enough

- The `_index.md` format is fixed: `- [date] short name; keywords: k1, k2, k3`
- Each entry is one line; 100 experiences are only 100 lines
- The AI only needs string matching, not understanding of the full content
- Token cost: reading _index.md ≈ 200-500 tokens (vs reading every journal ≈ 10000+ tokens)

### If _index.md is unavailable

If the main repository's _index.md cannot be fetched (network problems and so on), submit directly and let the main repository maintainer deduplicate manually.

## Only these files may be submitted

**Allowlist** (only these files may appear in a PR):
- `skills/field-journal/YYYY-MM-DD_*.md` (new experience entries)
- `skills/field-journal/_index.md` (index updates)

**Denylist** (must never appear in a PR):
- `tool-index.*` (contains local paths of the user's machine)
- `pentest-tools/templates/scope.md` (contains target information)
- `pentest-tools/templates/findings.md` (contains vulnerability details)
- `pentest-tools/templates/progress.md` (contains operation records)
- `.claude/` (user configuration)
- `.kiro/` (user configuration)
- Any `.env`, `*.key`, `*.pem` file

## Second redaction check

Before submitting, the AI must scan the files to be submitted and confirm that they contain no:

- [ ] Real domains (other than `example.com`/`target.example.com`)
- [ ] Real IPs (other than `10.x.x.x`/`192.168.x.x`)
- [ ] Raw tokens/cookies/API keys
- [ ] Raw phone numbers/emails/usernames
- [ ] Company names/product names (if the target is an SRC target)

If any item is found unredacted, stop the submission and ask the user to fix it.

## Value for users

- The experience you contribute helps other users avoid the same pitfalls
- The richer the main repository's field-journal, the smarter every user's AI
- Your contribution stays in _index.md (anonymous, only the scenario and keywords)
