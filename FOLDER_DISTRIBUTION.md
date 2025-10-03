# 📦 RustyBot - Folder-Based Distribution

## Why Folder Distribution?

We switched from single-file EXE to **folder-based distribution** because:

- ✅ **Much less likely to trigger antivirus** - No compression/packing that looks suspicious
- ✅ **Smaller download** - 165 MB ZIP vs 189 MB single EXE
- ✅ **Faster startup** - No unpacking needed
- ✅ **Better compatibility** - All DLLs visible to Windows
- ✅ **Easier debugging** - Can see all components

## 📥 For Users: How to Install

### Download & Extract

1. **Download** `RustyBot_v1.3.9_Standalone.zip` from [GitHub Releases](https://github.com/nexis84/Rusty-Client/releases)
2. **Right-click** the ZIP file → **Extract All**
3. **Choose a location** (e.g., `C:\RustyBot\`)
4. **Open** the extracted folder
5. **Double-click** `RustyBot.exe` to run!

### Alternative: Use the Launcher

You can also double-click `Start_RustyBot.bat` which will launch the application.

### ⚠️ Important

**DO NOT move RustyBot.exe out of the folder!**

The .exe needs all the DLL files and folders that are in the same directory:
- `assets/` - Web animations
- `sounds/` - Sound effects  
- `Fonts/` - Custom fonts
- `config.json` - Settings
- `.env` - Credentials
- Plus ~100 DLL files for Python, PyQt6, etc.

## 🛡️ Antivirus Handling

Folder-based distributions are **much less suspicious** to antivirus software because:

1. **No packing/compression** - Everything is visible
2. **No runtime unpacking** - No suspicious behavior
3. **Standard DLLs** - Windows recognizes Qt, Python, etc.
4. **Multiple files** - Looks like a normal application

### If Windows Defender Still Blocks

Very rare, but if it happens:

1. **Click "More info"** → **"Run anyway"**
2. **Or add folder to exclusions**:
   - Open Windows Security
   - Virus & threat protection → Manage settings
   - Exclusions → Add or remove exclusions
   - Choose "Folder" and select the RustyBot folder

## 🔄 Updates

The auto-update system works perfectly with folder distribution:

1. App detects new version on GitHub
2. Downloads new ZIP file
3. Extracts to a temporary location
4. Replaces old files with new ones
5. Restarts automatically

Users never have to manually download updates!

## 📊 Size Comparison

| Distribution Type | Download Size | Extracted Size | AV Detection |
|-------------------|---------------|----------------|--------------|
| PyInstaller Single EXE | 189 MB | 189 MB | ❌ High |
| Nuitka Single EXE | 124 MB | 124 MB | ❌ Medium |
| **Nuitka Folder (ZIP)** | **165 MB** | **413 MB** | **✅ Low** |

## 🛠️ For Developers: Creating Releases

### Build Process

```powershell
# Step 1: Build with Nuitka
.\build_nuitka.ps1

# Step 2: Create distribution package
.\create_package.ps1
```

Output:
- `release\RustyBot_v1.3.9_Standalone.zip` - Upload this to GitHub Releases

### What's Included in ZIP

```
RustyBot_v1.3.9_Standalone/
├── RustyBot.exe           # Main executable
├── Start_RustyBot.bat     # Launcher script
├── README.txt             # User instructions
├── assets/                # Web resources
├── sounds/                # Sound effects
├── Fonts/                 # Custom fonts
├── config.json            # Configuration
├── .env                   # Twitch credentials
├── PyQt6/                 # Qt libraries
├── pygame/                # Game library
├── certifi/               # SSL certificates
└── ~100 DLL files         # Python + dependencies
```

### Upload to GitHub

1. Go to https://github.com/nexis84/Rusty-Client/releases/new
2. Tag: `v1.3.9`
3. Title: `RustyBot v1.3.9 - Folder Distribution`
4. Upload: `RustyBot_v1.3.9_Standalone.zip`
5. Description:

```markdown
## 📦 Download & Install

1. Download `RustyBot_v1.3.9_Standalone.zip`
2. Extract the ZIP file
3. Run `RustyBot.exe` from the extracted folder
4. That's it!

## ✨ What's New

- ✅ Folder-based distribution (much less antivirus issues!)
- ✅ Auto-update functionality
- ✅ Smaller download size (165 MB)
- ✅ Faster startup (no unpacking)

## 📝 Important

**Extract the entire ZIP file!** All files must stay together.
Don't move RustyBot.exe out of the folder.

## 🛡️ Antivirus Note

This folder-based distribution is much less likely to trigger
antivirus warnings compared to single-file EXEs!

If Windows Defender shows a warning:
- Click "More info" → "Run anyway"
- The app is completely safe and open source
```

## 🎯 Benefits Summary

### For Users
- ✅ Easy to install (extract and run)
- ✅ Fewer antivirus warnings
- ✅ Auto-updates work seamlessly
- ✅ Can see all components (transparency)

### For Developers
- ✅ Easier to build
- ✅ No complex packing configuration
- ✅ Better debugging (can inspect all files)
- ✅ Smaller download size

### For Distribution
- ✅ Upload one ZIP file
- ✅ Users extract and run
- ✅ Works on any Windows 10/11
- ✅ No installer needed

## 🔧 Troubleshooting

### "Missing DLL" Error
User didn't extract all files. Tell them to extract the entire ZIP.

### "Can't find assets" Error
User moved RustyBot.exe out of the folder. Tell them to keep all files together.

### Antivirus Still Blocks
Very rare with folder distribution. Add folder to exclusions.

### Updates Not Working
Check GitHub release has the ZIP file attached with correct version tag.

---

**This folder-based approach is the industry standard for distributing Qt/Python applications!**

Examples: OBS Studio, Discord (Electron), VS Code - all use folder distributions for the same reasons.
