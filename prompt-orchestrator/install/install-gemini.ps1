# install-gemini.ps1 - Gemini CLI Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

# Pre-flight Source Validation
$RequiredSources = @("AGENT.md", "skills", "workflows")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: Source '$Source' missing from $OrchestratorDir"
    }
}

$Target = "$env:USERPROFILE\.gemini"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Gemini CLI Target Deployment                       " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$Target" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$Target\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$Target\workflows" | Out-Null

Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$Target\GEMINI.md" -Force
Copy-Item -Path "$OrchestratorDir\skills\*" -Destination "$Target\skills\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\workflows\*" -Destination "$Target\workflows\" -Recurse -Force

Write-Host "    [OK] GEMINI.md, skills, and workflows deployed successfully." -ForegroundColor Green
Write-Host "`n[SUCCESS] Gemini CLI deployment complete.`n" -ForegroundColor Green
Exit 0
