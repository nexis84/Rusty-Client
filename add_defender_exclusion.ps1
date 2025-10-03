# Add Windows Defender Exclusion for RustyBot Development
# Run this as Administrator to exclude the project folder from Windows Defender scanning

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Windows Defender Exclusion Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Yellow
    Write-Host "  1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "  2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "  3. Navigate to this folder" -ForegroundColor Yellow
    Write-Host "  4. Run: .\add_defender_exclusion.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Get current directory
$projectPath = Get-Location

Write-Host "Adding Windows Defender exclusion for:" -ForegroundColor Yellow
Write-Host "  $projectPath" -ForegroundColor Cyan
Write-Host ""

try {
    # Add exclusion for the entire project folder
    Add-MpPreference -ExclusionPath $projectPath
    
    Write-Host "✅ Exclusion added successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The following folder is now excluded from Windows Defender:" -ForegroundColor Green
    Write-Host "  $projectPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now:" -ForegroundColor Yellow
    Write-Host "  1. Rebuild RustyBot: .\build_nuitka.ps1" -ForegroundColor Yellow
    Write-Host "  2. Create package: .\create_package.ps1" -ForegroundColor Yellow
    Write-Host "  3. The exe files won't be deleted anymore!" -ForegroundColor Yellow
    Write-Host ""
    
    # Show current exclusions
    Write-Host "Current Windows Defender Exclusions:" -ForegroundColor Cyan
    $exclusions = Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
    foreach ($exclusion in $exclusions) {
        if ($exclusion -like "*RustyBot*") {
            Write-Host "  - $exclusion" -ForegroundColor Green
        }
    }
    
} catch {
    Write-Host "Failed to add exclusion!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual Steps:" -ForegroundColor Yellow
    Write-Host "  1. Open Windows Security" -ForegroundColor Yellow
    Write-Host "  2. Go to 'Virus & threat protection'" -ForegroundColor Yellow
    Write-Host "  3. Click 'Manage settings' under 'Virus & threat protection settings'" -ForegroundColor Yellow
    Write-Host "  4. Scroll down to 'Exclusions'" -ForegroundColor Yellow
    Write-Host "  5. Click 'Add or remove exclusions'" -ForegroundColor Yellow
    Write-Host "  6. Click 'Add an exclusion' -> 'Folder'" -ForegroundColor Yellow
    Write-Host "  7. Select this folder: $projectPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Important Notes:" -ForegroundColor Yellow
Write-Host "  - This exclusion is for DEVELOPMENT only" -ForegroundColor Yellow
Write-Host "  - Users will still get warnings (that is normal)" -ForegroundColor Yellow
Write-Host "  - Tell users to click 'More info' -> 'Run anyway'" -ForegroundColor Yellow
Write-Host "  - Or tell users to add their own exclusion" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
