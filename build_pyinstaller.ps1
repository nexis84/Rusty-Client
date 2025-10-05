# RustyBot PyInstaller Build Script
# This script builds RustyBot using PyInstaller instead of Nuitka
# PyInstaller creates a single executable file

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot PyInstaller Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
try {
    pyinstaller --version
    Write-Host "PyInstaller found!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: PyInstaller not found!" -ForegroundColor Red
    Write-Host "Please install: pip install pyinstaller" -ForegroundColor Red
    exit 1
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Build with PyInstaller
Write-Host ""
Write-Host "Building RustyBot with PyInstaller..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Yellow
Write-Host ""

pyinstaller --clean RustyBot.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Build Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green

    # Show file size
    if (Test-Path "dist\RustyBot.exe") {
        $fileSize = (Get-Item "dist\RustyBot.exe").Length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        Write-Host ""
        Write-Host "Executable created: dist\RustyBot.exe" -ForegroundColor Cyan
        Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
    }

    Write-Host ""
    Write-Host "The executable is ready for distribution!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Note: This is a single-file executable" -ForegroundColor Yellow
    Write-Host "Distribute the 'dist\RustyBot.exe' file to users" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Build Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Check the errors above for details." -ForegroundColor Red
    exit 1
}