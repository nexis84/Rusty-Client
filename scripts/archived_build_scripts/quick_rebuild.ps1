# Quick Rebuild Script
# Run this AFTER adding the Windows Defender exclusion

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RustyBot Quick Rebuild" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Building with Nuitka..." -ForegroundColor Yellow
.\build_nuitka.ps1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Step 2: Creating distribution package..." -ForegroundColor Yellow
    .\create_package.ps1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  Rebuild Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Test your application:" -ForegroundColor Yellow
        Write-Host "  cd release\RustyBot_v1.3.9_Standalone" -ForegroundColor Cyan
        Write-Host "  .\RustyBot.vbs" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Package creation failed!" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "Build failed! Check the errors above." -ForegroundColor Red
}
