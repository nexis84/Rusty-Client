@echo off
REM RustyBot Firewall Configuration Script
REM Run as Administrator to add Windows Firewall exceptions for RustyBot

title RustyBot Firewall Configuration

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ERROR: This script requires Administrator privileges to modify Windows Firewall rules.
    echo Please right-click and select "Run as administrator" and try again.
    echo.
    pause
    exit /b 1
)

echo RustyBot Firewall Configuration
echo ===============================
echo.

REM Get the directory where this script is located (should be the RustyBot installation directory)
set "INSTALL_DIR=%~dp0"
set "RUSTYBOT_PATH=%INSTALL_DIR%RustyBot.exe"

echo Install Directory: %INSTALL_DIR%
echo.

REM Check if executable exists
if not exist "%RUSTYBOT_PATH%" (
    echo WARNING: RustyBot.exe not found at: %RUSTYBOT_PATH%
    echo Please ensure this script is in the RustyBot installation directory.
    echo.
    pause
    exit /b 1
)

echo Adding Windows Firewall exceptions for RustyBot...
echo.

REM Add firewall rules for RustyBot.exe
echo Adding rules for RustyBot.exe...
netsh advfirewall firewall add rule name="RustyBot (Inbound)" dir=in action=allow program="%RUSTYBOT_PATH%" >nul 2>&1
if %errorLevel% equ 0 (
    echo   ^> Inbound rule added successfully
) else (
    echo   ^> Error adding inbound rule
)

netsh advfirewall firewall add rule name="RustyBot (Outbound)" dir=out action=allow program="%RUSTYBOT_PATH%" >nul 2>&1
if %errorLevel% equ 0 (
    echo   ^> Outbound rule added successfully
) else (
    echo   ^> Error adding outbound rule
)

echo.
echo Windows Firewall exceptions have been configured for RustyBot!
echo.
echo You can now run RustyBot without Windows Firewall blocking network connections.
echo.
pause