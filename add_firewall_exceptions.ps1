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
    
    $RustyBotPath = Join-Path $Path "RustyBot.exe"
    
    Write-Host "Adding Windows Firewall exceptions for RustyBot..." -ForegroundColor Green
    
    try {
        # Add rules for RustyBot.exe
        if (Test-Path $RustyBotPath) {
            netsh advfirewall firewall add rule name="RustyBot (Inbound)" dir=in action=allow program="$RustyBotPath" | Out-Null
            netsh advfirewall firewall add rule name="RustyBot (Outbound)" dir=out action=allow program="$RustyBotPath" | Out-Null
            Write-Host "✓ Added firewall rules for RustyBot.exe" -ForegroundColor Green
        } else {
            Write-Host "⚠ RustyBot.exe not found at: $RustyBotPath" -ForegroundColor Yellow
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
        # Remove RustyBot rules
        netsh advfirewall firewall delete rule name="RustyBot (Inbound)" | Out-Null
        netsh advfirewall firewall delete rule name="RustyBot (Outbound)" | Out-Null
        Write-Host "✓ Removed firewall rules for RustyBot.exe" -ForegroundColor Green
        
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