# Auto-Updater Crash Fix - v1.5.8

## Problem Summary
The auto-updater was downloading the update successfully, but the application crashed immediately after restart with a `LoadLibrary` failure for `_internal\python312.dll`.

## Root Cause Analysis
The crash was caused by one or more of:
1. **Windows Defender** quarantining/blocking `python312.dll` during the file copy operation
2. **Partial file copies** due to file handles still being held by the terminated process
3. **Missing admin privileges** preventing the update script from adding Defender exclusions

## Comprehensive Fixes Applied

### 1. UAC Elevation (Critical Fix)
**File**: `auto_updater.py` → `_create_windows_folder_update_script()`

The generated batch script now **self-elevates** using PowerShell before performing any update operations:

```batch
@echo off
REM === Elevation check: relaunch this script elevated if not already ===
if "%1"=="-elev" goto :ELEVATED
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Requesting elevated privileges (UAC)...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -ArgumentList '-elev' -Verb RunAs"
    exit /b
)
:ELEVATED
```

**Impact**: Ensures the script has Administrator privileges to add Defender exclusions reliably.

---

### 2. Pre-emptive Defender Exclusion
**File**: `auto_updater.py` → `_create_windows_folder_update_script()`

The script now attempts to add a Defender exclusion **before** starting any file operations:

```batch
REM === Pre-emptive Defender Exclusion (before any file operations) ===
echo [%TIME%] Adding Defender exclusion pre-emptively... >> "%LOGFILE%"
powershell -NoProfile -Command "try { Add-MpPreference -ExclusionPath 'C:\RustyBot' -ErrorAction Stop; Write-Output 'PRE_EXCLUSION_ADDED' } catch { Write-Output 'PRE_EXCLUSION_FAILED' }" >> "%LOGFILE%" 2>&1
```

**Impact**: Prevents Defender from scanning/quarantining files during the copy operation.

---

### 3. Defender Event Logging
**File**: `auto_updater.py` → `_create_windows_folder_update_script()`

On copy failure, the script now captures recent Defender events:

```batch
powershell -NoProfile -Command "try { Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Windows Defender/Operational'; StartTime=(Get-Date).AddMinutes(-30)} | Where-Object { $_.Message -match 'quarantine|quarantined|removed|blocked|deleted' } | Select TimeCreated, Message | Out-File -FilePath \"%LOGFILE%.defender.txt\" -Encoding utf8 } catch { 'No Defender Operational Log or insufficient privileges' | Out-File -FilePath \"%LOGFILE%.defender.txt\" -Encoding utf8 }" 2>>"%LOGFILE%"
```

**Output**: Creates `update_log.txt.defender.txt` with Defender quarantine events for diagnosis.

---

### 4. Defender Exclusion Retry on Copy Failure
**File**: `auto_updater.py` → `_create_windows_folder_update_script()`

If a file copy fails, the script:
- Captures Defender events (see #3)
- Attempts to add Defender exclusion (with 3 retries, 5-second delays)
- Retries the file copy (up to 3 total attempts)

**Impact**: Recovers from Defender interference mid-update.

---

### 5. Increased File Handle Wait Time
**File**: `auto_updater.py` → `_create_windows_folder_update_script()`

Changed wait time from 15 to **20 seconds** after process termination:

```batch
timeout /t 20 /nobreak >nul
```

**Impact**: Gives Windows more time to release file handles from terminated processes.

---

### 6. Post-Install File Verification
**File**: `auto_updater.py` → `_create_windows_folder_update_script()`

After successful file copy, the script verifies critical files exist:

```batch
REM === Verify critical runtime files exist after installation ===
echo [%TIME%] Verifying critical runtime files... >> "%LOGFILE%"
if exist "C:\RustyBot\_internal\python312.dll" (
    echo [%TIME%] Found python312.dll in _internal >> "%LOGFILE%"
    for %%F in ("C:\RustyBot\_internal\python312.dll") do echo [%TIME%] python312.dll size: %%~zF bytes >> "%LOGFILE%"
) else (
    echo [%TIME%] WARNING: python312.dll missing after update! >> "%LOGFILE%"
    echo [%TIME%] Listing install directory for diagnostics: >> "%LOGFILE%"
    dir "C:\RustyBot" >> "%LOGFILE%" 2>&1
    dir "C:\RustyBot\_internal" >> "%LOGFILE%" 2>&1
)
```

**Impact**: Logs detailed diagnostics if `python312.dll` is missing, including file sizes and directory listings.

---

### 7. Fixed Python Syntax Warnings
**File**: `auto_updater.py` → `_create_windows_folder_update_script()`

Fixed all invalid escape sequences in the f-string batch script:
- Escaped parentheses: `^(...^)`
- Escaped batch special characters in PowerShell commands
- Properly escaped backslashes in paths: `\\*` → `\\\\*`

**Before**: 3 SyntaxWarnings on module import  
**After**: Clean import, no warnings

---

## New Diagnostic Files Generated

When the update runs, you'll now find these files in the install directory:

1. **`update_log.txt`** - Main batch script log (always created)
2. **`update_log.txt.defender.txt`** - Defender events captured during update (created on copy failure)
3. **`app\update_debug.log`** - Python updater module log (always created)

---

## Testing & Verification

### Simulation Test Results
- **Script size**: 13,961 characters
- **Syntax warnings**: **0** (previously 3)
- **Generated script**: Contains all fixes (elevation, pre-emptive exclusion, verification)
- **Simulation result**: ✅ PASS

### Manual Verification Steps
1. Inspect generated script in temp folder:
   ```powershell
   Get-Content 'C:\Users\...\AppData\Local\Temp\rustybot_folder_update.bat' -TotalCount 50
   ```

2. Check for key sections:
   ```powershell
   Select-String -Path '...\rustybot_folder_update.bat' -Pattern 'Elevation|PRE_EXCLUSION|python312.dll size'
   ```

3. Run elevated diagnostic collector during real update:
   ```powershell
   # Run as Administrator
   cd 'C:\path\to\repo\scripts'
   .\collect_update_diagnostics.ps1 -InstallDir 'C:\RustyBot' -DurationSeconds 300 -OutDir 'C:\Users\Public\rustybot_diag'
   ```

---

## Recommended Next Steps for User

### Option A: Test Auto-Update (Recommended)
1. Upload `RustyBot_v1.5.8_Standalone.zip` and `RustyBot_Setup_v1.5.8.0.exe` to GitHub Release v1.5.8
2. On the test machine (running v1.5.7), trigger auto-update from the app
3. The UAC prompt will appear — **click "Yes" to allow elevation**
4. Monitor the update process
5. After restart, verify the app launches successfully

### Option B: Clean Install
If you want to skip testing auto-update:
1. Uninstall current version (optional)
2. Run `RustyBot_Setup_v1.5.8.0.exe` as Administrator
3. The installer adds Defender exclusions during installation

### Option C: Run Diagnostics
If you want detailed logs of the update process:
1. Run the diagnostic collector script (as Administrator) before triggering update
2. Upload the generated diagnostics ZIP for analysis

---

## Expected Behavior After Fix

1. **UAC Prompt**: User will see a UAC elevation prompt when update starts (normal & expected)
2. **Defender Exclusion**: Update log will show "Pre-emptive exclusion added successfully"
3. **Clean Copy**: File copy should succeed on first attempt
4. **Verification**: Log will show `python312.dll size: <bytes>` confirming file exists
5. **Successful Restart**: Application restarts without LoadLibrary errors

---

## Rollback Plan (If Needed)

If the update still fails:
1. Check `update_log.txt.defender.txt` for quarantine events
2. Check Windows Event Viewer → Application for crash details
3. Manually add Defender exclusion:
   ```powershell
   Add-MpPreference -ExclusionPath 'C:\RustyBot'
   ```
4. Run the installer manually (as Administrator): `RustyBot_Setup_v1.5.8.0.exe`

---

## Files Modified

- `auto_updater.py` - Updated `_create_windows_folder_update_script()` method
- All changes are backward-compatible (older versions will still work)

---

## Version Info

- **Current Version**: 1.5.8
- **Installer**: `RustyBot_Setup_v1.5.8.0.exe`
- **Standalone ZIP**: `RustyBot_v1.5.8_Standalone.zip`
- **Fix Date**: October 4, 2025

---

**Status**: ✅ All fixes implemented and tested via simulation. Ready for GitHub Release and real-world testing.
