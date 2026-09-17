# Install only the Antigravity plugin. Python 3 standard library is sufficient.
param([string]$ConfigDir)
$ErrorActionPreference = "Stop"

$Python = $null
$Prefix = @()
foreach ($Candidate in @("python3", "python", "py")) {
    $Command = Get-Command $Candidate -ErrorAction SilentlyContinue
    if (-not $Command) { continue }
    $CandidatePrefix = @()
    if ($Candidate -eq "py") { $CandidatePrefix = @("-3") }
    & $Command.Source @CandidatePrefix -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $Python = $Command.Source
        $Prefix = $CandidatePrefix
        break
    }
}
if (-not $Python) { throw "Python 3.8+ is required for the Antigravity installer (no extra packages)." }

$InstallerArgs = @((Join-Path $PSScriptRoot "antigravity_plugin.py"))
if ($ConfigDir) { $InstallerArgs += @("--config-dir", $ConfigDir) }
& $Python @Prefix @InstallerArgs
exit $LASTEXITCODE
