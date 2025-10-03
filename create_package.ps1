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

# Copy the application
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Path "dist\Main.dist\*" -Destination $releaseFolder -Recurse

# Rename Main.exe to RustyBot.exe
if (Test-Path "$releaseFolder\Main.exe") {
    Rename-Item -Path "$releaseFolder\Main.exe" -NewName "RustyBot.exe"
    Write-Host "Renamed Main.exe to RustyBot.exe" -ForegroundColor Green
}

# Create README for users
Write-Host "Creating README..." -ForegroundColor Yellow
$readmeContent = @"
# RustyBot v1.3.9 - Twitch Giveaway Bot

## 🚀 Quick Start

1. **Run RustyBot.exe** - That's it!
2. The application will check for updates automatically
3. Configure your settings in the Options menu

## 📁 What's Included

- **RustyBot.exe** - Main application
- **All DLL files** - Required dependencies (PyQt6, Python runtime, etc.)
- **assets/** - Web animations and UI resources
- **sounds/** - Sound effects for notifications
- **Fonts/** - Custom fonts
- **config.json** - Configuration file
- **.env** - Twitch credentials (already configured)

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

### First Time Setup
The app is already configured with your Twitch credentials.
Just run RustyBot.exe and you're ready to go!

## 🔄 Updates

The app checks for updates automatically on startup.
When a new version is available, you'll see a notification.
Click "Download & Install" to update automatically!

## 📝 Configuration

All settings can be changed in the Options menu:
- Sound effects volume
- Animation speeds
- UI colors and themes
- Twitch connection settings

## 🐛 Troubleshooting

### "Application won't start"
- Make sure you extracted ALL files from the ZIP
- Don't move RustyBot.exe out of this folder (it needs the DLL files)
- Try running as Administrator

### "No sound"
- Check Options → Sound settings
- Verify your system volume isn't muted
- Make sure the sounds folder is present

### "Can't connect to Twitch"
- Check your internet connection
- Verify .env file has correct credentials
- Check Twitch API status

## 📞 Support

- GitHub Issues: https://github.com/nexis84/Rusty-Client/issues
- Documentation: https://github.com/nexis84/Rusty-Client

## 📜 Version

Version: 1.3.9
Build Date: $(Get-Date -Format "yyyy-MM-dd")
Build Type: Nuitka Standalone (Folder Distribution)

---

**Enjoy RustyBot!** 🎉
"@

$readmeContent | Out-File -FilePath "$releaseFolder\README.txt" -Encoding UTF8

# Create a simple launcher batch file as alternative
Write-Host "Creating launcher script..." -ForegroundColor Yellow
$launcherContent = @"
@echo off
echo Starting RustyBot...
echo.
start "" "%~dp0RustyBot.exe"
"@
$launcherContent | Out-File -FilePath "$releaseFolder\Start_RustyBot.bat" -Encoding ASCII

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
