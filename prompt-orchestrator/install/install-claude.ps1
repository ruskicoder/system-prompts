# install-claude.ps1 - Claude / Claude Code Installer
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}

$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

$RequiredSources = @(".claude\skills", "AGENTS.md")
foreach ($Source in $RequiredSources) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $Source
    if (-not (Test-Path -Path $SourcePath)) {
        Throw "Pre-flight validation failed: '$Source' missing. Run: python tools\generate_integrations.py"
    }
}

$Target = "$env:USERPROFILE\.claude"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Claude / Claude Code Target Deployment             " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "--> Deploying configuration payload to: " -NoNewline -ForegroundColor Gray
Write-Host "$Target" -ForegroundColor Yellow

New-Item -ItemType Directory -Force -Path "$Target\skills" | Out-Null
Copy-Item -Path "$OrchestratorDir\.claude\skills\*" -Destination "$Target\skills\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\AGENTS.md" -Destination "$Target\AGENTS.md" -Force

$ClaudeMd = "$Target\CLAUDE.md"
$Marker = "<!-- prompt-orchestrator:start -->"
if (-not (Test-Path -Path $ClaudeMd)) { New-Item -ItemType File -Path $ClaudeMd -Force | Out-Null }
$ExistingContent = Get-Content -Path $ClaudeMd -Raw -ErrorAction SilentlyContinue
if ($ExistingContent -and $ExistingContent.Contains($Marker)) {
    Write-Host "    [SKIP] CLAUDE.md already references prompt-orchestrator." -ForegroundColor Gray
} else {
    Add-Content -Path $ClaudeMd -Value "`n$Marker`n@AGENTS.md`n<!-- prompt-orchestrator:end -->"
    Write-Host "    [OK] CLAUDE.md updated to import AGENTS.md." -ForegroundColor Green
}

Write-Host "    [OK] Skills and AGENTS.md deployed successfully." -ForegroundColor Green
Write-Host "`n[SUCCESS] Claude / Claude Code deployment complete.`n" -ForegroundColor Green
Exit 0
