# Build Script for RustyBot
# Creates a standalone executable using PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pyinstaller = pip show pyinstaller 2>$null
if (-not $pyinstaller) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the executable
Write-Host ""
Write-Host "Building RustyBot executable..." -ForegroundColor Green
pyinstaller --clean RustyBot.spec

# Check if build was successful
if (Test-Path "dist\RustyBot.exe") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Build Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\RustyBot.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test the executable: .\dist\RustyBot.exe" -ForegroundColor White
    Write-Host "2. Create a release on GitHub" -ForegroundColor White
    Write-Host "3. Upload the RustyBot.exe file to the release" -ForegroundColor White
    Write-Host ""
    
    # Calculate size
    $size = (Get-Item "dist\RustyBot.exe").Length / 1MB
    Write-Host "Executable size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
    
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Build Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the output above for errors." -ForegroundColor Yellow
    exit 1
}
