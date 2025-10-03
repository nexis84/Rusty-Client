@echo off
REM Add Windows Defender Exclusion - Auto-elevate to Administrator

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges...
    echo.
    goto :run_script
) else (
    echo Requesting Administrator privileges...
    echo.
    goto :elevate
)

:elevate
REM Re-launch as administrator
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:run_script
REM Run the PowerShell script
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0add_defender_exclusion.ps1"
echo.
echo.
pause
exit /b
