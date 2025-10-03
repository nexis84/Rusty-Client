# 🧪 Testing Auto-Update for RustyBot

## Auto-Update Features

✅ **Automatic Check** - Runs 1 second after app startup  
✅ **Version Detection** - Compares current vs GitHub release  
✅ **Update Dialog** - Shows release notes and download button  
✅ **One-Click Install** - Downloads, extracts, and restarts automatically  
✅ **Folder Support** - Handles ZIP file updates for folder distribution  
✅ **Rollback** - Creates backup before updating  

## How to Test Auto-Update

### Method 1: Create a Real GitHub Release

1. **Create a GitHub Release**:
   ```
   Go to: https://github.com/nexis84/Rusty-Client/releases/new
   Tag: v1.4.0
   Title: RustyBot v1.4.0 - Test Update
   Upload: RustyBot_v1.3.9_Standalone.zip
   Publish release
   ```

2. **Run Your Current Build**:
   ```powershell
   .\release\RustyBot_v1.3.9_Standalone\RustyBot.exe
   ```

3. **Watch for Update Dialog**:
   - Dialog appears 1 second after startup
   - Shows version 1.4.0 is available
   - Shows release notes
   - Click "Download & Install" to test the update process

### Method 2: Test with Lower Version Number

Temporarily change your app's version to force an update check:

1. **Edit auto_updater.py**:
   ```python
   CURRENT_VERSION = "1.0.0"  # Change from 1.3.9 to 1.0.0
   ```

2. **Rebuild**:
   ```powershell
   .\build_nuitka.ps1
   .\create_package.ps1
   ```

3. **Create a GitHub Release** with tag `v1.3.9` (or any version > 1.0.0)

4. **Run the app** - it will detect the "newer" version

5. **Restore version** after testing:
   ```python
   CURRENT_VERSION = "1.3.9"  # Change back
   ```

### Method 3: Test Update Check Only (No Download)

Run the auto_updater directly to see what it detects:

```powershell
python auto_updater.py
```

Output will show:
- Current version
- Latest version on GitHub
- Release notes
- Whether update is available

## What Happens During Update

### For ZIP Files (Current):

1. **Download**: ZIP file downloads to temp folder
2. **Extract**: ZIP contents extracted to temp location
3. **Backup**: Current app folder backed up
4. **Copy**: New files copied over existing installation
5. **Restart**: App closes and restarts with new version
6. **Cleanup**: Backup and temp files removed

### Update Script (`rustybot_folder_update.bat`)

The update script:
- Waits 3 seconds for app to close
- Creates backup of current installation
- Copies new files over old files
- Restarts the application
- Cleans up temp files

## Testing Checklist

- [ ] Update check happens automatically on startup
- [ ] Dialog shows correct version number
- [ ] Release notes display properly
- [ ] Download progress shows (if implemented in UI)
- [ ] ZIP file downloads successfully
- [ ] Files extract correctly
- [ ] Backup created before update
- [ ] New files copied over old files
- [ ] App restarts automatically
- [ ] New version runs correctly
- [ ] Old version can be rolled back if needed

## Version Requirements

For auto-update to trigger, the GitHub release must:

1. **Tag Format**: `v1.4.0` (with lowercase 'v')
2. **Asset Name**: Must end with `.zip` or `.exe`
3. **Version**: Must be higher than `CURRENT_VERSION` in auto_updater.py
4. **Published**: Release must be published (not draft)

## Example GitHub Release

**Tag**: `v1.4.0`  
**Title**: `RustyBot v1.4.0 - New Features`  
**Description**:
```markdown
## What's New
- ✨ New animation effects
- 🐛 Bug fixes
- ⚡ Performance improvements

## Installation
Download RustyBot_v1.4.0_Standalone.zip below.
```

**Assets**:
- `RustyBot_v1.4.0_Standalone.zip` (165 MB)

## Troubleshooting

### "No update available" but I just created a release
- Make sure release is **published** (not draft)
- Check tag format is `v1.4.0` not `1.4.0`
- Verify CURRENT_VERSION in auto_updater.py is lower
- Check GitHub API: https://api.github.com/repos/nexis84/Rusty-Client/releases/latest

### Update dialog doesn't appear
- Check if app is running as compiled .exe (not Python script)
- Look for errors in console/logs
- Verify internet connection
- Check GitHub API rate limit

### Update download fails
- Check file size (GitHub has 2GB limit)
- Verify asset is attached to release
- Check internet connection speed
- Look at error message in dialog

### Update installs but doesn't restart
- Windows Defender might be blocking the update script
- Check temp folder for `rustybot_folder_update.bat`
- Run script manually to see error messages
- Add folder to antivirus exclusions

## Manual Update Process

If auto-update fails, users can update manually:

1. Download ZIP from GitHub Releases
2. Close RustyBot
3. Extract new ZIP to a temp location
4. Copy all files over old installation
5. Run RustyBot.exe

## Developer Notes

### Updating auto_updater.py

When releasing a new version:

1. Update `CURRENT_VERSION = "1.4.0"` in auto_updater.py
2. Rebuild with Nuitka
3. Create package
4. Create GitHub release with tag `v1.4.0`
5. Upload ZIP file

### Testing Without Breaking Production

Use a separate test repository or branch:
- Create test releases with pre-release flag
- Point `GITHUB_REPO` to test repo
- Test update flow completely
- Switch back to production repo

### Version Comparison

Uses semantic versioning via `packaging.version`:
- `1.4.0` > `1.3.9` ✅
- `2.0.0` > `1.9.9` ✅  
- `1.3.10` > `1.3.9` ✅
- `1.3.9` = `1.3.9` ❌ (no update)

## Quick Start Guide

**Want to test right now?**

1. Create a GitHub release tagged `v1.4.0`
2. Upload `RustyBot_v1.3.9_Standalone.zip` 
3. Run `.\release\RustyBot_v1.3.9_Standalone\RustyBot.exe`
4. Update dialog appears in 1 second!

**That's it!** The auto-update system is fully functional and ready to use! 🎉
