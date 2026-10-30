# install-harness.ps1 [-Tools claude,codex] - add the harness to an existing core install.
param([string[]]$Tools = @("claude", "codex"))
$ErrorActionPreference = "Stop"
$ScriptFolder = $PSScriptRoot
$ToolList = ($Tools -join ",")

$Python = $null
$Prefix = @()
if (Get-Command py -ErrorAction SilentlyContinue) { $Python = "py"; $Prefix = @("-3") }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $Python = "python" }

if ($Python) {
    & $Python @Prefix -c "import sys; sys.exit(sys.version_info < (3, 11))"
    if ($LASTEXITCODE -eq 0) {
        & $Python @Prefix (Join-Path $ScriptFolder "install.py") --harness-only --yes --tools $ToolList
        exit $LASTEXITCODE
    }
}
& (Join-Path $ScriptFolder "install-tui.ps1") -HarnessOnly -Yes -Tools $Tools
exit $LASTEXITCODE
