# cleanup_distribution.ps1
# Removes unnecessary debug and unused files from Nuitka distribution

$distPath = "dist\Main.dist"

if (-not (Test-Path $distPath)) {
    Write-Host "ERROR: Distribution folder not found at $distPath" -ForegroundColor Red
    exit 1
}

Write-Host "`nCleaning up distribution files..." -ForegroundColor Cyan

# Files to remove
$filesToRemove = @(
    "v8_context_snapshot.debug.bin",  # Debug symbols - 2.03 MB
    "_bz2.pyd",                        # bzip2 compression - not used
    "_lzma.pyd",                       # LZMA compression - not used
    "_wmi.pyd",                        # Windows Management Instrumentation - not used
    "_multiprocessing.pyd",            # Multiprocessing - not used (using threading)
    "_overlapped.pyd"                  # Windows async I/O - not used
)

$totalSaved = 0
$removedCount = 0

foreach ($file in $filesToRemove) {
    $fullPath = Join-Path $distPath $file
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        $sizeMB = [math]::Round($size / 1MB, 2)
        Remove-Item $fullPath -Force
        Write-Host "  [REMOVED] $file - $sizeMB MB" -ForegroundColor Green
        $totalSaved += $size
        $removedCount++
    } else {
        Write-Host "  [SKIP] $file - already removed or not in build" -ForegroundColor Yellow
    }
}

$totalSavedMB = [math]::Round($totalSaved / 1MB, 2)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "  Files removed: $removedCount" -ForegroundColor White
Write-Host "  Space saved: $totalSavedMB MB" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Cyan

# Show new distribution size
Write-Host "Current distribution size:" -ForegroundColor Cyan
$totalSize = (Get-ChildItem -Path $distPath -File -Recurse | Measure-Object -Property Length -Sum).Sum
$totalSizeMB = [math]::Round($totalSize / 1MB, 2)
Write-Host "  Total: $totalSizeMB MB" -ForegroundColor White
Write-Host ""
