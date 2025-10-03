@echo off
REM RustyBot Installer Launcher
REM This will auto-elevate to Administrator and run the PowerShell installer

echo ========================================
echo   RustyBot Installer
echo ========================================
echo.
echo This will install RustyBot on your computer.
echo.
echo The installer will:
echo   - Ask where to install RustyBot
echo   - Add Windows Defender exclusion (prevents false positive)
echo   - Extract all files
echo   - Create a desktop shortcut
echo.
echo Press any key to start installation...
pause >nul

REM Run PowerShell installer
powershell -ExecutionPolicy Bypass -File "%~dp0Install.ps1"

exit
