# install-codex.ps1 - Codex Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

$RequiredSources = @(".agents\skills", ".codex\prompts", "AGENTS.md")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: '$Source' missing. Run: python tools\generate_integrations.py"
    }
}

$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { "$env:USERPROFILE\.codex" }
$AgentsSkillsHome = "$env:USERPROFILE\.agents\skills"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Codex Target Deployment                            " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$CodexHome" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$AgentsSkillsHome" | Out-Null
Copy-Item -Path "$OrchestratorDir\.agents\skills\*" -Destination "$AgentsSkillsHome\" -Recurse -Force

New-Item -ItemType Directory -Force -Path "$CodexHome\prompts" | Out-Null
Copy-Item -Path "$OrchestratorDir\.codex\prompts\*" -Destination "$CodexHome\prompts\" -Recurse -Force

Copy-Item -Path "$OrchestratorDir\AGENTS.md" -Destination "$CodexHome\AGENTS.md" -Force

Write-Host "    [OK] Skills deployed to $AgentsSkillsHome (Agent Skills standard)." -ForegroundColor Green
Write-Host "    [OK] Legacy prompts deployed to $CodexHome\prompts (use '/prompts:<name>')." -ForegroundColor Green
Write-Host "    [OK] AGENTS.md deployed." -ForegroundColor Green
Write-Host "`n[SUCCESS] Codex deployment complete.`n" -ForegroundColor Green
Exit 0
