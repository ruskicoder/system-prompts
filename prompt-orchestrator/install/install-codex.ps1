# Install prompt-orchestrator to Codex on Windows
$ErrorActionPreference = "Stop"

$OrchestratorDir = Resolve-Path "$PSScriptRoot\.."
$TargetDir = "$env:USERPROFILE\.codex"

Write-Host "==> Installing prompt-orchestrator to Codex ($TargetDir)"
New-Item -ItemType Directory -Force -Path "$TargetDir\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$TargetDir\workflows" | Out-Null
New-Item -ItemType Directory -Force -Path "$TargetDir\steering" | Out-Null

Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$TargetDir\AGENTS.md" -Force
Copy-Item -Path "$OrchestratorDir\skills\*" -Destination "$TargetDir\skills\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\workflows\*" -Destination "$TargetDir\workflows\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\.kiro\*" -Destination "$TargetDir\steering\" -Recurse -Force

$SkillCount = (Get-ChildItem -Path "$OrchestratorDir\skills\*.md").Count
$WorkflowCount = (Get-ChildItem -Path "$OrchestratorDir\workflows\*.md").Count

Write-Host "==> Done: AGENTS.md, $SkillCount skills, $WorkflowCount workflows, steering config"
