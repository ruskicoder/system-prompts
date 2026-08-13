# Install prompt-orchestrator to Antigravity (Agent & IDE) on Windows
$ErrorActionPreference = "Stop"

$OrchestratorDir = Resolve-Path "$PSScriptRoot\.."
$AgentDir = "$env:USERPROFILE\.gemini\antigravity"
$IdeDir = "$env:USERPROFILE\.gemini\antigravity-ide"

$Targets = @($AgentDir, $IdeDir)

foreach ($Target in $Targets) {
    Write-Host "==> Installing to $Target"
    New-Item -ItemType Directory -Force -Path "$Target\skills" | Out-Null
    New-Item -ItemType Directory -Force -Path "$Target\workflows" | Out-Null
    New-Item -ItemType Directory -Force -Path "$Target\steering" | Out-Null

    Copy-Item -Path "$OrchestratorDir\AGENT.md" -Destination "$Target\AGENTS.md" -Force
    Copy-Item -Path "$OrchestratorDir\skills\*" -Destination "$Target\skills\" -Recurse -Force
    Copy-Item -Path "$OrchestratorDir\workflows\*" -Destination "$Target\workflows\" -Recurse -Force
}

Write-Host "==> Done: installed to antigravity (agent) + antigravity-ide (IDE)"
