# RustyBot - Nuitka Build Guide

## Why Nuitka?

We switched from PyInstaller to Nuitka to avoid **Windows Defender false positives**. Nuitka compiles Python to C code and then to native machine code, which makes it:

- ✅ **Less likely to be flagged by antivirus** - Real compilation vs. runtime unpacking
- ✅ **Smaller executable size** - 124 MB (Nuitka) vs 189 MB (PyInstaller)
- ✅ **Better performance** - Compiled code runs faster than interpreted
- ✅ **No unpacking at runtime** - Everything is truly compiled

## Prerequisites

```powershell
# Install Nuitka and dependencies
pip install nuitka ordered-set zstandard
```

## Building

### Step 1: Build the Application

```powershell
.\build_nuitka.ps1
```

The build process:
1. **First build**: Takes 5-10 minutes (downloads MinGW GCC compiler)
2. **Subsequent builds**: 3-5 minutes (uses cached compilation)
3. **Output**: `dist\Main.dist\` folder with all files

### Step 2: Create Distribution Package

```powershell
.\create_package.ps1
```

This creates:
- **Folder**: `release\RustyBot_v1.3.9_Standalone\` with all files
- **ZIP**: `release\RustyBot_v1.3.9_Standalone.zip` (165 MB) - Upload this to GitHub!

## Build Output

- `dist\Main.dist\` - Application folder with all DLLs and dependencies
- `release\RustyBot_v1.3.9_Standalone.zip` - **Upload this to GitHub Releases**
- `release\RustyBot_v1.3.9_Standalone\` - Extracted folder for testing
- `Main.build/` - Build artifacts (ignored by git)

## What's Included

The executable includes:
- ✅ Python runtime (compiled to C)
- ✅ All dependencies (PyQt6, TwitchIO, pygame, etc.)
- ✅ Assets folder (HTML, JS, CSS files)
- ✅ Sounds folder (all .wav files)
- ✅ Fonts folder (custom fonts)
- ✅ config.json (settings)
- ✅ .env file (Twitch credentials)

## Antivirus Comparison

### PyInstaller
- ❌ Frequently flagged by Windows Defender
- ❌ Requires manual exclusions on every client PC
- ❌ Downloads may be blocked by browsers
- ⚠️ Users see scary warning messages

### Nuitka
- ✅ Rarely flagged (true compilation)
- ✅ No runtime unpacking behavior
- ✅ Clean downloads
- ✅ Better user experience

## Known Issues

### Icon Error
The icon file (`icon.ico`) causes an error during Nuitka post-processing. Currently building without icon. To add icon later:
- Convert icon to simpler format
- Or use `--windows-icon-from-exe` to copy from another exe
- Or use resource hacker after build

## Build Script Details

The `build_nuitka.ps1` script:
- Checks if Nuitka is installed
- Cleans previous build folders
- Compiles with these flags:
  - `--standalone` - Include all dependencies
  - `--onefile` - Single executable file
  - `--windows-disable-console` - No console window
  - `--enable-plugin=pyqt6` - PyQt6 support
  - Includes all data files and directories
  - Sets company name, product name, version info
- Shows file size after successful build

## Deployment

1. Build the application: `.\build_nuitka.ps1`
2. Create distribution package: `.\create_package.ps1`
3. Test locally: `.\release\RustyBot_v1.3.9_Standalone\RustyBot.exe`
4. Upload `RustyBot_v1.3.9_Standalone.zip` to GitHub Releases
5. Users download, extract ZIP, and run RustyBot.exe
6. Auto-update feature checks for new releases

**Note**: Users need to extract the entire ZIP file. All DLL files and folders must stay together!

## Troubleshooting

### "gcc not found"
Nuitka will automatically download MinGW GCC on first run. Just press Enter when prompted.

### Build fails
- Check Python version (requires 3.8+)
- Update Nuitka: `pip install --upgrade nuitka`
- Clear cache: Delete `C:\Users\<username>\AppData\Local\Nuitka\`

### Executable won't run
- Make sure all dependencies are installed
- Check that `.env` file exists in project root before build
- Verify `config.json` exists

### Still getting antivirus warnings?
Very rare with Nuitka, but if it happens:
- Build again (compiler randomness may help)
- Submit false positive report to Microsoft
- Consider code signing certificate ($100-400/year)

## Performance Notes

Nuitka-compiled code typically runs **faster** than PyInstaller because:
- No runtime unpacking needed
- True native compilation
- Better optimization opportunities

## Additional Resources

- [Nuitka Documentation](https://nuitka.net/doc/user-manual.html)
- [Nuitka Commercial](https://nuitka.net/doc/commercial.html) - For even better optimization
- [GitHub Issues](https://github.com/Nuitka/Nuitka/issues) - Community support
