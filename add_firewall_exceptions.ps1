# RustyBot Firewall Configuration Script
# Run as Administrator to add Windows Firewall exceptions for RustyBot

param(
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "C:\Program Files\RustyBot",
    
    [Parameter(Mandatory=$false)]
    [switch]$Remove = $false
)

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges to modify Windows Firewall rules." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    pause
    exit 1
}

# Function to add firewall rules
function Add-RustyBotFirewallRules {
    param([string]$Path)
    
    $LauncherPath = Join-Path $Path "Launcher.exe"
    $MainPath = Join-Path $Path "Main.exe"
    
    Write-Host "Adding Windows Firewall exceptions for RustyBot..." -ForegroundColor Green
    
    try {
        # Add rules for Launcher.exe
        if (Test-Path $LauncherPath) {
            netsh advfirewall firewall add rule name="RustyBot Launcher (Inbound)" dir=in action=allow program="$LauncherPath" | Out-Null
            netsh advfirewall firewall add rule name="RustyBot Launcher (Outbound)" dir=out action=allow program="$LauncherPath" | Out-Null
            Write-Host "✓ Added firewall rules for Launcher.exe" -ForegroundColor Green
        } else {
            Write-Host "⚠ Launcher.exe not found at: $LauncherPath" -ForegroundColor Yellow
        }
        
        # Add rules for Main.exe
        if (Test-Path $MainPath) {
            netsh advfirewall firewall add rule name="RustyBot Main (Inbound)" dir=in action=allow program="$MainPath" | Out-Null
            netsh advfirewall firewall add rule name="RustyBot Main (Outbound)" dir=out action=allow program="$MainPath" | Out-Null
            Write-Host "✓ Added firewall rules for Main.exe" -ForegroundColor Green
        } else {
            Write-Host "⚠ Main.exe not found at: $MainPath" -ForegroundColor Yellow
        }
        
        Write-Host "`nWindows Firewall exceptions have been successfully added for RustyBot!" -ForegroundColor Green
        
    } catch {
        Write-Host "✗ Error adding firewall rules: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Function to remove firewall rules
function Remove-RustyBotFirewallRules {
    Write-Host "Removing Windows Firewall exceptions for RustyBot..." -ForegroundColor Yellow
    
    try {
        # Remove Launcher rules
        netsh advfirewall firewall delete rule name="RustyBot Launcher (Inbound)" | Out-Null
        netsh advfirewall firewall delete rule name="RustyBot Launcher (Outbound)" | Out-Null
        Write-Host "✓ Removed firewall rules for Launcher.exe" -ForegroundColor Green
        
        # Remove Main rules
        netsh advfirewall firewall delete rule name="RustyBot Main (Inbound)" | Out-Null
        netsh advfirewall firewall delete rule name="RustyBot Main (Outbound)" | Out-Null
        Write-Host "✓ Removed firewall rules for Main.exe" -ForegroundColor Green
        
        Write-Host "`nWindows Firewall exceptions have been successfully removed for RustyBot!" -ForegroundColor Green
        
    } catch {
        Write-Host "✗ Error removing firewall rules: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Main execution
Write-Host "RustyBot Firewall Configuration" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

if ($Remove) {
    Remove-RustyBotFirewallRules
} else {
    Write-Host "Install Path: $InstallPath" -ForegroundColor White
    Write-Host ""
    
    if (-not (Test-Path $InstallPath)) {
        Write-Host "⚠ Installation directory not found: $InstallPath" -ForegroundColor Yellow
        Write-Host "Please specify the correct path using: -InstallPath 'C:\Path\To\RustyBot'" -ForegroundColor Yellow
        pause
        exit 1
    }
    
    Add-RustyBotFirewallRules -Path $InstallPath
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")