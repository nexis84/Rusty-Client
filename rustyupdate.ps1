# RustyBot Complete Update Build Script
# This script rebuilds everything for a new version release
# Usage: .\rustyupdatefiles.ps1 -Version "1.6.8"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"

Write-Host @"

═══════════════════════════════════════════════════════
   RustyBot Complete Update Build Script
   Building Version: $Version
═══════════════════════════════════════════════════════

"@ -ForegroundColor Cyan

# Step 1: Update version numbers in all files
Write-Host "`n[1/6] Updating version numbers..." -ForegroundColor Yellow

# Update Main.py
if (Test-Path "Main.py") {
    $content = Get-Content "Main.py" -Raw
    $content = $content -replace 'APP_VERSION = "[^"]*"', "APP_VERSION = `"$Version`""
    Set-Content "Main.py" -Value $content -NoNewline
    Write-Host "  + Updated Main.py" -ForegroundColor Green
}

# Update auto_updater.py
if (Test-Path "auto_updater.py") {
    $content = Get-Content "auto_updater.py" -Raw
    $content = $content -replace 'CURRENT_VERSION = "[^"]*"', "CURRENT_VERSION = `"$Version`""
    Set-Content "auto_updater.py" -Value $content -NoNewline
    Write-Host "  + Updated auto_updater.py" -ForegroundColor Green
}

# Update installer_improved.iss
if (Test-Path "installer_improved.iss") {
    $content = Get-Content "installer_improved.iss" -Raw
    $content = $content -replace '#define MyAppVersion "[^"]*"', "#define MyAppVersion `"$Version.0`""
    Set-Content "installer_improved.iss" -Value $content -NoNewline
    Write-Host "  + Updated installer_improved.iss" -ForegroundColor Green
}

# Step 2: Clean previous builds
Write-Host "`n[2/6] Cleaning previous builds..." -ForegroundColor Yellow
$cleanDirs = @("build", "dist", "github upload\RustyBot_v${Version}_Standalone")
$cleanFiles = @("github upload\RustyBot_v${Version}_Standalone.zip", "github upload\RustyBot_Setup_v${Version}.0.exe")

foreach ($dir in $cleanDirs) {
    if (Test-Path $dir) {
        Remove-Item $dir -Recurse -Force
        Write-Host "  + Cleaned $dir" -ForegroundColor Green
    }
}

foreach ($file in $cleanFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  + Removed $file" -ForegroundColor Green
    }
}

# Step 3: Build main RustyBot executable
Write-Host "`n[3/6] Building RustyBot.exe..." -ForegroundColor Yellow
pyinstaller --clean --noconfirm RustyBot.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "  X RustyBot build failed!" -ForegroundColor Red
    exit 1
}
$rustySize = (Get-Item "dist\RustyBot.exe").Length / 1MB
$rustySizeRounded = [math]::Round($rustySize, 2)
Write-Host "  + RustyBot.exe built successfully ($rustySizeRounded MB)" -ForegroundColor Green

# Step 4: Create standalone ZIP package (no launcher needed)
Write-Host "`n[4/6] Creating standalone ZIP package..." -ForegroundColor Yellow
$outputPath = "github upload\RustyBot_v${Version}_Standalone"
New-Item -ItemType Directory -Path $outputPath -Force | Out-Null

# Copy all files from dist folder
Write-Host "  > Copying dist folder contents..." -ForegroundColor Gray
Copy-Item "dist\*" "$outputPath\" -Recurse -Force

# Clean up old unused files from the package
Write-Host "  > Removing old unused files..." -ForegroundColor Gray
$oldFiles = @(
    "$outputPath\Launcher.exe",
    "$outputPath\Main.exe",
    "$outputPath\RustyBot_Web_Updater.exe",
    "$outputPath\simple_launcher.py",
    "$outputPath\launcher.py",
    "$outputPath\transition_launcher.py"
)
foreach ($file in $oldFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "    - Removed $(Split-Path $file -Leaf)" -ForegroundColor DarkGray
    }
}

Write-Host "  + Package folder created" -ForegroundColor Green

# Create ZIP
Write-Host "  > Compressing to ZIP..." -ForegroundColor Gray
Compress-Archive -Path "$outputPath\*" -DestinationPath "github upload\RustyBot_v${Version}_Standalone.zip" -CompressionLevel Optimal -Force
$zipSize = (Get-Item "github upload\RustyBot_v${Version}_Standalone.zip").Length / 1MB
$zipSizeRounded = [math]::Round($zipSize, 2)
Write-Host "  + ZIP created ($zipSizeRounded MB)" -ForegroundColor Green

# Step 5: Build professional installer
Write-Host "`n[5/6] Building professional installer..." -ForegroundColor Yellow
$innoSetupPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (Test-Path $innoSetupPath) {
    & $innoSetupPath "installer_improved.iss" /Q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  X Installer build failed!" -ForegroundColor Red
        exit 1
    }
    
    # Copy to github upload folder
    Copy-Item "installer_output\RustyBot_Setup_v${Version}.0.exe" "github upload\RustyBot_Setup_v${Version}.0.exe" -Force
    $installerSize = (Get-Item "github upload\RustyBot_Setup_v${Version}.0.exe").Length / 1MB
    $installerSizeRounded = [math]::Round($installerSize, 2)
    Write-Host "  + Installer created ($installerSizeRounded MB)" -ForegroundColor Green
} else {
    Write-Host "  X Inno Setup not found at $innoSetupPath" -ForegroundColor Red
    Write-Host "    Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    exit 1
}

# Step 6: Create/Update release notes
Write-Host "`n[6/6] Creating release notes..." -ForegroundColor Yellow
$releaseNotes = @"
# RustyBot v$Version Release Notes

## 🎉 What's New in v$Version

### Features & Improvements
- [Add your feature list here]

### Bug Fixes
- [Add bug fixes here]

### Technical Updates
- Updated to version $Version
- Built with PyInstaller 6.15.0
- Python 3.12.7

## 📦 Installation Options

### 1. Professional Installer (Recommended)
**RustyBot_Setup_v${Version}.0.exe**
- Automatic Windows Defender configuration
- Desktop shortcuts and Start Menu entries
- Clean uninstallation support

### 2. Standalone ZIP Package
**RustyBot_v${Version}_Standalone.zip**
- Portable - run from any location
- Manual update checking available in options dialog
- Manual setup required

## 🚀 Components Included

Both packages include:
- **RustyBot.exe v$Version** - Main application with manual update checking
- Configuration files (config.json, secure.env, qt.conf)
- Assets (animations, sounds, fonts)
- Documentation (README.md, SECURE_CREDENTIALS_SETUP.md)

## 📋 Installation Instructions

### Using the Professional Installer
1. Download RustyBot_Setup_v${Version}.0.exe
2. Run the installer (administrator rights required)
3. Follow the installation wizard
4. Launch RustyBot from desktop shortcut or Start Menu

### Using the Standalone ZIP
1. Download RustyBot_v${Version}_Standalone.zip
2. Extract to your preferred location
3. Run RustyBot.exe directly
4. Configure your credentials in secure.env
5. Check for updates manually through Options → Check for Updates

## 🔒 Security Notes
- Installer automatically configures Windows Defender exclusions
- All credentials stored securely in secure.env file
- See SECURE_CREDENTIALS_SETUP.md for credential setup

## 📝 Requirements
- Windows 10/11 (64-bit)
- Administrator rights (for installer)
- Active internet connection for Twitch integration
- Python NOT required - standalone executable

## 🆘 Support
- GitHub Issues: https://github.com/nexis84/Rusty-Client/issues
- Documentation: See README.md in the package

---

**Version**: $Version  
**Release Date**: $(Get-Date -Format 'MMMM d, yyyy')  
**Build Type**: Professional Release with Manual Update System
"@

Set-Content "github upload\RELEASE_NOTES_v${Version}.md" -Value $releaseNotes
Write-Host "  + Release notes created" -ForegroundColor Green

# Final Summary
Write-Host @"

═══════════════════════════════════════════════════════
   ✅ Build Complete - RustyBot v$Version
═══════════════════════════════════════════════════════

"@ -ForegroundColor Cyan

Write-Host "FILES READY IN 'github upload':" -ForegroundColor Yellow
Get-ChildItem "github upload" -Filter "*$Version*" | ForEach-Object {
    $size = $_.Length / 1MB
    $sizeRounded = [math]::Round($size, 2)
    Write-Host "   + $($_.Name) ($sizeRounded MB)" -ForegroundColor Green
}

Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Test the installer and ZIP package" -ForegroundColor White
Write-Host "   2. Review RELEASE_NOTES_v${Version}.md and add details" -ForegroundColor White
Write-Host "   3. Go to: https://github.com/nexis84/Rusty-Client/releases" -ForegroundColor White
Write-Host "   4. Click 'Draft a new release'" -ForegroundColor White
Write-Host "   5. Tag: v$Version" -ForegroundColor White
Write-Host "   6. Upload files from 'github upload' folder" -ForegroundColor White
Write-Host "   7. Copy content from RELEASE_NOTES_v${Version}.md" -ForegroundColor White
Write-Host "   8. Publish release!" -ForegroundColor White
Write-Host ""
$currentPath = Get-Location
Write-Host "All files ready in: $currentPath\github upload" -ForegroundColor Green
Write-Host ""
