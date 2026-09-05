# install-antigravity.ps1 - Antigravity Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "Script execution environment context missing: PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

$RequiredSources = @(".gemini\commands", ".agents\skills", "AGENT.md")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: Required source missing -> $SourcePath"
    }
}

$AgentsSkillsHome = "$env:USERPROFILE\.agents\skills"
New-Item -ItemType Directory -Force -Path "$AgentsSkillsHome" | Out-Null
Copy-Item -Path "$OrchestratorDir\.agents\skills\*" -Destination "$AgentsSkillsHome\" -Recurse -Force

$Targets = @(
    "$env:USERPROFILE\.gemini\antigravity",
    "$env:USERPROFILE\.gemini\antigravity-ide"
)

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Antigravity Target Deployment                      " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

foreach ($Target in $Targets) {
    Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
    Write-Host "$Target" -ForegroundColor Yellow

    New-Item -ItemType Directory -Force -Path "$Target\commands" | Out-Null
    Copy-Item -Path "$OrchestratorDir\.gemini\commands\*" -Destination "$Target\commands\" -Recurse -Force
    Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$Target\AGENTS.md" -Force

    Write-Host "    [OK] Payload deployed successfully." -ForegroundColor Green
}

Write-Host "    [OK] Shared skills deployed to $AgentsSkillsHome" -ForegroundColor Green
Write-Host "`n[SUCCESS] Antigravity deployment complete.`n" -ForegroundColor Green
Exit 0
