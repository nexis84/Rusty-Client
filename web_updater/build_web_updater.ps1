# Build script for RustyBot Web Updater
# This creates a small, reliable updater executable

Write-Host "Building RustyBot Web Updater..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "rustybot_web_updater.py")) {
    Write-Host "ERROR: rustybot_web_updater.py not found in current directory" -ForegroundColor Red
    exit 1
}

# Build with PyInstaller
Write-Host "Running PyInstaller..." -ForegroundColor Yellow
pyinstaller --clean --noconfirm RustyBot_Web_Updater.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green

    # Check the size
    $exePath = "dist\RustyBot_Web_Updater.exe"
    if (Test-Path $exePath) {
        $size = (Get-Item $exePath).Length
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "Executable size: $sizeMB MB" -ForegroundColor Cyan

        # Copy to parent directory for easy access
        Copy-Item $exePath "..\RustyBot_Web_Updater.exe" -Force
        Write-Host "Copied to: ..\RustyBot_Web_Updater.exe" -ForegroundColor Green
    }
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Web Updater build complete!" -ForegroundColor Green</content>
<parameter name="filePath">d:\coding project\RustyBot V1.2 GUI and new Draw\Rusty Bot Main Branch - 1.40\web_updater\build_web_updater.ps1