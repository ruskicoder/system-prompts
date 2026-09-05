# install-opencode.ps1 - OpenCode Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

$RequiredSources = @(".opencode\skills", ".opencode\commands", "AGENTS.md")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: '$Source' missing. Run: python tools\generate_integrations.py"
    }
}

$Target = "$env:USERPROFILE\.config\opencode"
if (-not (Test-Path -Path (Split-Path -Path $Target -Parent))) {
    $Target = "$env:APPDATA\opencode"
}

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " OpenCode Target Deployment                         " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$Target" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$Target\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$Target\commands" | Out-Null

Copy-Item -Path "$OrchestratorDir\.opencode\skills\*" -Destination "$Target\skills\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\.opencode\commands\*" -Destination "$Target\commands\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\AGENTS.md" -Destination "$Target\AGENTS.md" -Force

Write-Host "    [OK] Skills, slash commands, and AGENTS.md deployed successfully." -ForegroundColor Green
Write-Host "`n[SUCCESS] OpenCode deployment complete. Type '/' in the TUI to browse.`n" -ForegroundColor Green
Exit 0
