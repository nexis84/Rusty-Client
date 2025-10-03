# Build Professional Inno Setup Installer for RustyBot
# This creates a trusted Windows installer that won't trigger antivirus warnings

param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

Write-Host @"
========================================
  RustyBot Professional Installer Build
  Using Inno Setup (Industry Standard)
========================================
"@ -ForegroundColor Cyan

# Check if Inno Setup is installed
$innoSetupPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoSetupPath)) {
    Write-Host ""
    Write-Host "Inno Setup 6 is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Download and install from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing, run this script again." -ForegroundColor Yellow
    Write-Host ""
    
    $download = Read-Host "Open download page now? (y/n)"
    if ($download -eq "y") {
        Start-Process "https://jrsoftware.org/isdl.php"
    }
    
    exit 1
}

Write-Host ""
Write-Host "✓ Inno Setup found: $innoSetupPath" -ForegroundColor Green

# Build main application first (if not skipping)
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "Building main application with Nuitka..." -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path ".\build_nuitka.ps1") {
        & ".\build_nuitka.ps1"
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "ERROR: Main application build failed!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Warning: build_nuitka.ps1 not found. Using existing build..." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Skipping main application build (using existing)..." -ForegroundColor Yellow
}

# Verify required files exist
Write-Host ""
Write-Host "Verifying required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "Main.exe",
    "Main.dist",
    "RustyBot.vbs",
    "RustyBot.bat",
    "config.json",
    "secure.env",
    "README.md",
    "assets",
    "sounds",
    "Fonts"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "ERROR: Missing required files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please build the main application first." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ All required files present" -ForegroundColor Green

# Create output directory
Write-Host ""
Write-Host "Creating output directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "installer_output" -Force | Out-Null
Write-Host "✓ Output directory ready: installer_output\" -ForegroundColor Green

# Build installer
Write-Host ""
Write-Host "Building installer with Inno Setup..." -ForegroundColor Yellow
Write-Host "This may take a few minutes due to compression..." -ForegroundColor Gray
Write-Host ""

$scriptPath = "installer_improved.iss"
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: $scriptPath not found!" -ForegroundColor Red
    exit 1
}

try {
    & $innoSetupPath $scriptPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Inno Setup build failed! (Exit code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to run Inno Setup: $_" -ForegroundColor Red
    exit 1
}

# Check if installer was created
$installerFile = Get-ChildItem -Path "installer_output" -Filter "RustyBot_Setup_*.exe" | Select-Object -First 1

if (-not $installerFile) {
    Write-Host ""
    Write-Host "ERROR: Installer was not created!" -ForegroundColor Red
    Write-Host "Check installer_output\ for log files." -ForegroundColor Yellow
    exit 1
}

# Get file size
$fileSizeMB = [math]::Round($installerFile.Length / 1MB, 2)

# Success!
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installer Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Installer created:" -ForegroundColor Cyan
Write-Host "  File: $($installerFile.Name)" -ForegroundColor White
Write-Host "  Path: $($installerFile.FullName)" -ForegroundColor White
Write-Host "  Size: $fileSizeMB MB" -ForegroundColor White
Write-Host ""
Write-Host "This installer:" -ForegroundColor Cyan
Write-Host "  ✓ Won't trigger Windows Defender warnings" -ForegroundColor Green
Write-Host "  ✓ Has a professional, modern UI" -ForegroundColor Green
Write-Host "  ✓ Automatically handles Windows Defender exclusions" -ForegroundColor Green
Write-Host "  ✓ Configures Windows Firewall rules" -ForegroundColor Green
Write-Host "  ✓ Creates desktop shortcuts" -ForegroundColor Green
Write-Host "  ✓ Includes proper uninstaller" -ForegroundColor Green
Write-Host ""
Write-Host "Test the installer:" -ForegroundColor Yellow
Write-Host "  $($installerFile.FullName)" -ForegroundColor White
Write-Host ""
Write-Host "Distribution:" -ForegroundColor Yellow
Write-Host "  1. Test the installer on a clean Windows system" -ForegroundColor White
Write-Host "  2. Upload to GitHub Releases" -ForegroundColor White
Write-Host "  3. Users download and run the .exe" -ForegroundColor White
Write-Host ""

# Ask if user wants to test the installer
$test = Read-Host "Run the installer now for testing? (y/n)"
if ($test -eq "y") {
    Write-Host ""
    Write-Host "Launching installer..." -ForegroundColor Cyan
    Start-Process $installerFile.FullName
}

Write-Host ""
Write-Host "Build script complete!" -ForegroundColor Green
Write-Host ""
