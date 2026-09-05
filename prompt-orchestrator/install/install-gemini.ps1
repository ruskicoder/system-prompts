# install-gemini.ps1 - Gemini CLI Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

$RequiredSources = @(".gemini\commands", ".agents\skills", "AGENT.md")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: '$Source' missing. Run: python tools\generate_integrations.py"
    }
}

$Target = "$env:USERPROFILE\.gemini"
$AgentsSkillsHome = "$env:USERPROFILE\.agents\skills"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Gemini CLI Target Deployment                       " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$Target" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$Target\commands" | Out-Null
New-Item -ItemType Directory -Force -Path "$AgentsSkillsHome" | Out-Null

Copy-Item -Path "$OrchestratorDir\.gemini\commands\*" -Destination "$Target\commands\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\.agents\skills\*" -Destination "$AgentsSkillsHome\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$Target\GEMINI.md" -Force

Write-Host "    [OK] Slash commands, shared skills, and GEMINI.md deployed successfully." -ForegroundColor Green
Write-Host "`n[SUCCESS] Gemini CLI deployment complete. Run '/commands reload', then type '/'.`n" -ForegroundColor Green
Exit 0
