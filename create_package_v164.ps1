# RustyBot v1.6.4 Package Creator (PyInstaller)
# Creates a distributable ZIP file from PyInstaller builds

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot v1.6.4 Package Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if dist folder exists
if (-not (Test-Path "dist\RustyBot")) {
    Write-Host "ERROR: RustyBot build folder not found!" -ForegroundColor Red
    Write-Host "Please run .\build.ps1 first" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "dist\Launcher.exe")) {
    Write-Host "ERROR: Launcher.exe not found!" -ForegroundColor Red
    Write-Host "Please run 'pyinstaller --clean Launcher.spec' first" -ForegroundColor Red
    exit 1
}

# Create release folder
Write-Host "Creating release package..." -ForegroundColor Yellow
$releaseName = "RustyBot_v1.6.4_Standalone"
$releaseFolder = "release\$releaseName"

if (Test-Path "release") {
    Remove-Item -Recurse -Force "release"
}
New-Item -ItemType Directory -Force -Path $releaseFolder | Out-Null

# Copy the PyInstaller builds
Write-Host "Copying RustyBot application..." -ForegroundColor Yellow
Copy-Item -Path "dist\RustyBot\*" -Destination $releaseFolder -Recurse

Write-Host "Copying Launcher.exe..." -ForegroundColor Yellow
Copy-Item -Path "dist\Launcher.exe" -Destination $releaseFolder

# Copy user-editable files
Write-Host "Copying user configuration files..." -ForegroundColor Yellow
Copy-Item -Path "config.json" -Destination $releaseFolder -ErrorAction SilentlyContinue
Copy-Item -Path "secure.env" -Destination $releaseFolder -ErrorAction SilentlyContinue

# Create simple README
Write-Host "Creating README..." -ForegroundColor Yellow
$readmeContent = @"
RustyBot v1.6.4 - Twitch Giveaway Bot

Quick Start:
1. Extract all files from this ZIP
2. Double-click Launcher.exe to start RustyBot
3. On first run, enter your Twitch channel name

The bot will automatically check for updates on startup.

Files:
- Launcher.exe - Main application launcher
- RustyBot.exe - Core application
- config.json - Settings (edit this)
- secure.env - Encrypted credentials (don't edit)

For support: https://github.com/nexis84/Rusty-Client
"@

$readmeContent | Out-File -FilePath "$releaseFolder\README.txt" -Encoding UTF8

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
Write-Host "  RustyBot v1.6.4 Package Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package Details:" -ForegroundColor Cyan
Write-Host "  - Folder size: $folderSizeMB MB" -ForegroundColor White
Write-Host "  - ZIP size: $zipSizeMB MB" -ForegroundColor White
Write-Host "  - Location: $zipPath" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test Launcher.exe from release\$releaseName\" -ForegroundColor White
Write-Host "  2. Upload $releaseName.zip to GitHub Releases" -ForegroundColor White
Write-Host "  3. Test auto-update from an older version!" -ForegroundColor White
Write-Host ""