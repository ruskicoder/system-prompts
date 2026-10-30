# install-tui.ps1 - native installer menu for Windows when Python 3 is not available.
#
# Installs the core per-tool scripts and the harness's pre-rendered agents and overlay from
# harness\dist. Hooks, the status line, plan modes and the gates run Python 3.11+, so this path
# installs agents and instructions only.
#   powershell -File install\install-tui.ps1
#   powershell -File install\install-tui.ps1 -Yes [-Core] [-HarnessOnly] [-Tools claude,codex]
#   powershell -File install\install-tui.ps1 -UninstallHarness
param(
    [switch]$Core,
    [switch]$HarnessOnly,
    [switch]$Yes,
    [switch]$UninstallHarness,
    [string[]]$Tools,
    [string]$ProfileClaude = "claude-pro"
)
$ErrorActionPreference = "Stop"
$ScriptFolder = $PSScriptRoot
$Root = [System.IO.Path]::GetFullPath((Join-Path $ScriptFolder ".."))
$Dist = Join-Path $Root "harness\dist"
$Overlay = Join-Path $Root "harness\HARNESS.md"
$Marker = "prompt-orchestrator-harness"
$AllTools = @("claude", "codex", "opencode", "cursor", "gemini", "antigravity", "openclaw", "copilot", "kiro")
$CoreTools = @("claude", "codex", "opencode", "cursor", "gemini", "antigravity", "openclaw")
$Selected = if ($Tools) { @($Tools | ForEach-Object { $_ -split "," } | Where-Object { $_ }) } else { @($CoreTools) }
$DoCore = -not $HarnessOnly
$DoHarness = -not $Core
$Home_ = $env:USERPROFILE
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $Home_ ".codex" }

function Get-AgentDir($Tool) {
    switch ($Tool) {
        "claude" { Join-Path $Home_ ".claude\agents" }
        "codex" { Join-Path $CodexHome "agents" }
        "opencode" { Join-Path $Home_ ".config\opencode\agents" }
        "cursor" { Join-Path $Home_ ".cursor\agents" }
        "copilot" { Join-Path $Home_ ".copilot\agents" }
        "gemini" { Join-Path $Home_ ".gemini\agents" }
        "antigravity" { Join-Path $Home_ ".gemini\config\agents" }
        "kiro" { Join-Path $Home_ ".kiro\agents" }
        default { $null }
    }
}

function Get-OverlayFile($Tool) {
    switch ($Tool) {
        "claude" { Join-Path $Home_ ".claude\CLAUDE.md" }
        "codex" { Join-Path $CodexHome "AGENTS.md" }
        "opencode" { Join-Path $Home_ ".config\opencode\AGENTS.md" }
        "gemini" { Join-Path $Home_ ".gemini\GEMINI.md" }
        default { $null }
    }
}

function Get-ProfileFor($Tool) {
    switch ($Tool) {
        { $_ -in @("claude", "opencode") } { $ProfileClaude }
        "codex" { "codex-plus" }
        default { "generic" }
    }
}

function Remove-Block($Path) {
    if (-not (Test-Path $Path)) { return }
    $Text = Get-Content -Raw -Path $Path
    $Pattern = "(?s)\r?\n?<!-- $($Marker):start -->.*?<!-- $($Marker):end -->\r?\n?"
    Set-Content -Path $Path -Value ([regex]::Replace($Text, $Pattern, "`n")) -NoNewline
}

function Add-Block($Path, $Content) {
    Remove-Block $Path
    New-Item -ItemType Directory -Force -Path (Split-Path $Path) | Out-Null
    Add-Content -Path $Path -Value "`n<!-- $($Marker):start -->`n$Content`n<!-- $($Marker):end -->"
}

function Copy-Marked($Src, $Dest) {
    if ((Test-Path $Dest) -and -not (Select-String -Path $Dest -Pattern $Marker -Quiet)) {
        Write-Host "  skipped $Dest : exists without the harness marker" -ForegroundColor Yellow
        return
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $Dest) | Out-Null
    Copy-Item -Path $Src -Destination $Dest -Force
}

function Install-HarnessNative($Tool) {
    $ProfileName = Get-ProfileFor $Tool
    $Src = Join-Path $Dist "$Tool\$ProfileName\agents"
    $Dest = Get-AgentDir $Tool
    if ($Dest -and (Test-Path $Src)) {
        Get-ChildItem -Path $Src -File | ForEach-Object { Copy-Marked $_.FullName (Join-Path $Dest $_.Name) }
        Write-Host "  agents ($ProfileName) -> $Dest"
    }
    $OverlayText = Get-Content -Raw -Path $Overlay
    switch ($Tool) {
        "claude" {
            Set-Content -Path (Join-Path $Home_ ".claude\HARNESS.md") -Value "<!-- $Marker -->`n$OverlayText"
            Add-Block (Get-OverlayFile "claude") "@HARNESS.md"
            Copy-Marked (Join-Path $Dist "skills\autosetup\SKILL.md") (Join-Path $Home_ ".claude\skills\autosetup\SKILL.md")
            $Wf = Join-Path $Home_ ".claude\workflows"
            New-Item -ItemType Directory -Force -Path $Wf | Out-Null
            Get-ChildItem -Path (Join-Path $Root "harness\workflows") -Filter *.js | ForEach-Object {
                Set-Content -Path (Join-Path $Wf $_.Name) -Value ("// $Marker`n" + (Get-Content -Raw $_.FullName))
            }
        }
        "cursor" {
            $Rule = Join-Path $Home_ ".cursor\rules\prompt-orchestrator-harness.mdc"
            New-Item -ItemType Directory -Force -Path (Split-Path $Rule) | Out-Null
            Set-Content -Path $Rule -Value "---`ndescription: prompt-orchestrator harness overlay`nalwaysApply: true`n---`n<!-- $Marker -->`n$OverlayText"
        }
        "kiro" {
            $Steer = Join-Path $Home_ ".kiro\steering\prompt-orchestrator-harness.md"
            New-Item -ItemType Directory -Force -Path (Split-Path $Steer) | Out-Null
            Set-Content -Path $Steer -Value "<!-- $Marker -->`n$OverlayText"
        }
        default {
            $File = Get-OverlayFile $Tool
            if ($File) { Add-Block $File $OverlayText }
        }
    }
}

function Uninstall-HarnessNative {
    foreach ($Tool in $Selected) {
        $Dest = Get-AgentDir $Tool
        if ($Dest -and (Test-Path $Dest)) {
            Get-ChildItem -Path $Dest -File | Where-Object { Select-String -Path $_.FullName -Pattern $Marker -Quiet } | Remove-Item
        }
        $File = Get-OverlayFile $Tool
        if ($File) { Remove-Block $File }
        Write-Host "  $Tool : harness files removed"
    }
    foreach ($Path in @(".claude\HARNESS.md", ".cursor\rules\prompt-orchestrator-harness.mdc", ".kiro\steering\prompt-orchestrator-harness.md", ".claude\skills\autosetup")) {
        $Full = Join-Path $Home_ $Path
        if (Test-Path $Full) { Remove-Item -Recurse -Force $Full }
    }
}

function Show-Menu {
    while ($true) {
        Write-Host "`nprompt-orchestrator installer (native)" -ForegroundColor Cyan
        Write-Host "  [c] core skills and workflows: $(if ($script:DoCore) { 'yes' } else { 'no' })"
        Write-Host "  [h] harness agents and overlay: $(if ($script:DoHarness) { 'yes' } else { 'no' })"
        Write-Host "      (hooks, status line, plan modes and gates need Python 3.11+)"
        Write-Host "  [p] Claude plan profile: $script:ProfileClaude"
        for ($i = 0; $i -lt $AllTools.Count; $i++) {
            $Mark = if ($script:Selected -contains $AllTools[$i]) { "x" } else { " " }
            Write-Host "   $($i + 1). [$Mark] $($AllTools[$i])"
        }
        $Choice = Read-Host "Number toggles a tool, a = all, n = none, Enter = install, q = quit"
        switch -Regex ($Choice) {
            "^$" { return $true }
            "^q$" { return $false }
            "^a$" { $script:Selected = @($AllTools) }
            "^n$" { $script:Selected = @() }
            "^c$" { $script:DoCore = -not $script:DoCore }
            "^h$" { $script:DoHarness = -not $script:DoHarness }
            "^p$" {
                $Order = @("claude-pro", "claude-max", "api", "free")
                $script:ProfileClaude = $Order[($Order.IndexOf($script:ProfileClaude) + 1) % $Order.Count]
            }
            "^\d+$" {
                $Index = [int]$Choice - 1
                if ($Index -ge 0 -and $Index -lt $AllTools.Count) {
                    $Tool = $AllTools[$Index]
                    if ($script:Selected -contains $Tool) { $script:Selected = @($script:Selected | Where-Object { $_ -ne $Tool }) }
                    else { $script:Selected += $Tool }
                }
            }
            default { Write-Host "  unknown choice" }
        }
    }
}

if ($UninstallHarness) { Uninstall-HarnessNative; exit 0 }
if (-not $Yes -and [Environment]::UserInteractive -and -not [Console]::IsInputRedirected) {
    if (-not (Show-Menu)) { Write-Host "cancelled"; exit 1 }
}

$Failed = @()
foreach ($Tool in $Selected) {
    Write-Host "`n=== $Tool" -ForegroundColor Yellow
    if ($DoCore -and ($CoreTools -contains $Tool)) {
        $Script = Join-Path $ScriptFolder "install-$Tool.ps1"
        $Process = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$Script`"" -NoNewWindow -PassThru -Wait
        if ($Process.ExitCode -ne 0) { $Failed += $Tool; continue }
    }
    if ($DoHarness) { Install-HarnessNative $Tool }
}
if ($Failed.Count -gt 0) { Write-Host "`n==> finished with failures: $($Failed -join ', ')" -ForegroundColor Red; exit 1 }
Write-Host "`n==> done. Install Python 3.11+ and run install-harness.ps1 to add hooks, the status line and plan modes." -ForegroundColor Green
exit 0
