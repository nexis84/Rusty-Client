# Build RustyBot GUI Installer
# Creates a standalone executable for the installer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot GUI Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python not found!" -ForegroundColor Red
    exit 1
}

# Install pywin32 if needed
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
$pipList = pip list 2>&1
if ($pipList -notmatch "pywin32") {
    Write-Host "Installing pywin32..." -ForegroundColor Yellow
    pip install pywin32
}

# Build with Nuitka
Write-Host "`nBuilding installer executable..." -ForegroundColor Yellow
Write-Host "This will take a few minutes..." -ForegroundColor Gray
Write-Host ""

python -m nuitka --standalone --onefile --enable-plugin=pyqt6 --windows-company-name=RustyBot --windows-product-name="RustyBot Installer" --windows-file-version=1.4.0 --windows-product-version=1.4.0 --windows-file-description="RustyBot GUI Installer" --output-filename=Install --output-dir=installer_build Install_GUI.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
    Write-Host "Installer created: installer_build\Install.exe" -ForegroundColor Cyan
    
    # Get file size
    $exePath = "installer_build\Install.exe"
    if (Test-Path $exePath) {
        $size = (Get-Item $exePath).Length / 1MB
        Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
    }
    
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Test the installer: .\installer_build\Install.exe" -ForegroundColor White
    Write-Host "2. Run create_package.ps1 to rebuild the distribution" -ForegroundColor White
}
else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Gray
    Write-Host "Check the error messages above." -ForegroundColor Gray
}

Write-Host ""
