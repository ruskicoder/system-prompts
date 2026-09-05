# install-project.ps1 - Universal single-project installer
# Copies every generated integration into a target project so it is
# immediately usable by Claude Code, Codex, Cursor, OpenCode, Gemini CLI,
# Antigravity, Windsurf, and any AGENTS.md / Agent-Skills-compliant tool.
param(
    [string]$TargetDir = (Get-Location).Path
)
$ErrorActionPreference = "Stop"

if (-not $PSScriptRoot) {
    Throw "PSScriptRoot is undefined."
}
$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath ".."))

if (-not (Test-Path -Path $TargetDir)) {
    Throw "Target project directory does not exist: $TargetDir`nUsage: powershell install\install-project.ps1 -TargetDir C:\path\to\project"
}
$TargetDir = [System.IO.Path]::GetFullPath($TargetDir)

if ($TargetDir -eq $OrchestratorDir) {
    Write-Host "==> Target is the prompt-orchestrator repo itself; nothing to copy." -ForegroundColor Yellow
    Exit 0
}

Write-Host "==> Installing prompt-orchestrator into project: $TargetDir" -ForegroundColor Cyan

$DotDirs = @(".agents", ".claude", ".claude-plugin", ".codex", ".cursor", ".gemini", ".opencode", ".windsurf")
$RootFiles = @("AGENTS.md", "AGENT.md", "CLAUDE.md", "INTEGRATIONS.md")
$ContentDirs = @("skills", "workflows")

foreach ($d in $DotDirs) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $d
    if (Test-Path -Path $SourcePath) {
        $DestPath = Join-Path -Path $TargetDir -ChildPath $d
        New-Item -ItemType Directory -Force -Path $DestPath | Out-Null
        Copy-Item -Path "$SourcePath\*" -Destination $DestPath -Recurse -Force
        Write-Host "   [OK] $d\" -ForegroundColor Green
    }
}

foreach ($f in $RootFiles) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $f
    if (Test-Path -Path $SourcePath) {
        Copy-Item -Path $SourcePath -Destination (Join-Path -Path $TargetDir -ChildPath $f) -Force
        Write-Host "   [OK] $f" -ForegroundColor Green
    }
}

foreach ($d in $ContentDirs) {
    $SourcePath = Join-Path -Path $OrchestratorDir -ChildPath $d
    if (Test-Path -Path $SourcePath) {
        $DestPath = Join-Path -Path $TargetDir -ChildPath $d
        New-Item -ItemType Directory -Force -Path $DestPath | Out-Null
        Copy-Item -Path "$SourcePath\*" -Destination $DestPath -Recurse -Force
        Write-Host "   [OK] $d\ (canonical source)" -ForegroundColor Green
    }
}

Write-Host "`n[SUCCESS] $TargetDir now works with Claude, Codex, Cursor, OpenCode, Gemini CLI, Antigravity, and Windsurf.`n" -ForegroundColor Green
Exit 0
