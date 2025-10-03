# RustyBot Installer
# This script will:
# 1. Check for admin rights (elevate if needed)
# 2. Let user choose installation location
# 3. Add Windows Defender exclusion
# 4. Extract files
# 5. Create desktop shortcut
# 6. Launch RustyBot

param(
    [string]$InstallPath = ""
)

$ErrorActionPreference = "Stop"

Write-Host @"
========================================
  RustyBot Installer v1.4.0
========================================
"@ -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "This installer needs Administrator rights to:" -ForegroundColor Yellow
    Write-Host "  - Add Windows Defender exclusion (prevents false positive)" -ForegroundColor Yellow
    Write-Host "  - Create installation folder" -ForegroundColor Yellow
    Write-Host "  - Create desktop shortcut" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Requesting Administrator privileges..." -ForegroundColor Cyan
    
    # Re-launch as administrator
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    if ($InstallPath) {
        $arguments += " -InstallPath `"$InstallPath`""
    }
    
    try {
        Start-Process PowerShell -Verb RunAs -ArgumentList $arguments -Wait
        exit 0
    } catch {
        Write-Host ""
        Write-Host "Failed to elevate to Administrator." -ForegroundColor Red
        Write-Host "Please right-click this script and select 'Run as Administrator'" -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Function to get installation path from user
function Get-InstallationPath {
    if ($InstallPath) {
        return $InstallPath
    }
    
    Write-Host "Choose installation location:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. C:\RustyBot (Recommended)" -ForegroundColor White
    Write-Host "  2. C:\Program Files\RustyBot" -ForegroundColor White
    Write-Host "  3. Custom location" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1-3)"
    
    switch ($choice) {
        "1" { return "C:\RustyBot" }
        "2" { return "C:\Program Files\RustyBot" }
        "3" { 
            $custom = Read-Host "Enter full path (e.g., D:\Games\RustyBot)"
            return $custom
        }
        default { 
            Write-Host "Invalid choice, using default: C:\RustyBot" -ForegroundColor Yellow
            return "C:\RustyBot"
        }
    }
}

# Get installation path
$installLocation = Get-InstallationPath
Write-Host ""
Write-Host "Installation location: $installLocation" -ForegroundColor Cyan

# Create installation directory
Write-Host ""
Write-Host "Creating installation directory..." -ForegroundColor Yellow
try {
    if (-not (Test-Path $installLocation)) {
        New-Item -ItemType Directory -Path $installLocation -Force | Out-Null
        Write-Host "  Created: $installLocation" -ForegroundColor Green
    } else {
        Write-Host "  Directory already exists" -ForegroundColor Yellow
        $overwrite = Read-Host "Overwrite existing installation? (y/n)"
        if ($overwrite -ne "y") {
            Write-Host "Installation cancelled." -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 0
        }
    }
} catch {
    Write-Host "  Failed to create directory: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Add Windows Defender exclusion
Write-Host ""
Write-Host "Adding Windows Defender exclusion..." -ForegroundColor Yellow
Write-Host "  This prevents false positive virus warnings" -ForegroundColor Gray
try {
    Add-MpPreference -ExclusionPath $installLocation -ErrorAction Stop
    Write-Host "  Exclusion added successfully!" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not add exclusion: $_" -ForegroundColor Yellow
    Write-Host "  You may need to add it manually if Windows Defender blocks the app" -ForegroundColor Yellow
}

# Extract files
Write-Host ""
Write-Host "Extracting RustyBot files..." -ForegroundColor Yellow

# Get the directory where this script is located (should be inside the extracted folder)
$scriptDir = Split-Path -Parent $PSCommandPath

# Check if we're in the release folder structure
$sourceFolder = $scriptDir
if (Test-Path "$scriptDir\app\RustyBot.exe") {
    Write-Host "  Source folder found at: $scriptDir" -ForegroundColor Gray
} else {
    Write-Host "  ERROR: Could not find RustyBot files!" -ForegroundColor Red
    Write-Host "  Make sure this installer is run from the extracted RustyBot folder" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Copy all files
try {
    Write-Host "  Copying files..." -ForegroundColor Gray
    Copy-Item -Path "$sourceFolder\*" -Destination $installLocation -Recurse -Force -Exclude "Install.ps1","Install.bat"
    Write-Host "  Files copied successfully!" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Failed to copy files: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create desktop shortcut
Write-Host ""
Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = "$desktopPath\RustyBot.lnk"
    $shortcut = $WshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "$installLocation\RustyBot.vbs"
    $shortcut.WorkingDirectory = $installLocation
    $shortcut.Description = "RustyBot - Twitch Giveaway Bot"
    $shortcut.Save()
    Write-Host "  Desktop shortcut created!" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not create desktop shortcut: $_" -ForegroundColor Yellow
}

# Installation complete
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "RustyBot has been installed to:" -ForegroundColor Cyan
Write-Host "  $installLocation" -ForegroundColor White
Write-Host ""
Write-Host "You can:" -ForegroundColor Cyan
Write-Host "  - Double-click the desktop shortcut" -ForegroundColor White
Write-Host "  - Or run: $installLocation\RustyBot.vbs" -ForegroundColor White
Write-Host ""
Write-Host "First Run:" -ForegroundColor Yellow
Write-Host "  You'll be asked to enter your Twitch channel name" -ForegroundColor White
Write-Host "  After that, RustyBot will start automatically" -ForegroundColor White
Write-Host ""

# Ask if user wants to launch now
$launch = Read-Host "Launch RustyBot now? (y/n)"
if ($launch -eq "y") {
    Write-Host ""
    Write-Host "Launching RustyBot..." -ForegroundColor Cyan
    Start-Process -FilePath "$installLocation\RustyBot.vbs"
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Thank you for installing RustyBot!" -ForegroundColor Cyan
Write-Host "GitHub: https://github.com/nexis84/Rusty-Client" -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"
