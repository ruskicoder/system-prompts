@echo off
REM Windows CMD Batch Wrapper to launch prompt-orchestrator PowerShell master installer
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-all.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installation failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
