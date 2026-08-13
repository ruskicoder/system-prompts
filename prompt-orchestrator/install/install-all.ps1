# Master installer: install prompt-orchestrator to all supported platforms on Windows
$ErrorActionPreference = "Stop"

Write-Host "==> Installing prompt-orchestrator to all platforms on Windows..."

$Scripts = @(
    "install-antigravity.ps1",
    "install-codex.ps1",
    "install-cursor.ps1",
    "install-gemini.ps1",
    "install-openclaw.ps1",
    "install-opencode.ps1"
)

foreach ($Script in $Scripts) {
    $ScriptPath = Join-Path $PSScriptRoot $Script
    if (Test-Path $ScriptPath) {
        Write-Host "--- Running $Script ---"
        & $ScriptPath
    } else {
        Write-Warning "Script not found: $ScriptPath"
    }
}

Write-Host "==> All Windows installations complete"
