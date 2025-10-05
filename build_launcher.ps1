# Build RustyBot Launcher
# This creates the small launcher executable that handles updates

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         Building RustyBot Launcher v1.5.0                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Configuration
$LauncherScript = "launcher.py"
$OutputDir = "dist_launcher"
$Version = "1.5.0"

# Check if launcher.py exists
if (-not (Test-Path $LauncherScript)) {
    Write-Host "❌ ERROR: $LauncherScript not found!" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Build Configuration:" -ForegroundColor Yellow
Write-Host "   Source:  $LauncherScript" -ForegroundColor White
Write-Host "   Output:  $OutputDir\Launcher.exe" -ForegroundColor White
Write-Host "   Version: $Version`n" -ForegroundColor White

# Check if Nuitka is installed
Write-Host "🔍 Checking for Nuitka..." -ForegroundColor Cyan
try {
    $nuitkaVersion = python -m nuitka --version 2>&1 | Select-Object -First 1
    Write-Host "   ✓ Nuitka found: $nuitkaVersion" -ForegroundColor Green
    $useNuitka = $true
} catch {
    Write-Host "   ⚠ Nuitka not found, will try PyInstaller" -ForegroundColor Yellow
    $useNuitka = $false
}

if ($useNuitka) {
    Write-Host "`n🔨 Building with Nuitka (recommended)...`n" -ForegroundColor Cyan
    
    # Clean previous build
    if (Test-Path $OutputDir) {
        Remove-Item -Recurse -Force $OutputDir
    }
    
    # Build command
    python -m nuitka `
        --standalone `
        --onefile `
        --enable-plugin=pyqt6 `
        --include-data-file=auto_updater.py=auto_updater.py `
        --windows-company-name="Nexis84" `
        --windows-product-name="RustyBot Launcher" `
        --windows-file-version=$Version `
        --windows-product-version=$Version `
        --windows-file-description="RustyBot Launcher - Update Manager" `
        --output-dir=$OutputDir `
        --output-filename=Launcher.exe `
        --assume-yes-for-downloads `
        $LauncherScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Nuitka build successful!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Nuitka build failed!" -ForegroundColor Red
        exit 1
    }
} else {
    # Try PyInstaller
    Write-Host "🔍 Checking for PyInstaller..." -ForegroundColor Cyan
    try {
        $pyiVersion = pyinstaller --version 2>&1
        Write-Host "   ✓ PyInstaller found: $pyiVersion" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ ERROR: Neither Nuitka nor PyInstaller found!" -ForegroundColor Red
        Write-Host "`n   Install one of them:" -ForegroundColor Yellow
        Write-Host "   pip install nuitka  (recommended)" -ForegroundColor White
        Write-Host "   pip install pyinstaller" -ForegroundColor White
        exit 1
    }
    
    Write-Host "`n🔨 Building with PyInstaller...`n" -ForegroundColor Cyan
    
    # Clean previous build
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "Launcher.spec") { Remove-Item -Force "Launcher.spec" }
    
    # Build command
    pyinstaller `
        --onefile `
        --windowed `
        --name=Launcher `
        --add-data "auto_updater.py;." `
        --distpath=$OutputDir `
        $LauncherScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ PyInstaller build successful!" -ForegroundColor Green
        
        # Clean up build artifacts
        if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
        if (Test-Path "Launcher.spec") { Remove-Item -Force "Launcher.spec" }
    } else {
        Write-Host "`n❌ PyInstaller build failed!" -ForegroundColor Red
        exit 1
    }
}

# Verify output
$LauncherExe = Join-Path $OutputDir "Launcher.exe"
if (Test-Path $LauncherExe) {
    $fileInfo = Get-Item $LauncherExe
    $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    
    Write-Host "`n📦 Build Results:" -ForegroundColor Cyan
    Write-Host "   File: $LauncherExe" -ForegroundColor White
    Write-Host "   Size: $sizeMB MB" -ForegroundColor White
    Write-Host "   Date: $($fileInfo.LastWriteTime)`n" -ForegroundColor White
    
    # Copy to dist folder if it exists
    if (Test-Path "dist\Main.dist") {
        Write-Host "📋 Copying Launcher.exe to dist\Main.dist\..." -ForegroundColor Cyan
        Copy-Item $LauncherExe "dist\Main.dist\" -Force
        Write-Host "   ✓ Copied successfully`n" -ForegroundColor Green
    }
    
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║            ✅ LAUNCHER BUILD COMPLETE! ✅                  ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
    
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Test Launcher.exe" -ForegroundColor White
    Write-Host "  2. Create ZIP package with Launcher included" -ForegroundColor White
    Write-Host "  3. Upload to GitHub releases`n" -ForegroundColor White
    
    # Ask if user wants to create ZIP now
    $createZip = Read-Host "Create ZIP package now? (y/n)"
    if ($createZip -eq 'y') {
        Write-Host "`n🗜️ Creating ZIP package..." -ForegroundColor Cyan
        
        $zipName = "RustyBot_v${Version}_WithLauncher.zip"
        $zipPath = "installer_output\1.5.0\$zipName"
        
        # Ensure output directory exists
        if (-not (Test-Path "installer_output\1.5.0")) {
            New-Item -ItemType Directory -Path "installer_output\1.5.0" -Force | Out-Null
        }
        
        # Create ZIP
        Compress-Archive -Force -Path "dist\Main.dist\*" -DestinationPath $zipPath
        
        $zipInfo = Get-Item $zipPath
        $zipSizeMB = [math]::Round($zipInfo.Length / 1MB, 2)
        
        Write-Host "   ✓ ZIP created: $zipName" -ForegroundColor Green
        Write-Host "   Size: $zipSizeMB MB" -ForegroundColor White
        Write-Host "   Location: installer_output\1.5.0\`n" -ForegroundColor White
    }
    
} else {
    Write-Host "`n❌ ERROR: Launcher.exe not found after build!" -ForegroundColor Red
    exit 1
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
