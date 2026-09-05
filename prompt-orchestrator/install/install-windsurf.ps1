# install-windsurf.ps1 - Windsurf Installer (project-scoped)
param(
    [string]$TargetDir = (Get-Location).Path
)
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}
$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

if (-not (Test-Path -Path $TargetDir)) {
    Throw "Target project directory does not exist: $TargetDir`nUsage: powershell install\install-windsurf.ps1 -TargetDir C:\path\to\project"
}
$TargetDir = [System.IO.Path]::GetFullPath($TargetDir)

Write-Host "==> Installing prompt-orchestrator Windsurf workflows into $TargetDir" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path "$TargetDir\.windsurf\workflows" | Out-Null
New-Item -ItemType Directory -Force -Path "$TargetDir\.windsurf\rules" | Out-Null

Copy-Item -Path "$OrchestratorDir\.windsurf\workflows\*" -Destination "$TargetDir\.windsurf\workflows\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\.windsurf\rules\*" -Destination "$TargetDir\.windsurf\rules\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\AGENTS.md" -Destination "$TargetDir\AGENTS.md" -Force

Write-Host "`n[SUCCESS] Windsurf workflows deployed. Type '/' in Cascade to browse.`n" -ForegroundColor Green
Exit 0
