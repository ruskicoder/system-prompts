# Install prompt-orchestrator to Gemini CLI on Windows
$ErrorActionPreference = "Stop"

$OrchestratorDir = Resolve-Path "$PSScriptRoot\.."
$TargetDir = "$env:USERPROFILE\.gemini"

Write-Host "==> Installing prompt-orchestrator to Gemini CLI ($TargetDir)"
New-Item -ItemType Directory -Force -Path "$TargetDir\skills" | Out-Null
New-Item -ItemType Directory -Force -Path "$TargetDir\workflows" | Out-Null

Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$TargetDir\GEMINI.md" -Force
Copy-Item -Path "$OrchestratorDir\skills\*" -Destination "$TargetDir\skills\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\workflows\*" -Destination "$TargetDir\workflows\" -Recurse -Force

$SkillCount = (Get-ChildItem -Path "$OrchestratorDir\skills\*.md").Count
$WorkflowCount = (Get-ChildItem -Path "$OrchestratorDir\workflows\*.md").Count

Write-Host "==> Done: GEMINI.md, $SkillCount skills, $WorkflowCount workflows"
