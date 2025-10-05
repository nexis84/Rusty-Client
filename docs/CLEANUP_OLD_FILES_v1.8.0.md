# RustyBot v1.8.0 - Old Files Cleanup

## Overview
Added automatic cleanup functionality to remove old/unused files from previous versions of RustyBot. This ensures a clean installation and prevents conflicts with deprecated files.

## Changes Made

### 1. Auto Updater (`auto_updater.py`)

#### New Cleanup Function
Added `_cleanup_old_files()` method that removes deprecated files:
- `Launcher.exe` - Old launcher no longer used
- `Main.exe` - Old main executable name
- `RustyBot_Web_Updater.exe` - Deprecated web updater
- `simple_launcher.py` - Old launcher script
- `launcher.py` - Old launcher script
- `transition_launcher.py` - Old launcher script

#### Update Script Improvements
**Version Updated:** 1.5.0 → 1.8.0

**Added Cleanup Steps:**
- Deletes old files after successful update
- Logs each file removal
- Continues even if files don't exist (silent cleanup)

**Fixed DLL Errors:**
- Increased wait time before restart from 2 to 10 seconds
- Added explicit directory change (`cd /d`) before restart
- Ensures all file handles are released before application restart
- Added final 2-second grace period after restart command

### 2. Build Script (`rustyupdate.ps1`)

#### Package Cleanup
Added automatic removal of old files when creating standalone ZIP:
```powershell
# Clean up old unused files from the package
$oldFiles = @(
    "Launcher.exe",
    "Main.exe",
    "RustyBot_Web_Updater.exe",
    "simple_launcher.py",
    "launcher.py",
    "transition_launcher.py"
)
```

Ensures clean distribution packages without deprecated files.

### 3. Installer Script (`installer_improved.iss`)

#### Post-Install Cleanup
Added `CurStepChanged` procedure enhancement:
- Checks for old files after installation
- Removes deprecated files if found
- Logs each removal operation
- Runs before security configuration (Defender/Firewall)

**Files Removed:**
1. `Launcher.exe`
2. `Main.exe`
3. `RustyBot_Web_Updater.exe`
4. `simple_launcher.py`
5. `launcher.py`
6. `transition_launcher.py`

## Benefits

### For Users
1. **Cleaner Installation** - No leftover files from previous versions
2. **No Confusion** - Only current executable present
3. **Reduced Disk Space** - Old redundant files removed
4. **Fewer Errors** - Eliminates DLL loading issues on restart

### For Developers
1. **Easier Maintenance** - Deprecated code automatically removed
2. **Clean Transition** - Smooth migration from launcher to direct execution
3. **Better Logging** - Track which files are being cleaned up
4. **Consistent State** - All installations have same file structure

## Testing Recommendations

### Before Release
1. ✅ Test clean install (no old files)
2. ✅ Test upgrade from v1.7.x (with old files)
3. ✅ Verify auto-update doesn't cause DLL errors
4. ✅ Check all old files are removed
5. ✅ Confirm RustyBot.exe launches correctly after update

### Scenarios to Test
- **Clean Install:** Fresh installation on new system
- **Update from 1.7.x:** System with Launcher.exe present
- **Manual Update:** Using Check for Updates in Options
- **Installer Update:** Using the .exe installer
- **ZIP Update:** Extracting standalone ZIP over old installation

## Notes

### Why 10 Second Wait?
The extended wait time (10 seconds) before restart ensures:
- All DLL handles are released
- Windows file system cache is flushed
- QtWebEngine processes are fully terminated
- No file locking conflicts on restart

### Silent Cleanup
All cleanup operations are "silent" - they won't fail if files don't exist:
```batch
del /F /Q "file.exe" 2>nul
```
This prevents errors on clean installations where old files never existed.

## Future Improvements

### Potential Enhancements
1. Add cleanup history log (track what was removed)
2. Report cleanup results to user in UI
3. Add option to skip cleanup (for debugging)
4. Create cleanup utility as standalone tool
5. Add version-specific cleanup logic

### Configuration
Consider adding a `cleanup_config.json`:
```json
{
  "cleanup_enabled": true,
  "files_to_remove": [
    "Launcher.exe",
    "Main.exe"
  ],
  "wait_before_restart": 10
}
```

## Version History

- **v1.8.0** - Initial cleanup implementation
  - Added old file removal
  - Fixed DLL restart errors
  - Updated installer cleanup
  - Enhanced build script cleanup

---

**Last Updated:** October 6, 2025  
**Version:** 1.8.0  
**Status:** Implemented ✅
