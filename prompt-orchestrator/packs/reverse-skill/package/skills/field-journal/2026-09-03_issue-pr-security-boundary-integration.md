# 2026-09-03 Security Boundary Integration of Multiple Issues/PRs

## Scenario

Maintaining a public security skill routing repository: the local main working tree held many user changes and lagged behind the remote, while several open PRs needed review, historical issues needed resolution, features needed adding, a security re-review needed publishing, and the GitHub state and cross-platform CI needed to close the loop.

## Reusable patterns

1. **Dirty working tree isolation:** fetch the remote first, then create a separate worktree from `origin/main`; every PR merge, conflict resolution, test and commit happens in the isolated directory.
2. **Keep PR attribution:** merge each accepted PR head into the integration branch as a parent of a merge commit; after the final fast-forward push to main, GitHub automatically marks the corresponding PRs as merged/closed.
3. **State freeze:** record each PR's head SHA before merging; fetch again before pushing, require that remote main still equals the review baseline, and verify that every accepted PR head is an ancestor of the final HEAD.
4. **Review under AV quarantine:** for payload documents that Defender may quarantine, do not depend on working tree files; use `git show :path` / Git index blobs for hash, link and content boundary checks.
5. **Reference/executable layering:** passive Markdown/JSON payloads may stay, but executable scripts must not reference them; CI pins the corpus hash, the binary allowlist, symlinks, dangerous patterns and GitHub Action full SHAs.
6. **Do not merge feature PRs blindly:** besides running the original PR tests, check cross-instance state, path/port isolation and new mainline constraints. This time the IDA keepalive file was found not to be isolated by port, and the merge commit fixed it.
7. **Clear issues with grounds:** reply to each issue with a traceable conclusion first, then close it as completed / duplicate / not_planned; "bulk cleanup" is no reason to skip the explanation.

## Pitfalls

| Problem | Cause | Handling |
|---|---|---|
| A PR shows as mergeable on GitHub but still has semantic conflicts with the latest mainline | The PR base lags behind, and several PRs modify the same CI/routing files | Simulate the merge locally, resolve against the latest SSoT and rerun the full test suite |
| AV deleted payload working tree files, so ordinary scans missed them | Even the Markdown extension matches signatures | Read from Git index blobs; "skip when unreadable" is forbidden |
| The Binary Ninja MCP source is easily mistaken for official | The MCP project is a community GPL plugin, not an official Vector 35 component | State the source, reviewed commit, bridge version and loopback binding explicitly in the skill |
| Git Bash cannot faithfully simulate Linux Python→bash child processes | Windows CreateProcess resolves the system `bash.exe`/WSL first | Run Bash syntax and direct contract checks locally, with Ubuntu/macOS CI as the final authority |

## Verification

- Routing regression: 175/175
- Windows PowerShell 5.1 and PowerShell 7: P0, encoding, Evidence, IDA, smoke all passed
- Python: case-review, doc links, repository security all passed
- Bash: syntax, case workflow, new Binary Ninja route passed
- GitHub: Windows, Ubuntu, macOS, Gradle Wrapper Validation all passed
- Remote open issues / PRs: both 0

## Environment

- OS: Windows
- Git: isolated worktree + PR head ancestor verification
- CI: Windows, Ubuntu, macOS
- Data handling: only public repository metadata and redacted method records
