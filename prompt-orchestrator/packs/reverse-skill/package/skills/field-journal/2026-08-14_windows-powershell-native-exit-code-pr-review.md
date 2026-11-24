# 2026-08-14 Review of a PR on Windows PowerShell Native Command Exit Codes

## Scenario classification

Other (toolchain, supply chain bootstrap scripts, open PR review)

## Target overview

Evaluated a bootstrap script PR that pins source and commit, and verified whether it stays fail-closed under Windows PowerShell 5.1 without wrongly rejecting a legitimate checkout.

## Scope summary (redacted)

- auth_basis: the repository maintainer authorized reviewing the public PR and submitting a review
- network_profile: public code hosting platform; read-only during evidence collection, review submitted after the conclusion was confirmed
- asset_types: [public source code, CI results, Windows PowerShell bootstrap script]

## Roles

- lead_role: lead
- specialists: [supply-chain-reviewer, windows-compatibility-reviewer]

## Complete execution chain

1. Pinned the PR head commit and read the changes, discussion, CI and target script, to avoid reviewing a moving target.
2. Split the security goals into six items: pinned source, pinned commit, atomic replacement, dirty directory rejection, lockfile install and platform compatibility.
3. Confirmed that the design direction of a single manifest source, staged checkout, dirty-tree fail-closed and frozen lockfile is valid.
4. Located the checkout verification function and ran the native command and the pipeline version with `Select-Object` separately in Windows PowerShell 5.1.
5. Observed that both returned the same commit text, but the pipeline version read a `$LASTEXITCODE` of `-1`, causing a legitimate checkout to be rejected.
6. Ran the supply chain test script and confirmed that it failed before reaching the expected dirty-tree assertion, ruling out a problem in the test fixture itself.
7. Submitted a changes-requested review on the PR, asking to save the native command exit code before processing the output and to add Windows PowerShell 5.1 verification.
8. Wrote back the reproduction method and review criteria in redacted form for reuse in later PowerShell bootstrap script reviews.

## Evidence chain summary (redacted)

| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-001 | info | observed | command | `powershell.exe -NoProfile -Command "& git -C {install_dir} rev-parse HEAD; $LASTEXITCODE"` | F-001 |
| E-002 | medium | validated | command | `powershell.exe -NoProfile -Command "& git -C {install_dir} rev-parse HEAD \| Select-Object -First 1; $LASTEXITCODE"` | F-001 |
| E-003 | medium | validated | command | `powershell.exe -NoProfile -File skills/scripts/tests/test-bootstrap-supply-chain.ps1` | F-001 |

## Finding / Path summary

- top_finding: in Windows PowerShell 5.1, reading `$LASTEXITCODE` after the native command output enters the object pipeline can yield `-1`; even when the output commit matches the pinned value exactly, it triggers a wrong checkout verification failure.
- path_type: callflow
- path_one_liner: `git rev-parse` succeeds → output enters `Select-Object` → `$LASTEXITCODE` is overwritten → the fail-closed branch wrongly rejects a legitimate checkout

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| All existing CI passed but Windows still regressed | CI covered newer PowerShell and Bash but not the native command pipeline semantics of Windows PowerShell 5.1 | Ran the minimal reproduction and the complete supply chain test with `powershell.exe` | About 20 minutes |
| Identical commit text judged inconsistent | The verification logic depended on both the output and a later read of `$LASTEXITCODE` | Save the exit code immediately after the native command returns, then normalize the output separately | About 10 minutes |
| A PR shown as clean is easily mistaken as directly mergeable | mergeable only describes the Git merge state and does not prove target runtime compatibility | Treat base freshness, the platform matrix and local reproduction as independent gates | About 5 minutes |

## Toolchain findings

- The GitHub API suits pinning the PR head and reading CI and commit status; review records should be bound to the verified commit.
- `powershell.exe` and `pwsh` are not interchangeable test entries. Scripts targeting Windows PowerShell 5.1 must be tested on that host.
- `$LASTEXITCODE` is mutable session state; any later pipeline or command can make a delayed read lose the native command semantics.

## Key code/commands

```powershell
# Capture the native command output first and save the exit code immediately.
$output = & git -C $CheckoutPath rev-parse HEAD 2>$null
$gitExitCode = $LASTEXITCODE
$resolvedCommit = [string]($output | Select-Object -First 1)

if ($gitExitCode -ne 0 -or $resolvedCommit.Trim() -ne $PinnedCommit) {
    throw "Checkout verification failed"
}
```

## Improvement suggestions for this package

- Add a `powershell.exe` 5.1 test job for PRs that modify PowerShell bootstrap scripts, so `pwsh` is not the only coverage.
- Add "is the native command exit code saved before the next command" to the supply chain review checklist.
- Before merging, check the PR head, the diff against the latest main and the target platform tests together; do not let GitHub's clean status replace runtime verification.

## Reusable patterns/script snippets

Handle every PowerShell native command in three steps: execute and capture the output, save `$LASTEXITCODE` immediately, and parse the output with the PowerShell pipeline last. Error decisions may use only the saved exit code.

## Evolution actions

- [ ] Updated the routing matrix
- [ ] Updated tool-index
- [ ] Updated bootstrap-manifest
- [ ] Updated sub-skill documentation
- [x] Added pitfall records
- [ ] No update needed

## Environment information

- OS: Windows
- Tool versions: Windows PowerShell 5.1, Git 2.x
- Target platform/version: PowerShell-compatible bootstrap script, public PR head commit

## Redaction check

- [x] No real domains, IPs, credentials, tokens, cookies or PII
- [x] Local install paths replaced with `{install_dir}`
- [x] No user project files or private repository content attached

---
<!-- [Evolution statistics] Projects completed by this package: 18 | New patterns this time: 1 | Toolchain problems fixed this time: 0 -->
<!-- [Community contribution] The user authorized writing back this redacted experience through a separate PR. -->
