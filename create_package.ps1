# RustyBot Package Creator
# Creates a distributable ZIP file from the Nuitka build

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot Package Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if dist folder exists
if (-not (Test-Path "dist\Main.dist")) {
    Write-Host "ERROR: Build folder not found!" -ForegroundColor Red
    Write-Host "Please run .\build_nuitka.ps1 first" -ForegroundColor Red
    exit 1
}

# Create release folder
Write-Host "Creating release package..." -ForegroundColor Yellow
$releaseName = "RustyBot_v1.3.9_Standalone"
$releaseFolder = "release\$releaseName"

if (Test-Path "release") {
    Remove-Item -Recurse -Force "release"
}
New-Item -ItemType Directory -Force -Path $releaseFolder | Out-Null

# Copy the application with organized structure
Write-Host "Copying and organizing application files..." -ForegroundColor Yellow

# Strategy: Keep everything Nuitka needs in an 'app' subfolder
# Put only the launcher and user files in root for clean appearance

# Create organized folder structure
$appFolder = "$releaseFolder\app"
New-Item -ItemType Directory -Force -Path $appFolder | Out-Null

# Copy everything from Nuitka build to app folder
Write-Host "Copying Nuitka build to app folder..." -ForegroundColor Yellow
Copy-Item -Path "dist\Main.dist\*" -Destination $appFolder -Recurse

# Rename Main.exe to RustyBot.exe in app folder
if (Test-Path "$appFolder\Main.exe") {
    Rename-Item -Path "$appFolder\Main.exe" -NewName "RustyBot.exe"
    Write-Host "Renamed Main.exe to RustyBot.exe" -ForegroundColor Green
}

# Copy user-editable files to root for easy access
Write-Host "Copying user files to root for easy access..." -ForegroundColor Yellow
Copy-Item -Path "$appFolder\config.json" -Destination $releaseFolder -ErrorAction SilentlyContinue
Copy-Item -Path "$appFolder\.env" -Destination $releaseFolder -ErrorAction SilentlyContinue

# Create shortcuts to user folders in root (optional)
# This keeps root clean while making assets accessible

# Create README for users
Write-Host "Creating README..." -ForegroundColor Yellow
$readmeContent = @"
# RustyBot v1.3.9 - Twitch Giveaway Bot

## 🚀 Quick Start

**Double-click `RustyBot.vbs`** - Launches RustyBot cleanly (no console window)

OR

**Double-click `RustyBot.bat`** - Launches RustyBot (shows brief console message)

## 📁 Folder Structure

### Root Folder (What you see)
- **RustyBot.vbs** - Main launcher (recommended - silent launch)
- **RustyBot.bat** - Alternative launcher (shows console briefly)
- **config.json** - Your settings (edit here)
- **.env** - Twitch credentials (edit here)
- **README.txt** - This file
- **app/** - Application files (all the messy stuff is here!)

### App Folder (Don't touch unless needed)
The `app` folder contains:
- RustyBot.exe - The actual application
- All Python libraries and dependencies
- All DLL files (277 files!)
- assets/, sounds/, Fonts/ folders

**💡 Tip**: You don't need to go into the app folder. Just use the launchers in the root!

## ⚙️ Configuration

**To change settings:**
1. Edit `config.json` in the root folder
2. Edit `.env` in the root folder for Twitch credentials
3. Restart RustyBot

The app will automatically read your settings from the root folder!

## ⚠️ Important Notes

### Antivirus Warning
Some antivirus software may flag this application. **This is a false positive!**

The application is completely safe:
- ✅ Open source: https://github.com/nexis84/Rusty-Client
- ✅ Built with Nuitka (Python compiler)
- ✅ No malicious code

**If Windows Defender blocks it:**
1. Click "More info" → "Run anyway"
2. Or add the folder to Windows Defender exclusions:
   - Open Windows Security
   - Virus & threat protection → Manage settings
   - Exclusions → Add or remove exclusions
   - Add this folder

### Keep Files Together
**DO NOT** move files out of their folders!
- Keep the `app` folder with the root folder
- Don't separate RustyBot.exe from its DLL files
- Extract the entire ZIP before running

## 🔄 Updates

The app checks for updates automatically on startup.
When a new version is available, you'll see a notification.
Click "Download & Install" to update automatically!

## 📝 Settings Files

Edit these files in the ROOT folder (not in app folder):

- **config.json** - Application settings
  - Sound volumes
  - Animation speeds
  - UI colors
  
- **.env** - Twitch connection
  - Your bot credentials
  - Channel names
  - API tokens

## 🐛 Troubleshooting

### "Application won't start"
- Make sure you extracted ALL files from the ZIP
- Don't move files between folders
- Try running as Administrator
- Use RustyBot.vbs instead of RustyBot.bat

### "Can't find config.json"
- Make sure config.json is in the ROOT folder (same level as the launchers)
- Don't move or rename it

### "Missing DLL" Error
- Make sure the `app` folder is present and hasn't been moved
- Re-extract the ZIP file if something is missing

### "No sound"
- Check config.json in root folder
- Verify your system volume isn't muted

### "Can't connect to Twitch"
- Edit .env in root folder
- Check your internet connection
- Verify Twitch credentials are correct

## 📞 Support

- GitHub Issues: https://github.com/nexis84/Rusty-Client/issues
- Documentation: https://github.com/nexis84/Rusty-Client

## 📜 Version

Version: 1.3.9
Build Date: $(Get-Date -Format "yyyy-MM-dd")
Build Type: Nuitka Standalone (Organized Structure)

**Root folder contains**: User files and launchers (clean!)
**App folder contains**: All technical files (organized!)

---

**Enjoy RustyBot!** 🎉
"@

$readmeContent | Out-File -FilePath "$releaseFolder\README.txt" -Encoding UTF8

# Create a launcher in root that runs the app from app folder
Write-Host "Creating launcher script..." -ForegroundColor Yellow
$launcherContent = @"
@echo off
REM RustyBot Launcher
REM This launches RustyBot from the app folder

echo Starting RustyBot...
echo.

REM Run RustyBot from app folder
cd /d "%~dp0app"
start "" "%~dp0app\RustyBot.exe"
cd /d "%~dp0"
"@
$launcherContent | Out-File -FilePath "$releaseFolder\RustyBot.bat" -Encoding ASCII

# Also create a direct EXE launcher using PowerShell
Write-Host "Creating RustyBot.vbs launcher (silent, no console)..." -ForegroundColor Yellow
$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run Chr(34) & WshShell.CurrentDirectory & "\app\RustyBot.exe" & Chr(34), 0
Set WshShell = Nothing
"@
$vbsContent | Out-File -FilePath "$releaseFolder\RustyBot.vbs" -Encoding ASCII

# Calculate folder size
$folderSize = (Get-ChildItem -Path $releaseFolder -Recurse | Measure-Object -Property Length -Sum).Sum
$folderSizeMB = [math]::Round($folderSize / 1MB, 2)

Write-Host ""
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = "release\$releaseName.zip"
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
Write-Host ""
Write-Host "Distribution Files:" -ForegroundColor Cyan
Write-Host "  📦 $releaseName.zip - Upload this to GitHub Releases" -ForegroundColor White
Write-Host "  📁 $releaseName\ - Test folder (optional)" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test the application from release\$releaseName\RustyBot.exe"
Write-Host "  2. Upload $releaseName.zip to GitHub Releases"
Write-Host "  3. Users extract the ZIP and run RustyBot.exe"
Write-Host ""
Write-Host "Tip: This folder-based distribution is much less likely" -ForegroundColor Green
Write-Host "     to trigger antivirus warnings than single-file EXEs!" -ForegroundColor Green
Write-Host ""
