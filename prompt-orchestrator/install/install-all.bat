@echo off
REM install-all.bat - Wrapper for Windows Prompt Orchestrator Setup
setlocal enabledelayedexpansion

title Prompt Orchestrator Installer Engine

echo ====================================================
echo  Launching Script Engine via PowerShell Pipeline...
echo ====================================================

cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-all.ps1"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if %EXIT_CODE% NEQ 0 (
    echo [ERROR] Setup pipeline reported runtime failures.
) else (
    echo [SUCCESS] Task sequence lifecycle fully verified.
)

echo %CMDCMDLINE% | findstr /i /c:"/c" >nul
if %ERRORLEVEL% EQ 0 (
    echo.
    echo Script execution context generated via Explorer loop. Holding active session window.
    pause
)

exit /b %EXIT_CODE%
