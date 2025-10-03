@echo off
REM RustyBot GUI Installer Launcher
REM This script adds Windows Defender exclusion for the temp folder, then runs the installer

echo ========================================
echo   RustyBot GUI Installer
echo ========================================
echo.
echo This will launch the RustyBot installer with a beautiful GUI.
echo.
echo IMPORTANT: You'll see a UAC prompt requesting Administrator rights.
echo This is needed to:
echo   - Add Windows Defender exclusion
echo   - Install to system folders (if chosen)
echo.
echo Press any key to continue...
pause >nul

echo.
echo Adding Windows Defender exclusion for installer...
echo (You may see another UAC prompt)
echo.

REM Add exclusion for current folder (where Install.exe is extracted)
PowerShell -Command "Start-Process PowerShell -ArgumentList '-Command', 'Add-MpPreference -ExclusionPath \"$PWD\"' -Verb RunAs -Wait"

echo.
echo Launching installer...
echo.

REM Run the installer
start "" "%~dp0Install.exe"

echo.
echo Installer launched! If it doesn't appear, check for UAC prompts.
echo You can close this window.
echo.
pause
