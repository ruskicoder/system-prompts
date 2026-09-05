# install-cursor.ps1 - Cursor Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

$RequiredSources = @(".cursor\commands", ".cursor\rules", "AGENTS.md")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: '$Source' missing. Run: python tools\generate_integrations.py"
    }
}

$Target = "$env:USERPROFILE\.cursor"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Cursor Target Deployment                           " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$Target" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$Target\commands" | Out-Null
New-Item -ItemType Directory -Force -Path "$Target\rules" | Out-Null

Copy-Item -Path "$OrchestratorDir\.cursor\commands\*" -Destination "$Target\commands\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\.cursor\rules\orchestrator.mdc" -Destination "$Target\rules\prompt-orchestrator.mdc" -Force
Copy-Item -Path "$OrchestratorDir\AGENTS.md" -Destination "$Target\AGENTS.md" -Force

Write-Host "    [OK] Slash commands and orchestrator rule deployed successfully." -ForegroundColor Green
Write-Host "`n[SUCCESS] Cursor deployment complete. Type '/' in chat to browse.`n" -ForegroundColor Green
Exit 0
