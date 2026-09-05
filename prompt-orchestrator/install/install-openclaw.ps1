# install-openclaw.ps1 - OpenClaw Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

$RequiredSources = @("AGENT.md", "AGENTS.md", "skills", "workflows", ".agents\skills")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: Source '$Source' missing."
    }
}

$Target = "$env:USERPROFILE\.openclaw"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " OpenClaw Target Deployment                         " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$Target" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$Target\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$Target\workflows" | Out-Null
New-Item -ItemType Directory -Force -Path "$Target\agents-skills" | Out-Null

Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$Target\AGENT.md" -Force
Copy-Item -Path "$OrchestratorDir\AGENTS.md" -Destination "$Target\AGENTS.md" -Force
Copy-Item -Path "$OrchestratorDir\skills\*" -Destination "$Target\skills\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\workflows\*" -Destination "$Target\workflows\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\.agents\skills\*" -Destination "$Target\agents-skills\" -Recurse -Force

Write-Host "    [OK] AGENT.md, AGENTS.md, skills, and workflows deployed successfully." -ForegroundColor Green
Write-Host "`n[SUCCESS] OpenClaw deployment complete.`n" -ForegroundColor Green
Exit 0
