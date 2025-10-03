# RustyBot Nuitka Build Script
# This script builds RustyBot using Nuitka instead of PyInstaller
# Nuitka compiles Python to C which typically avoids antivirus false positives

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot Nuitka Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Nuitka is installed
Write-Host "Checking for Nuitka..." -ForegroundColor Yellow
try {
    python -m nuitka --version
    Write-Host "Nuitka found!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Nuitka not found!" -ForegroundColor Red
    Write-Host "Please install: pip install nuitka ordered-set zstandard" -ForegroundColor Red
    exit 1
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "Main.dist") {
    Remove-Item -Recurse -Force "Main.dist"
}
if (Test-Path "Main.build") {
    Remove-Item -Recurse -Force "Main.build"
}
if (Test-Path "Main.onefile-build") {
    Remove-Item -Recurse -Force "Main.onefile-build"
}

# Build with Nuitka
Write-Host ""
Write-Host "Building RustyBot with Nuitka..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Yellow
Write-Host ""

python -m nuitka `
    --standalone `
    --windows-disable-console `
    --enable-plugin=pyqt6 `
    --include-data-dir=assets=assets `
    --include-data-dir=sounds=sounds `
    --include-data-dir=Fonts=Fonts `
    --include-data-file=config.json=config.json `
    --include-data-file=.env=.env `
    --output-dir=dist `
    Main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Build Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # Show file size
    if (Test-Path "dist\Main.exe") {
        $fileSize = (Get-Item "dist\Main.exe").Length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        Write-Host ""
        Write-Host "Executable created: dist\Main.exe" -ForegroundColor Cyan
        Write-Host "File size: $fileSizeMB MB" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "The executable is ready for distribution!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Note: This is a standalone build (folder-based distribution)" -ForegroundColor Yellow
        Write-Host "Distribute the entire 'dist' folder to users" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Build Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Check the errors above for details." -ForegroundColor Red
    exit 1
}
