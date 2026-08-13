# Install prompt-orchestrator to OpenClaw on Windows
$ErrorActionPreference = "Stop"

$OrchestratorDir = Resolve-Path "$PSScriptRoot\.."
$TargetDir = "$env:USERPROFILE\.openclaw"

Write-Host "==> Installing prompt-orchestrator to OpenClaw at $TargetDir..."
New-Item -ItemType Directory -Force -Path "$TargetDir" | Out-Null

Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$TargetDir\AGENT.md" -Force
Copy-Item -Path "$OrchestratorDir\skills" -Destination "$TargetDir\" -Recurse -Force
Copy-Item -Path "$OrchestratorDir\workflows" -Destination "$TargetDir\" -Recurse -Force

Write-Host "==> OpenClaw installation complete."
