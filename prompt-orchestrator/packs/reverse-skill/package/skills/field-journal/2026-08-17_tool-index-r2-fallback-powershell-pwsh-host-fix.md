# 2026-08-17 reverse-skill

## Scenario classification
Toolchain and environment (bootstrap phase defect fixes)

## Target overview
Fixed three layers of masked defects in the local bootstrap: tool-index misreported the radare2 main analyzer `r2` as no; several test scripts hard-coded `powershell` child process calls that fail on machines with only PowerShell 7+; and a pin gate StrictMode property access bug hidden by that failure.

## Scope summary (redacted)
- auth_basis: own_system (this repository itself)
- network_profile: offline / no ACT against external targets
- asset_types: [local scripts and tool index]

## Roles
- lead_role: lead
- specialists: [bootstrap, test-infra]

## Complete execution chain

1. Ran the bootstrap per section 0 of `README_AI.md`: `refresh-tool-index.ps1` generated tool-index.md (37 tools).
2. Reading `tool-index.md` revealed an anomaly: `r2` (the radare2 main analyzer) = no, while `rabin2/rasm2/radiff2/rahash2/rax2/r2pm` in the same directory were all yes.
3. Listed `C:\Users\{username}\Tools\radare2\bin` to confirm: `r2.bat` exists (21 bytes, content `@"%~dp0\radare2" %*`) and `radare2.exe`, **but no `r2.exe`**.
4. Read `lib/ToolDiscovery.ps1:131-141`: the `r2` Fallbacks look only for `r2.exe` and miss `r2.bat`/`radare2.exe`. By comparison, `jadx`/`apktool`/`analyzeHeadless` all have fallbacks for `.bat` tools.
5. Fix: added `r2.bat` and `radare2.exe` paths to the `r2` Fallbacks (covering `%USERPROFILE%\Tools\radare2\bin`, the root directory and `C:\Tools\`), keeping the original `r2.exe` fallback for compatibility with other machines.
6. Reran `refresh-tool-index.ps1`: `r2` turned yes, path `r2.bat`, version `radare2 6.2.0`, source `FallbackPath`.
7. `smoke.ps1` still FAILed: `verify-routing-coherence exit 1`. Running verify directly to see the error located a hard-coded `& powershell` at `verify-routing-coherence.ps1:257`; this machine has no `powershell` (only `pwsh` 7.6.4).
8. Grepped every `.ps1` in the repository for `powershell\s(-NoProfile|-ExecutionPolicy|-File|-Command)` and found 20+ hard-coded `& powershell` child process calls in 5 scripts (verify 7 / test-p0-friction 18 / test-routing 1 / case-init 1; the rest are comment examples).
9. Found that `smoke.ps1:31-46` already uses `$SmokeHostExe` correctly (current process path first → pwsh → Windows PowerShell path fallback). Extracted that verified logic into a shared function `Resolve-ReverseHostExe` in a new `lib/HostRuntime.ps1`, resolution order: current process → `pwsh` → `powershell` → `%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe`.
10. The 4 child scripts dot-source `HostRuntime.ps1` and define `$HostExe`; `replaceAll` turns `& powershell -NoProfile -ExecutionPolicy Bypass -File` into `& $HostExe -NoProfile -ExecutionPolicy Bypass -File`; the `cmd /c "powershell ..."` at `test-p0-friction.ps1:244` was changed separately to `cmd /c "`"$HostExe`" ..."` (the path may contain spaces and needs quoting).
11. Reran smoke; verify got past 257 but exposed that the pin gate at `verify-routing-coherence.ps1:414` errors under `Set-StrictMode -Version Latest` when it accesses nonexistent properties such as `$cap.pinnedVersion`. This pre-existing bug had been masked by the powershell bug until now.
12. Fixed 414: converted `$cap` to a hashtable (`$capMap`); index access to a nonexistent key returns `$null` without an error, and the pin gate semantics stay the same.
13. Reran smoke → ALL PASS (VERIFY_EXIT=0 / PARSE 11/11 / ROUTE 9/9).
14. Ran `test-routing.ps1` → 166/166 ALL PASS.
15. Ran `test-p0-friction.ps1` → most passed, but `:343` and `:364` hit `Start-Process -FilePath 'powershell.exe'` (the earlier grep pattern `powershell\s+(-NoProfile...)` missed the literal `powershell.exe`).
16. Grepped `powershell\.exe` and confirmed that only the two places at 343/364 in test-p0-friction are hard-coded Start-Process calls (the rest are compatibility lookups or fallback paths); `replaceAll` changed them to `Start-Process -FilePath $HostExe`.
17. Reran `test-p0-friction.ps1` → ALL PASS (FAIL_COUNT=0). All three suites green.

## Evidence chain summary (redacted)
> This was a bootstrap fix of this repository itself, with no ACT against an external target and no evidence files produced under a case directory. Below are reproducible verification commands (equivalent Evidence).

| E-id | severity | status | source_type | Reusable command pattern | Related Finding |
|------|----------|--------|-------------|----------------|--------------|
| E-r2 | info | validated | command | After `pwsh -File skills/scripts/refresh-tool-index.ps1`, the `r2` row in tool-index.md = yes | F-r2 |
| E-smoke | info | validated | command | `pwsh -File skills/scripts/smoke.ps1` → `OVERALL: ALL PASS` | F-host |
| E-route | info | validated | command | `pwsh -File skills/scripts/test-routing.ps1` → `166/166 ALL PASS` | F-host |
| E-p0 | info | validated | command | `pwsh -File skills/scripts/test-p0-friction.ps1` → `OVERALL: ALL PASS` | F-host |

## Finding / Path summary
- top_finding: three classes of defects masked each other in layers: the `r2` fallback missed the `.bat` entry → `verify` failed and aborted on hard-coded `powershell` → which masked the pin gate StrictMode property access bug; the grep compatibility scan also missed the literal `powershell.exe`.
- path_type: solve
- path_one_liner: unify child process entry with the shared `Resolve-ReverseHostExe` (current process first), add `.bat`/`radare2.exe` fallbacks for `r2`, and access optional PSCustomObject properties safely through a hashtable.

## Pitfall record

| Problem | Cause | Solution | Time |
|------|------|---------|------|
| tool-index marked `r2` no, while the other r2* tools in the same directory were yes | The `r2` Fallbacks in `ToolDiscovery.ps1` look only for `r2.exe`, but the radare2 Windows distribution wraps `radare2.exe` with `r2.bat` and has no `r2.exe` | Added `r2.bat` and `radare2.exe` path fallbacks | Short |
| smoke still FAILed: verify exit 1 | verify hard-codes `& powershell` internally; this machine has only pwsh 7+ and no `powershell` | Created `Resolve-ReverseHostExe` in `lib/HostRuntime.ps1` and replaced the calls in 4 scripts with `& $HostExe` | Medium |
| After fixing powershell, verify failed again at 414 | A pre-existing bug masked by the powershell bug at 257: under StrictMode, accessing nonexistent properties such as `$cap.pinnedVersion` errors | Converted `$cap` to the hashtable `$capMap`; index access does not error | Short |
| test-p0-friction failed again at 343/364 | Hard-coded `Start-Process -FilePath 'powershell.exe'`; the earlier grep pattern `powershell\s+(-NoProfile...)` missed the literal `powershell.exe` | Completed the search with grep `powershell\.exe` and switched to `$HostExe` | Short |
| test-p0-friction prints many `Exception: case-init.ps1:54` | Test 14b deliberately uses an invalid CaseName to make case-init throw; this is expected | No action needed; a final FAIL_COUNT=0 means a pass | - |

## Toolchain findings
- **radare2 Windows distribution layout**: the main program is `radare2.exe`, and `r2.bat` (`@"%~dp0\radare2" %*`) is its batch wrapper; **there is no `r2.exe`**. Any tool scan that probes for `r2.exe` misreports it. `rabin2.exe`/`rasm2.exe` and the like in the same directory are standalone `.exe` files and probe normally.
- **PowerShell 7+ only environment**: this machine has `pwsh` 7.6.4 (path `C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.4.0_x64__8wekyb3d8bbwe\pwsh.exe`) and **no `powershell` / `powershell.exe`**. Every `& powershell ...` child process call fails outright in this environment.
- **StrictMode property access**: under `Set-StrictMode -Version Latest`, accessing a nonexistent property of a `PSCustomObject` throws; index access to a nonexistent hashtable key returns `$null`, which is the safe approach for "many optional properties" cases such as the pin gate.
- **Blind spot of grep compatibility scans**: `powershell\s+(-NoProfile...)` catches only the `& powershell -File` form and misses `Start-Process -FilePath 'powershell.exe'` and `cmd /c "powershell ..."`. Compatibility scans should cover both `powershell\s` and `powershell\.exe`.

## Key code/commands

```powershell
# lib/HostRuntime.ps1: unified PowerShell entry for child processes (current process first)
function Resolve-ReverseHostExe {
    [CmdletBinding()] [OutputType([string])] param()
    $hostExe = $null
    try { $p = (Get-Process -Id $PID -ErrorAction Stop).Path; if ($p -and (Test-Path -LiteralPath $p)) { $hostExe = $p } } catch { }
    if (-not $hostExe) { $c = Get-Command pwsh -ErrorAction SilentlyContinue; if ($c -and $c.Source) { $hostExe = $c.Source } }
    if (-not $hostExe) { $c = Get-Command powershell -ErrorAction SilentlyContinue; if ($c -and $c.Source) { $hostExe = $c.Source } }
    if (-not $hostExe -and $env:SystemRoot) { $f = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'; if (Test-Path -LiteralPath $f) { $hostExe = $f } }
    if (-not $hostExe) { throw 'No usable PowerShell host executable found.' }
    return $hostExe
}

# ToolDiscovery.ps1 r2 Fallbacks: add .bat/.exe entries
Fallbacks = @(
    @{ Type = 'command'; Value = 'r2' },
    @{ Type = 'command'; Value = 'radare2' },
    @{ Type = 'path'; Value = (Join-Path $userProfile 'Tools\radare2\bin\r2.bat') },
    @{ Type = 'path'; Value = (Join-Path $userProfile 'Tools\radare2\bin\radare2.exe') },
    @{ Type = 'path'; Value = (Join-Path $userProfile 'Tools\radare2\bin\r2.exe') }
    # ... root directory and C:\Tools mirrors
)

# verify-routing-coherence.ps1:412: safe property access for the pin gate
foreach ($cap in $mc.capabilities) {
    $capMap = @{}
    foreach ($prop in $cap.PSObject.Properties) { $capMap[$prop.Name] = $prop.Value }
    if (-not $capMap['canAutoInstall']) { continue }
    $hasPin = ($capMap['pinnedVersion'] -or $capMap['pinnedCommit'] -or $capMap['pinPolicy'])
    # ... switch ($capMap['bootstrapKind']) ...
}
```

## Improvement suggestions for this package
- **Script the compatibility scan**: in `verify-routing-coherence.ps1` or a standalone lint, scan the child process calls of every `.ps1`, forbid bare `powershell` / `powershell.exe`, and require `Resolve-ReverseHostExe` everywhere. This time a manual grep was used, which misses cases easily (the `powershell.exe` blind spot already bit).
- **`.bat` convention in the tool catalog**: on Windows, `jadx`/`apktool`/`r2`/`analyzeHeadless` are all `.bat` files wrapping an `.exe`; the catalog should configure both the `.bat` and the matching `.exe` fallback for each such tool, to avoid hitting the problem one tool at a time.
- **CI should include a "pwsh only" matrix**: on GitHub Actions `windows-latest`, this class of bug surfaces if Windows PowerShell 5.1 is not preinstalled. `smoke.ps1` already does it right with `$SmokeHostExe`, but the child scripts did not reuse it.
- **Traversing PSCustomObject under StrictMode**: for checks with a "loose object schema" such as the pin gate, convert to a hashtable for access, or provide a `Get-SafeProp` helper.

## Reusable patterns/script snippets
- `Resolve-ReverseHostExe`: whenever a script needs to start a child PowerShell process, dot-source `lib/HostRuntime.ps1`, then `& $HostExe -NoProfile -ExecutionPolicy Bypass -File <script> ...`; compatible with pwsh-only, powershell-only and mixed environments.
- `$capMap` conversion: copy `PSCustomObject` properties into a hashtable and use index access, avoiding the StrictMode missing-property exception.
- `r2.bat` → `radare2.exe` pass-through: the version check `r2.bat -v` correctly returns `radare2 6.2.0`, which proves that the `.bat` wrapper passes arguments through and can serve as a catalog entry.

## Evolution actions
- [x] Updated tool-index (r2 turned yes, path r2.bat)
- [x] Added `skills/scripts/lib/HostRuntime.ps1`
- [x] Fixed the `ToolDiscovery.ps1` r2 Fallbacks
- [x] Fixed `verify-routing-coherence.ps1` hard-coded powershell + pin gate StrictMode
- [x] Fixed hard-coded powershell in `case-init.ps1` / `test-routing.ps1` / `test-p0-friction.ps1`
- [ ] Updated the routing matrix (none)
- [ ] Updated bootstrap-manifest (none)
- [ ] Added a pitfalls record (this entry)

## Environment information
- OS: Windows (win32)
- Shell/Host: pwsh 7.6.4 (`C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.4.0_x64__8wekyb3d8bbwe\pwsh.exe`); this machine has no `powershell` / `powershell.exe`
- radare2: 6.2.0 +1 abi:132 @ windows-x86_64 (installed in `C:\Users\{username}\Tools\radare2\bin\`)
- Repository root: `D:\Sources\reverse-skill`

## Redaction requirements
This was a fix of this repository's own scripts, with no real target domains/IPs/credentials, so no redaction is needed.

## Index sync (last step before submission)

After writing this journal, update `_index.md` in sync:
1. Add a row to the "Toolchain and environment" subsection ✓
2. Append this file name to "Frequent success patterns" (unified PowerShell child process entry) ✓
3. Append this file name to the "Entity inverted index" (reverse-skill bootstrap scripts) ✓
4. Update the total count and the last updated date in "Statistics" ✓

---
<!-- [Evolution statistics] Projects completed by this package: 19 | New patterns this time: 1 (unified Resolve-ReverseHostExe child process entry) | Toolchain problems fixed this time: 3 (r2 fallback / hard-coded powershell / pin gate StrictMode) -->
<!-- [Community contribution] This fix repairs a bootstrap defect of the repository itself and qualifies as a fix PR under CONTRIBUTING.md; when done, ask the user whether to submit it. -->
