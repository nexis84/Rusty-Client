<#
collect_update_diagnostics.ps1

Usage:
  Run on the TEST MACHINE (where RustyBot v1.5.7 is installed) as Administrator.
  This script collects updater logs, tails them during the update, captures process lists,
  the Windows Application event log, and snapshots of important files. It packages everything
  into a zip for easier upload and analysis.

Example:
  .\collect_update_diagnostics.ps1 -InstallDir "C:\RustyBot" -DurationSeconds 180 -OutDir "C:\Users\Public\rustybot_diag"

Parameters:
  -InstallDir       : Install directory (default C:\RustyBot)
  -DurationSeconds  : How long to monitor/tail logs while you trigger the auto-update (default 180)
  -OutDir           : Where to write outputs (default: %TEMP%\rustybot_diag_<timestamp>)
#>
param(
    [string]$InstallDir = "C:\RustyBot",
    [int]$DurationSeconds = 180,
    [string]$OutDir = "$env:TEMP\rustybot_diag_$((Get-Date).ToString('yyyyMMdd_HHmmss'))",
    [switch]$SkipAdminCheck
)

function Ensure-Admin {
    if ($SkipAdminCheck) {
        Write-Output "Skipping admin check because -SkipAdminCheck was provided"
        return
    }
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Error "This script must be run as Administrator. Re-run the PowerShell session as Admin and try again, or re-run with -SkipAdminCheck to bypass for offline inspection."
        exit 1
    }
}

Ensure-Admin

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
Write-Output "Diagnostic output folder: $OutDir"

# Paths to watch / collect
$pathsToCollect = @(
    "$InstallDir\update_log.txt",
    "$InstallDir\app\update_log.txt",
    "$InstallDir\app\_internal\update_debug.log",
    "$InstallDir\app\_internal\python312.dll",
    "$InstallDir\app\Main.exe",
    "$InstallDir\app\RustyBot.exe",
    "$InstallDir\Launcher.exe",
    "$InstallDir\RustyBot.exe"
)

# Copy any existing logs and important files
foreach ($p in $pathsToCollect) {
    if (Test-Path $p) {
        $dest = Join-Path $OutDir (Split-Path $p -Leaf)
        try {
            Copy-Item -Path $p -Destination $dest -Force -ErrorAction Stop
            Write-Output "Copied $p -> $dest"
        } catch {
            Write-Warning "Failed to copy $p : $_"
        }
    } else {
        Write-Output "Not found: $p"
    }
}

# Function to tail a file into an output file for a period of time
function Tail-FileTo($SourceFile, $OutFile, [int]$Seconds) {
    if (-not (Test-Path $SourceFile)) { Write-Output "Tail: source missing: $SourceFile"; return }
    Write-Output "Tailing $SourceFile -> $OutFile for $Seconds seconds"

    $start = Get-Date
    $file = Get-Item $SourceFile
    $stream = [System.IO.File]::Open($file.FullName, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    $reader = New-Object System.IO.StreamReader($stream)
    # Seek to end so we only capture new content
    $reader.BaseStream.Seek(0, 'End') | Out-Null

    $outStream = New-Object System.IO.StreamWriter($OutFile, $false)
    $outStream.AutoFlush = $true

    try {
        while ((Get-Date) -lt $start.AddSeconds($Seconds)) {
            $line = $reader.ReadLine()
            if ($null -ne $line) {
                $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                $outStream.WriteLine("[$timestamp] $line")
            } else {
                Start-Sleep -Milliseconds 200
            }
        }
    } finally {
        $reader.Close()
        $stream.Close()
        $outStream.Close()
    }
}

# Start background tail jobs (if files exist)
$tailJobs = @()
$watchFiles = @{
    "$InstallDir\app\_internal\update_debug.log" = "$OutDir\update_debug_tail.log"
    "$InstallDir\app\update_log.txt" = "$OutDir\app_update_log_tail.txt"
    "$InstallDir\update_log.txt" = "$OutDir\root_update_log_tail.txt"
}

foreach ($k in $watchFiles.Keys) {
    if (Test-Path $k) {
        $scriptBlock = { param($s,$o,$t) Tail-FileTo -SourceFile $s -OutFile $o -Seconds $t } 
        $job = Start-Job -ScriptBlock $scriptBlock -ArgumentList $k, $watchFiles[$k], $DurationSeconds
        $tailJobs += $job
        Write-Output "Started tail job for $k"
    } else {
        Write-Output "No file to tail: $k"
    }
}

# While tails run, periodically snapshot processes and file locks
$snapInterval = 5
$procSnapDir = Join-Path $OutDir "process_snapshots"
New-Item -ItemType Directory -Path $procSnapDir -Force | Out-Null

$endTime = (Get-Date).AddSeconds($DurationSeconds)
$i = 0
while ((Get-Date) -lt $endTime) {
    $i++
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $procFile = Join-Path $procSnapDir "procs_$ts.txt"
    Get-Process | Sort-Object CPU -Descending | Select-Object Id,ProcessName,CPU,PM,WS | Out-File -FilePath $procFile -Encoding UTF8

    # List open handles for Main/Launcher/RustyBot if handle.exe available (Sysinternals)
    $handlesOut = Join-Path $procSnapDir "handles_$ts.txt"
    $possibleHandles = @("$InstallDir\app\Main.exe","$InstallDir\app\RustyBot.exe","$InstallDir\Launcher.exe","$InstallDir\RustyBot.exe")
    $foundHandleInfo = $false
    foreach ($h in $possibleHandles) {
        if (Test-Path $h) {
            # Try to use handle.exe if present in PATH
            try {
                $handlePath = (Get-Command handle.exe -ErrorAction SilentlyContinue).Source
                if ($handlePath) {
                    & $handlePath -accepteula $h > $handlesOut 2>&1
                    $foundHandleInfo = $true
                }
            } catch {
                # ignore
            }
        }
    }
    if (-not $foundHandleInfo) { "handle.exe not present or no entries" | Out-File -FilePath $handlesOut }

    Start-Sleep -Seconds $snapInterval
}

# Wait for tail jobs to finish
if ($tailJobs.Count -gt 0) {
    Write-Output "Waiting for tail jobs to finish..."
    Wait-Job -Job $tailJobs -Timeout 10 | Out-Null
    Receive-Job -Job $tailJobs | Out-Null
    # cleanup jobs
    $tailJobs | Remove-Job -Force
}

# Collect recent Application event log entries related to RustyBot or python312
$since = (Get-Date).AddMinutes(-30)
$evts = Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2; StartTime=$since} | Where-Object { $_.Message -match 'Main.exe|Launcher.exe|RustyBot|python312.dll|Faulting application' }
if ($evts) {
    $evts | Select-Object TimeCreated,Id,ProviderName,@{n='Message';e={$_.Message}} | ConvertTo-Json -Depth 4 | Out-File -FilePath (Join-Path $OutDir "event_log_errors.json") -Encoding utf8
    Write-Output "Saved event log entries to event_log_errors.json"
} else {
    Write-Output "No matching Application errors found in last 30 minutes"
}

# Snapshot _internal folder listing
if (Test-Path "$InstallDir\app\_internal") {
    Get-ChildItem -Path "$InstallDir\app\_internal" -Recurse -Force | Select-Object FullName,Length,LastWriteTime | ConvertTo-Json -Depth 10 | Out-File (Join-Path $OutDir "internal_listing.json") -Encoding utf8
    Write-Output "Saved _internal listing"
}

# Zip the output
$zipName = Join-Path $OutDir ("rustybot_diag_" + (Get-Date).ToString('yyyyMMdd_HHmmss') + ".zip")
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($OutDir, $zipName)
Write-Output "Diagnostics collected into: $zipName"

# Also print the location for convenience
Write-Output "Done. Upload the zip or paste the outputs for analysis: $zipName"
