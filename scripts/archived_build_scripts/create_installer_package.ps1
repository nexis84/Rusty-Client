# RustyBot Minimal Installer Package Creator
# Creates package with ONLY essential installer files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot Installer Package Creator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$releaseDir = ".\release"
$packageDir = "$releaseDir\RustyBot_Installer"
$zipPath = "$releaseDir\RustyBot_Installer.zip"
$distDir = ".\dist\Main.dist"

# Check for source
if (-not (Test-Path $distDir)) {
    Write-Host "Error: $distDir not found. Run build_nuitka.ps1 first!" -ForegroundColor Red
    exit 1
}

# Clean previous installer package
Write-Host "Cleaning previous installer package..." -ForegroundColor Yellow
if (Test-Path $packageDir) {
    Remove-Item -Recurse -Force $packageDir
}
if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Copy ONLY the compiled app
Write-Host "Copying RustyBot application..." -ForegroundColor Yellow
$appDir = "$packageDir\app"

# Use robocopy for more reliable copying
$robocopyResult = robocopy $distDir $appDir /E /NFL /NDL /NJH /NJS /nc /ns /np
$fileCount = (Get-ChildItem -Path $appDir -Recurse -File).Count
Write-Host "  Copied: $fileCount files" -ForegroundColor Green

# Rename Main.exe to RustyBot.exe
# Ensure the executable is named RustyBot.exe (PyInstaller creates RustyBot.exe already)
# If using other build tools that output Main.exe, rename it to RustyBot.exe
$mainExe = "$appDir\Main.exe"
$newExe = "$appDir\RustyBot.exe"
if (Test-Path $mainExe -and -not (Test-Path $newExe)) {
    Rename-Item -Path $mainExe -NewName "RustyBot.exe" -Force
}

# Copy GUI installer executable to root
Write-Host "Copying GUI installer..." -ForegroundColor Yellow
$installerExe = ".\RustyInstaller.exe"

if (Test-Path $installerExe) {
    Copy-Item -Path $installerExe -Destination "$packageDir\RustyInstaller.exe" -Force
    $installerSize = [math]::Round((Get-Item $installerExe).Length / 1MB, 2)
    Write-Host "  Installer copied successfully ($installerSize MB)" -ForegroundColor Green
} else {
    Write-Host "  Warning: Installer not found at $installerExe" -ForegroundColor Yellow
}

# Copy uninstaller executable to root
Write-Host "Copying uninstaller..." -ForegroundColor Yellow
$uninstallerExe = ".\dist\RustyUninstaller.exe"

if (Test-Path $uninstallerExe) {
    Copy-Item -Path $uninstallerExe -Destination "$packageDir\RustyUninstaller.exe" -Force
    $uninstallerSize = [math]::Round((Get-Item $uninstallerExe).Length / 1MB, 2)
    Write-Host "  Uninstaller copied successfully ($uninstallerSize MB)" -ForegroundColor Green
} else {
    Write-Host "  Warning: Uninstaller not found at $uninstallerExe" -ForegroundColor Yellow
}

# Create ZIP
Write-Host "Creating ZIP archive..." -ForegroundColor Yellow
Compress-Archive -Path "$packageDir\*" -DestinationPath $zipPath -Force

# Get sizes
$folderSize = [math]::Round((Get-ChildItem -Path $packageDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installer Package Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package Details:" -ForegroundColor Cyan
Write-Host "  - Application files: $fileCount" -ForegroundColor White
Write-Host "  - Folder size: $folderSize MB" -ForegroundColor White
Write-Host "  - ZIP size: $zipSize MB" -ForegroundColor White
Write-Host "  - Location: $zipPath" -ForegroundColor White
Write-Host ""
Write-Host "Contents:" -ForegroundColor Cyan
Write-Host "  - RustyInstaller.exe (double-click to start installer)" -ForegroundColor White
Write-Host "  - app\ (RustyBot application files)" -ForegroundColor White
Write-Host ""
Write-Host "User Instructions:" -ForegroundColor Cyan
Write-Host "  1. Extract ZIP" -ForegroundColor White
Write-Host "  2. Right-click 'RustyInstaller.exe' → Run as Administrator" -ForegroundColor White
Write-Host "  3. Follow GUI installer prompts" -ForegroundColor White
Write-Host "  4. RustyBot auto-update handles future updates" -ForegroundColor White
Write-Host ""
