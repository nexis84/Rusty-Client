# Clean and Optimized Package Creator
# Removes unnecessary files and creates minimal distribution

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot Clean Package Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if dist folder exists
if (-not (Test-Path "dist\Main.dist")) {
    Write-Host "ERROR: Build folder not found!" -ForegroundColor Red
    Write-Host "Please run .\build_nuitka.ps1 first" -ForegroundColor Red
    exit 1
}

# Create release folder
Write-Host "Creating clean release package..." -ForegroundColor Yellow
$releaseName = "RustyBot_v1.6.6_Standalone"
$releaseFolder = "release\$releaseName"

# Try to remove old release (with retry logic for locked files)
if (Test-Path "release") {
    Write-Host "Removing old release folder..." -ForegroundColor Yellow
    try {
        Remove-Item -Recurse -Force "release" -ErrorAction Stop
        Write-Host "Old release removed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Some files are locked (RustyBot may be running)" -ForegroundColor Yellow
        Write-Host "Attempting to work around..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

New-Item -ItemType Directory -Force -Path $releaseFolder | Out-Null

# Create app folder
$appFolder = "$releaseFolder\app"
New-Item -ItemType Directory -Force -Path $appFolder | Out-Null

# Copy files with error handling
Write-Host "Copying application files..." -ForegroundColor Yellow

# Copy the main executable
Copy-Item "dist\RustyBot.exe" -Destination $appFolder -ErrorAction Stop
Write-Host "Copied RustyBot.exe" -ForegroundColor Green

# PyInstaller bundles everything into the exe, so no additional files to copy
$copiedFiles = 1
$skippedFiles = 0

Write-Host "Copied: $copiedFiles files, Skipped (locked): $skippedFiles files" -ForegroundColor Gray

# Copy essential files only to root
Write-Host "Copying essential configuration files..." -ForegroundColor Yellow
try { Copy-Item -Path "$appFolder\config.json" -Destination $releaseFolder -ErrorAction SilentlyContinue } catch {}
try { Copy-Item -Path "$appFolder\secure.env" -Destination $releaseFolder -ErrorAction SilentlyContinue } catch {}

# Create README
Write-Host "Creating documentation..." -ForegroundColor Yellow
$readmeContent = @"
# RustyBot v1.6.6 - Twitch Giveaway Bot

## 🚀 QUICKEST START

**Double-click `Run_Installer.bat`** - That's it! The easiest way to install.

OR use `Install.bat` for console-based installation.

---

## 📝 What's Included

- **Run_Installer.bat** ⭐ - Easiest way to install (launches GUI)
- **Install.exe** - Beautiful GUI installer (run via Run_Installer.bat)
- **Install.bat** - Console-based installer (alternative)
- **Install.ps1** - PowerShell installer script
- **README.txt** - This file
- **READ_FIRST.txt** - Important Windows Defender info
- **INSTALLER_TROUBLESHOOTING.md** - If you have issues
- **WINDOWS_DEFENDER_INSTRUCTIONS.md** - Detailed security info
- **RustyBot.vbs** - Main launcher (silent)
- **RustyBot.bat** - Alternative launcher (shows console)
- **config.json** - Your settings
- **secure.env** - Encrypted credentials (included, ready to use!)
- **app/** - Application files

---

## ⚠️ IMPORTANT: Windows Defender

Windows Defender will flag this as suspicious. This is a FALSE POSITIVE.

**Solution:** Use `Run_Installer.bat` - it handles everything automatically!

See READ_FIRST.txt for details.

---

## 🎯 First Time Setup

1. Run the installer (Run_Installer.bat recommended)
2. Launch RustyBot (desktop shortcut or RustyBot.vbs)
3. Enter your Twitch channel name when prompted
4. Done! Bot is ready to use

---

## 📚 Full Documentation

GitHub: https://github.com/nexis84/Rusty-Client

Version: 1.6.6
Build Date: $(Get-Date -Format "yyyy-MM-dd")
"@

$readmeContent | Out-File -FilePath "$releaseFolder\README.txt" -Encoding UTF8

# Copy documentation files
Write-Host "Copying installer and documentation..." -ForegroundColor Yellow
Copy-Item "READ_FIRST.txt" -Destination "$releaseFolder\READ_FIRST.txt" -ErrorAction SilentlyContinue
Copy-Item "WINDOWS_DEFENDER_INSTRUCTIONS.md" -Destination "$releaseFolder\WINDOWS_DEFENDER_INSTRUCTIONS.md" -ErrorAction SilentlyContinue
Copy-Item "INSTALLER_TROUBLESHOOTING.md" -Destination "$releaseFolder\INSTALLER_TROUBLESHOOTING.md" -ErrorAction SilentlyContinue

# Copy installer files
Write-Host "Copying installer scripts..." -ForegroundColor Yellow
Copy-Item "Install.ps1" -Destination "$releaseFolder\Install.ps1" -ErrorAction SilentlyContinue
Copy-Item "Install.bat" -Destination "$releaseFolder\Install.bat" -ErrorAction SilentlyContinue
Copy-Item "Run_Installer.bat" -Destination "$releaseFolder\Run_Installer.bat" -ErrorAction SilentlyContinue

# Copy GUI installer if it exists
if (Test-Path "installer_build\Install.exe") {
    Write-Host "Copying GUI installer..." -ForegroundColor Yellow
    Copy-Item "installer_build\Install.exe" -Destination "$releaseFolder\Install.exe" -ErrorAction SilentlyContinue
}

# Create launchers
Write-Host "Creating launchers..." -ForegroundColor Yellow

$launcherContent = @"
@echo off
REM RustyBot Launcher
echo Starting RustyBot...
cd /d "%~dp0app"
start "" "%~dp0app\RustyBot.exe"
cd /d "%~dp0"
"@
$launcherContent | Out-File -FilePath "$releaseFolder\RustyBot.bat" -Encoding ASCII

$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run Chr(34) & WshShell.CurrentDirectory & "\app\RustyBot.exe" & Chr(34), 0
Set WshShell = Nothing
"@
$vbsContent | Out-File -FilePath "$releaseFolder\RustyBot.vbs" -Encoding ASCII

# Calculate sizes
$folderSize = (Get-ChildItem -Path $releaseFolder -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
$folderSizeMB = [math]::Round($folderSize / 1MB, 2)

# Create ZIP
Write-Host ""
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = "release\$releaseName.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}
Compress-Archive -Path $releaseFolder -DestinationPath $zipPath -Force

$zipSize = (Get-Item $zipPath).Length
$zipSizeMB = [math]::Round($zipSize / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Package Created Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package Details:" -ForegroundColor Cyan
Write-Host "  - Folder size: $folderSizeMB MB" -ForegroundColor White
Write-Host "  - ZIP size: $zipSizeMB MB" -ForegroundColor White
Write-Host "  - Location: $zipPath" -ForegroundColor White
Write-Host "  - Copied: $copiedFiles files" -ForegroundColor White
if ($skippedFiles -gt 0) {
    Write-Host "  - Skipped (locked): $skippedFiles files" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Distribution Files:" -ForegroundColor Cyan
Write-Host "  Package: $releaseName.zip - Upload to GitHub Releases" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Close any running RustyBot instances" -ForegroundColor White
Write-Host "  2. Test installer: .\release\$releaseName\Run_Installer.bat" -ForegroundColor White
Write-Host "  3. Upload ZIP to GitHub Releases" -ForegroundColor White
Write-Host ""
