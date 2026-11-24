# Verify reverse-skill PowerShell scripts and bootstrap tests

Branch `cloud/verify-reverse-pwsh`, based on master `313617d` (release 1.12.0).

## Result

| Acceptance item | Status |
|---|---|
| 0 parse errors across .ps1 files under packs/ | 40 of 40 reverse-skill files parse. 1 error remains in `packs/cyber-skills/.../audit_smb_signing.ps1:325` (outside scope, see Open issues) |
| test-routing.ps1 passes | Pass, 221 of 221 |
| Bootstrap tests pass, or each block is named | Both blocked by the session rm guard. Output is in Evidence |
| PowerShell and bash routers agree on three hints | Agree on the three hints |
| `validate_packs.py` 0 problems | 5 packs checked, 0 problems |
| `generate_installers.py --check` current | Installers are current |
| `check.py secrets` and `unicode` 0 gate findings | 0 gate findings for both checks |

PowerShell 7.7.0 came from the Microsoft package source (`packages-microsoft-prod.deb` for Ubuntu 24.04, then `apt-get install powershell`).

In the 40 reverse-skill files, the parser found no error. The translation did not break quotes, here-strings or keywords. A token comparison with upstream commit `b972ad0` shows that 38 files match token for token outside string and comment text. The other 2 files (`verify-doc-facts.ps1`, `verify-routing-coherence.ps1`) drop the checks on `RULES_zh.md` and `README_zh.md`, which the port does not ship.

The port broke one test. In `verify-routing-coherence.ps1`, six checks failed under pwsh. The translator wrote English needles that differ from the wording of the translated docs. Commit `f70c09d` changes five needles to the doc wording. The sixth check (`do not delete files before evidence is preserved`) already matched case-insensitively once its partner needle matched. The docs stay unchanged. After the fix, the package's Linux CI set passes.

Commit `9eaacf2` adds one step to `.github/workflows/prompt-orchestrator-ci.yml`. The step parses the .ps1 files under `prompt-orchestrator/packs` with pwsh and fails on a parse error. For the known cyber-skills file, the step emits a warning.

## Evidence

### Install

```
$ curl -sSLo /tmp/pkgms.deb https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb && dpkg -i /tmp/pkgms.deb && apt-get update && apt-get install -y powershell
Setting up powershell (7.7.0-1.deb) ...
$ pwsh -v
PowerShell 7.7.0
```

### Parse check (ParseFile over packs/)

```
$ pwsh -NoProfile -File parse.ps1      # [Parser]::ParseFile on each .ps1 under prompt-orchestrator/packs
./prompt-orchestrator/packs/cyber-skills/skills/detecting-ntlm-relay-with-event-correlation/scripts/audit_smb_signing.ps1:325:20: A switch statement must have one of the following:  '-file file_name' or '( expression )'.
Parsed 42 files, 1 parse errors
```

The brief counted 40 files. The tree has 42 .ps1 files under packs/ (40 in reverse-skill, 2 in cyber-skills).

### Token comparison with upstream b972ad0

```
$ pwsh -File tokdiff.ps1 -Port <repo>/packs/reverse-skill/package -Up <upstream b972ad0>
DIFF skills/scripts/verify-doc-facts.ps1 (113 token diffs)          # removed RULES_zh.md checks
DIFF skills/scripts/verify-routing-coherence.ps1 (8 token diffs)    # removed RULES_zh.md from the scope-gate loop
files with non-literal token differences: 2
```

### Package PowerShell tests (copy outside the repo, run from the package root, `powershell` shim to pwsh as in the package CI)

Before the fix:

```
verify-routing-coherence EXIT=1
[FAIL] field 'feasibility latch' missing in .../re-agent-workflow.md
[FAIL] field 'timebox' missing in .../re-agent-workflow.md
[FAIL] field 'IOC/ATT&CK not required' missing in .../docs-generator/SKILL.md
[FAIL] malware remediation does not require evidence preservation before destructive actions
[FAIL] field 'timebox' missing in .../malware-analysis/SKILL.md
[FAIL] representative RE workflow missing delta consumer contract
FAILED 6
smoke EXIT=1    (VERIFY_EXIT=1 from verify-routing-coherence)
```

After the fix:

```
test-routing EXIT=0                  | OVERALL: ALL PASS (221)
verify-routing-coherence EXIT=0      | ALL ROUTING COHERENCE CHECKS PASSED
test-bootstrap-supply-chain EXIT=0   | PowerShell bootstrap supply-chain regression passed
test-parse-contracts EXIT=0          | ALL PARSE CONTRACTS PASSED
test-skill-name-uniqueness EXIT=0    | ALL SKILL NAME CONTRACTS PASSED
test-workflow-title-safety EXIT=0    | WORKFLOW TITLE SAFETY CHECKS PASSED
test-bootstrap-codex-encoding EXIT=0 | OVERALL: ALL PASS
test-consolidate-evidence EXIT=0     | CONSOLIDATE_ALIGN_OK
smoke EXIT=0                         | OVERALL: ALL PASS
verify-doc-facts EXIT=0              | verify-doc-facts: 0 failure(s)
extract-summaries -Check EXIT=0      | [CHECK] INDEX.md up to date
scan-leaks -Path skills/field-journal EXIT=0 | scan-leaks: scanned 61 files, 0 finding(s)
```

The package CI runs two tests on Windows PowerShell 5.1 only (`.github/workflows/ci.yml` lines 56 - 64). On Linux they fail for Windows reasons.

```
test-client-neutral-bootstrap.ps1 EXIT=1 | Codex-only bootstrap did not report ready
    (the test writes node.cmd, npm.cmd and npx.cmd stubs and joins PATH with ';')
test-p0-friction.ps1 EXIT=1 | The term 'cmd' is not recognized ... (line 257: cmd /c ...)
```

### Bash bootstrap tests (copy outside the repo)

```
$ bash skills/scripts/test-bootstrap-manifest.sh
parser-bootstrap failed:
[INFO] platform=linux doc=docs/platforms/linux.md tools_root=/tmp/reverse-bootstrap-test-aFfIzg/tools mcp_host=none
[INFO] apt install python3
[INFO] ensure agent-browser
[ { "name": "agent-browser", "status": "ready" } ]
rm: command not found
EXIT=1

$ bash skills/scripts/test-client-neutral-bootstrap.sh
rm: command not found
EXIT=127

$ type -a rm
rm is /root/.claude/rm-guard/<id>/refuse/rm
rm is /usr/bin/rm
```

The block is the session rm guard. The guard is first on PATH and execs "the next rm on PATH". Both tests symlink `$(command -v rm)` (the guard) into a stub bin directory and then run with only that directory on PATH. The guard finds no real rm and exits 127. In `test-bootstrap-manifest.sh`, the sink checks before line 180 pass. The test stops at the parser-bootstrap fixture (line 190, `PATH="$NO_PYTHON_BIN"`). In `test-client-neutral-bootstrap.sh`, the test stops at its first `refresh-tool-index.sh` call (line 112, `PATH="$BIN_DIR"`). The guard was left in place.

Other bash tests that the package docs name:

```
skills/scripts/test-routing.sh EXIT=0             | OVERALL: ALL PASS (221 routing cases + default-root regression)
skills/scripts/test-bash-workflow.sh EXIT=0       | === All Bash Workflow Tests Passed ===
skills/scripts/test-apk-decode-manifest.sh EXIT=0 | === All APK Decode Manifest Tests Passed ===
skills/scripts/test-docker-assets.sh EXIT=0       | === Docker asset smoke passed ===
kali/scripts/test-pwntools-discovery.sh EXIT=0    | Kali pwntools discovery regression passed
```

### Router agreement

| Hint | master-route.ps1 | master-route.sh |
|---|---|---|
| Android APK reverse engineering: unpack app-release.apk and hook its login check | R1 `skills/apk-reverse/SKILL.md`, high | R1 `skills/apk-reverse/SKILL.md`, high |
| Windows PE binary: reverse sample.exe, an x64 PE32+ executable, find the license check | R0 `skills/reverse-engineering/SKILL.md`, high | R0 `skills/reverse-engineering/SKILL.md`, high |
| JS crypto routine: reverse the obfuscated JavaScript that signs the API request with AES and an HMAC sign parameter | R3 `skills/js-reverse/SKILL.md`, medium, secondary `skills/reverse-engineering/SKILL.md` | R3 `skills/js-reverse/SKILL.md`, medium, secondary `skills/reverse-engineering/SKILL.md` |

```
$ diff ps3/route-scope.md sh3/route-scope.md
< ﻿# reverse-skill Master route (PRIMARY)
< - created: 2026-11-24T18:06:29.0462014+00:00
> # reverse-skill Master route (PRIMARY)
> - created: 2026-11-24T18:06:29.117799+00:00
```

The two route-scope.md files differ only in the UTF-8 BOM and the timestamp.

### CI step

```
$ cd prompt-orchestrator && pwsh -File <run block of the new step>
::warning file=prompt-orchestrator/packs/cyber-skills/.../audit_smb_signing.ps1,line=325::A switch statement must have one of the following:  '-file file_name' or '( expression )'.
Parsed 42 .ps1 files under packs/, 0 blocking parse errors
EXIT=0

# Negative test: a copy of packs/ with an injected unterminated string
::error file=prompt-orchestrator/packs/reverse-skill/package/skills/scripts/zz-broken.ps1,line=2::The string is missing the terminator: ".
::error file=prompt-orchestrator/packs/reverse-skill/package/skills/scripts/zz-broken.ps1,line=1::Missing closing '}' in statement block or type definition.
Parsed 43 .ps1 files under packs/, 2 blocking parse errors
NEG EXIT=1
```

### Repository checks

```
$ python3 prompt-orchestrator/tools/validate_packs.py
5 packs checked, 0 problems
$ python3 prompt-orchestrator/tools/generate_installers.py --check
installers are current
$ python3 prompt-orchestrator/skills/ci-enforcement/check.py secrets --repo . --base origin/master --head HEAD
summary: 0 gate finding(s), 0 advisory finding(s)
$ python3 prompt-orchestrator/skills/ci-enforcement/check.py unicode --repo . --base origin/master --head HEAD
summary: 0 gate finding(s), 0 advisory finding(s)
```

## Open issues

1. `packs/cyber-skills/skills/detecting-ntlm-relay-with-event-correlation/scripts/audit_smb_signing.ps1:325` does not parse (`$riskLevel = switch {` has no subject). The file sits outside this branch's scope, and the session refused the edit for that reason. The fix needs `break` in each branch. With `switch ($true)` alone, a score of 70 yields `CRITICAL,HIGH,MEDIUM`. The tested fix is below. After the fix lands, remove the `$known` entry from the CI step.

   ```powershell
   $riskLevel = switch ($true) {
       ($riskScore -ge 60) { "CRITICAL"; break }
       ($riskScore -ge 40) { "HIGH"; break }
       ($riskScore -ge 20) { "MEDIUM"; break }
       default { "LOW" }
   }
   ```

2. The bash bootstrap tests cannot run in this hosted session because of the rm guard. A run on a plain Linux host or in GitHub Actions confirms them. The upstream package CI runs `test-client-neutral-bootstrap.sh` in its `sh-syntax` job.

3. `test-client-neutral-bootstrap.ps1` and `test-p0-friction.ps1` depend on Windows (`.cmd` stubs, `;` in PATH, `cmd /c`). They need a Windows PowerShell 5.1 run to be verified.

4. In `verify-routing-coherence.ps1`, the negative check `JS/Web signature reverse engineering report\s*\|[^\r\n]*malware` cannot match. The doc row reads `4. JS/web signature reverse engineering |` without "report". Upstream has the same mismatch (needle `JS/Web 签名逆向报告`, row `4. JS/Web 签名逆向`). A literal fix would also trip on the row text "no malware overlay". The check stays as it was.

5. `master-route.ps1:174` prints `Wrote <dir>\route-scope.md` with a backslash on Linux. The file itself is written with `Join-Path`. Upstream has the same line.

6. Running the upstream scripts for a side-by-side baseline was blocked in this session. The comparison with upstream uses parser token streams and text diffs.

QUESTION FOR THE LEADER: Should a follow-up branch apply the `audit_smb_signing.ps1` fix from Open issue 1 and remove the CI exception? Recommended answer: yes. The follow-up is a 4-line change in cyber-skills plus a 1-line removal in the workflow. After the change, the step parses the 42 files under packs/ with no exception.
