# install-antigravity.ps1 - Antigravity Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "Script execution environment context missing: PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

# Pre-flight Source Validation
$RequiredSources = @("AGENT.md", "skills", "workflows")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: Required source missing -> $SourcePath"
    }
}

$Targets = @(
    "$env:USERPROFILE\.gemini\antigravity",
    "$env:USERPROFILE\.gemini\antigravity-ide"
)

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Antigravity Target Deployment                     " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

foreach ($Target in $Targets) {
    Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
    Write-Host "$Target" -ForegroundColor Yellow
    
    # Pre-create concrete leaf directories safely
    New-Item -ItemType Directory -Force -Path "$Target\skills" | Out-Null
    New-Item -ItemType Directory -Force -Path "$Target\workflows" | Out-Null
    New-Item -ItemType Directory -Force -Path "$Target\steering" | Out-Null

    # Copy files and folder contents
    Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$Target\AGENTS.md" -Force
    Copy-Item -Path "$OrchestratorDir\skills\*" -Destination "$Target\skills\" -Recurse -Force
    Copy-Item -Path "$OrchestratorDir\workflows\*" -Destination "$Target\workflows\" -Recurse -Force
    
    Write-Host "    [OK] Payload deployed successfully." -ForegroundColor Green
}

Write-Host "`n[SUCCESS] Antigravity deployment complete.`n" -ForegroundColor Green
Exit 0
