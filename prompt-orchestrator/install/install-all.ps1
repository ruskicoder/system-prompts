# install-all.ps1 - Master Installer Suite (global-scope installers)
$ErrorActionPreference = "Continue"

if (-not $PSScriptRoot) {
    Write-Error "Critical Framework Fault: Execution runtime environment missing local system path tracking context."
    Exit 1
}

$ScriptFolder = $PSScriptRoot
$OrchestratorDir = [System.IO.Path]::GetFullPath((Join-Path -Path $ScriptFolder -ChildPath ".."))

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Prompt Orchestrator Windows Setup Environment       " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Regenerate derived integration files if Python + PyYAML are available.
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($PythonCmd) {
    & $PythonCmd.Source -c "import yaml" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n--- Regenerating integrations (tools\generate_integrations.py) ---" -ForegroundColor Yellow
        & $PythonCmd.Source (Join-Path -Path $OrchestratorDir -ChildPath "tools\generate_integrations.py")
    }
}

# Global-scope installers only. install-project.ps1 and install-windsurf.ps1
# target a specific project directory and are run separately:
#   powershell install\install-project.ps1 -TargetDir C:\path\to\project
$TargetsMap = [ordered]@{
    "Claude / Claude Code"      = "install-claude.ps1"
    "Antigravity (Agent & IDE)" = "install-antigravity.ps1"
    "Gemini CLI"                = "install-gemini.ps1"
    "Codex"                     = "install-codex.ps1"
    "Cursor"                    = "install-cursor.ps1"
    "OpenClaw"                  = "install-openclaw.ps1"
    "OpenCode"                  = "install-opencode.ps1"
}

# Pre-flight Check: Structural Audit Validation
foreach ($Script in $TargetsMap.Values) {
    $FullPath = Join-Path -Path $ScriptFolder -ChildPath $Script
    if (-not (Test-Path -Path $FullPath)) {
        Write-Error "Deployment Component Footprint Missing -> $FullPath"
        Exit 1
    }
}

$ResultsTable = [ordered]@{}
$GlobalFailureFlag = $false

foreach ($Platform in $TargetsMap.Keys) {
    $ScriptName = $TargetsMap[$Platform]
    $ScriptPath = Join-Path -Path $ScriptFolder -ChildPath $ScriptName

    Write-Host "`n==> Thread Launching: Target $Platform ($ScriptName)" -ForegroundColor Yellow

    try {
        $Process = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`"" -NoNewWindow -PassThru -Wait

        if ($Process.ExitCode -eq 0) {
            Write-Host "   Status: Platform link sequence verified successfully." -ForegroundColor Green
            $ResultsTable[$Platform] = "SUCCESS"
        } else {
            Write-Error "   Status Component Failure: Script '$ScriptName' returned exit code [$($Process.ExitCode)]"
            $ResultsTable[$Platform] = "FAILED (Code $($Process.ExitCode))"
            $GlobalFailureFlag = $true
        }
    }
    catch {
        Write-Error "   Status System Engine Exception caught while configuring platform payload target '$Platform': $_"
        $ResultsTable[$Platform] = "CRASHED"
        $GlobalFailureFlag = $true
    }
}

Write-Host "`n====================================================" -ForegroundColor Cyan
Write-Host " WINDOWS DEPLOYMENT TRANSACTION SUMMARY             " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

foreach ($Platform in $ResultsTable.Keys) {
    $Status = $ResultsTable[$Platform]
    if ($Status -eq "SUCCESS") {
        Write-Host ("{0,-32} : {1}" -f $Platform, $Status) -ForegroundColor Green
    } else {
        Write-Host ("{0,-32} : {1}" -f $Platform, $Status) -ForegroundColor Red
    }
}

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "`nTo also install into a specific project (Cursor/OpenCode/Windsurf project scope), run:" -ForegroundColor Gray
Write-Host "    powershell install\install-project.ps1 -TargetDir C:\path\to\project" -ForegroundColor Gray
Write-Host "    powershell install\install-windsurf.ps1 -TargetDir C:\path\to\project" -ForegroundColor Gray

if ($GlobalFailureFlag) {
    Write-Host "`n[FATAL] Deployment reported failures. Review log output above." -ForegroundColor Red
    Exit 1
} else {
    Write-Host "`n[SUCCESS] Systems target update tracking initialized fully across all targets." -ForegroundColor Green
    Exit 0
}
