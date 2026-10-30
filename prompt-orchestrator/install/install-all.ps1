# install-all.ps1 - install prompt-orchestrator (core and, by default, the harness) on Windows.
# Uses the Python menu (install.py) when Python 3 exists, otherwise the native PowerShell menu
# (install-tui.ps1). Arguments pass through, for example:
#   powershell -File install\install-all.ps1 --core --yes     (Python menu flags)
#   powershell -File install\install-all.ps1 -Core -Yes       (native menu switches)
$ErrorActionPreference = "Stop"
$ScriptFolder = $PSScriptRoot

$Python = $null
$Prefix = @()
if (Get-Command py -ErrorAction SilentlyContinue) { $Python = "py"; $Prefix = @("-3") }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = "python" }

if ($Python) {
    & $Python @Prefix (Join-Path $ScriptFolder "install.py") @args
    exit $LASTEXITCODE
}
Write-Host "--- Python 3 not found; using the native installer (harness hooks need Python 3.11+)" -ForegroundColor Yellow
& (Join-Path $ScriptFolder "install-tui.ps1") @args
exit $LASTEXITCODE
