# RustyBot - Deployment & Auto-Update Guide

## Building the Executable

### Prerequisites
```bash
pip install pyinstaller packaging
```

### Build Process
1. **Run the build script:**
   ```powershell
   .\build.ps1
   ```

2. **The executable will be created at:**
   ```
   dist\RustyBot\RustyBot.exe
   ```

3. **Test the executable before releasing:**
   - Run `.\dist\RustyBot\RustyBot.exe`
   - Verify all features work correctly
   - Check that assets, sounds, and fonts load properly

## Creating a Release with Auto-Update

### 1. Update Version Number
Edit `auto_updater.py` and update the version:
```python
CURRENT_VERSION = "1.4.0"  # Increment this
```

### 2. Build the Executable
```powershell
.\build.ps1
```

### 3. Create GitHub Release

#### Option A: Using GitHub Web Interface
1. Go to: https://github.com/nexis84/Rusty-Client/releases/new
2. Click "Choose a tag" and create a new tag: `v1.4.0` (match your version)
3. Set release title: `RustyBot v1.4.0`
4. Add release notes describing changes
5. **Upload the executable:** `dist\RustyBot\RustyBot.exe`
6. Click "Publish release"

#### Option B: Using GitHub CLI
```powershell
# Install GitHub CLI if needed: winget install GitHub.cli

gh release create v1.4.0 `
  dist\RustyBot\RustyBot.exe `
  --title "RustyBot v1.4.0" `
  --notes "Release notes here"
```

## How Auto-Update Works

1. **On Startup:** The app checks GitHub for the latest release
2. **If Update Available:** User is prompted with version info and release notes
3. **User Accepts:** The new `.exe` is downloaded
4. **Installation:** Current executable is backed up and replaced
5. **Restart:** App restarts with the new version

## User Installation Instructions

### First-Time Setup
1. Download `RustyBot.exe` from the latest release
2. Create a folder (e.g., `C:\RustyBot\`)
3. Move the executable to that folder
4. Run `RustyBot.exe`

### Updates
- Updates happen automatically when available
- Users just click "Update" when prompted
- The app handles everything and restarts

## Distribution Methods

### Method 1: GitHub Releases (Recommended)
- Users download from: https://github.com/nexis84/Rusty-Client/releases/latest
- Auto-update works automatically
- Free hosting

### Method 2: Direct Download
- Host the `.exe` on your own server
- Update `GITHUB_API_URL` in `auto_updater.py` to point to your API
- Requires custom update API endpoint

## Troubleshooting

### Build Issues
- **Missing dependencies:** Run `pip install -r requirements.txt`
- **Icon not found:** Ensure `icon.ico` exists in project root
- **Assets missing:** Check that `assets/`, `sounds/`, `Fonts/` folders exist

### Auto-Update Issues
- **Update check fails:** Verify internet connection and GitHub access
- **Download fails:** Check firewall/antivirus settings
- **Update won't apply:** Run as administrator (Windows may block file replacement)

## Version History

- **v1.3.9** - Current version with auto-update support
- Future versions will be tracked in GitHub releases

## Configuration for Developers

### Building Without Auto-Update
If you want to disable auto-update for development builds:
1. Comment out the update check in `Main.py`
2. Or set `ENABLE_AUTO_UPDATE = False` in config

### Building Single-File Executable
To create a single `.exe` file instead of a folder:
1. Edit `RustyBot.spec`
2. Change `exe = EXE(` section to use `onefile=True`
3. Note: This increases startup time but simplifies distribution

## Security Notes

- Executables are downloaded over HTTPS from GitHub
- Original executable is backed up before update
- Update can be rolled back if it fails
- Users should only download from official GitHub releases

## Support

For issues or questions:
- GitHub Issues: https://github.com/nexis84/Rusty-Client/issues
- Check release notes for known issues
