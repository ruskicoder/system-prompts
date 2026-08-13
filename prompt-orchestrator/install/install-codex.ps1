# install-codex.ps1 - Codex Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

# Pre-flight Source Validation
$RequiredSources = @("AGENT.md", "skills", "workflows", ".kiro\steering")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: Source architectural footprint component '$Source' missing."
    }
}

$Target = "$env:USERPROFILE\.codex"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Codex Target Deployment                            " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$Target" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$Target\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$Target\workflows" | Out-Null
New-Item -ItemType Directory -Force -Path "$Target\steering" | Out-Null

Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$Target\AGENTS.md" -Force
Copy-Item -Path "$OrchestratorDir\skills\*" -Destination "$Target\skills\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\workflows\*" -Destination "$Target\workflows\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\.kiro\steering\*" -Destination "$Target\steering\" -Recurse -Force

Write-Host "    [OK] AGENTS.md, skills, workflows, and steering deployed successfully." -ForegroundColor Green
Write-Host "`n[SUCCESS] Codex deployment complete.`n" -ForegroundColor Green
Exit 0
