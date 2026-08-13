# Install prompt-orchestrator to Cursor rules on Windows
$ErrorActionPreference = "Stop"

$OrchestratorDir = Resolve-Path "$PSScriptRoot\.."
$TargetDir = "$env:USERPROFILE\.cursor\rules"

Write-Host "==> Installing prompt-orchestrator to Cursor ($TargetDir)"
New-Item -ItemType Directory -Force -Path "$TargetDir" | Out-Null

Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$TargetDir\AGENT.md" -Force
Copy-Item -Path "$OrchestratorDir\skills" -Destination "$TargetDir\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\workflows" -Destination "$TargetDir\" -Recurse -Force

Write-Host "==> Done: installed to Cursor rules"
