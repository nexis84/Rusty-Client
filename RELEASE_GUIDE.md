# 🚀 Quick Start: Creating Your First Release

## Step 1: Build the Executable

```powershell
# Make sure you have dependencies installed
pip install pyinstaller packaging

# Run the build script
.\build.ps1
```

The executable will be created at: `dist\RustyBot\RustyBot.exe`

## Step 2: Test the Executable

Before releasing, test thoroughly:
```powershell
.\dist\RustyBot\RustyBot.exe
```

Check:
- ✅ Application starts correctly
- ✅ All UI elements display properly
- ✅ Sound effects work
- ✅ Animations load
- ✅ Twitch connection works

## Step 3: Create a GitHub Release

### Option A: Using Web Browser (Easiest)

1. **Go to your repository:**
   https://github.com/nexis84/Rusty-Client

2. **Click "Releases"** (right sidebar)

3. **Click "Create a new release"**

4. **Fill in the details:**
   - **Tag version:** `v1.3.9` (must match version in `auto_updater.py`)
   - **Release title:** `RustyBot v1.3.9`
   - **Description:** 
     ```markdown
     ## 🎉 What's New
     
     - ✨ Auto-update functionality - Updates happen automatically!
     - 🔄 GitHub releases integration
     - 🛠️ Build system improvements
     - 🐛 Bug fixes and performance improvements
     
     ## 📥 Installation
     
     1. Download `RustyBot.exe` below
     2. Create a folder and move the .exe there
     3. Run it!
     
     ## 🔄 Updating
     
     Future updates will download and install automatically!
     ```

5. **Upload the executable:**
   - Drag and drop `dist\RustyBot\RustyBot.exe` into the "Attach binaries" area

6. **Click "Publish release"**

### Option B: Using GitHub CLI (Advanced)

```powershell
# Install GitHub CLI if you haven't (one-time)
winget install GitHub.cli

# Login to GitHub (one-time)
gh auth login

# Create the release
gh release create v1.3.9 `
  dist\RustyBot\RustyBot.exe `
  --title "RustyBot v1.3.9" `
  --notes "Initial release with auto-update functionality"
```

## Step 4: Verify the Release

1. **Check the release page:**
   https://github.com/nexis84/Rusty-Client/releases

2. **Verify:**
   - ✅ Tag is `v1.3.9`
   - ✅ `RustyBot.exe` is attached
   - ✅ Release is marked as "Latest"

3. **Test the download link:**
   - Download the .exe from the release page
   - Run it in a clean folder
   - Verify it works

## Step 5: Share with Users!

Your users can now:
1. Go to: https://github.com/nexis84/Rusty-Client/releases/latest
2. Download `RustyBot.exe`
3. Run it!

Future updates will happen automatically! 🎉

---

## 🔄 For Future Updates

When you want to release a new version:

### 1. Update the version number

Edit `auto_updater.py`:
```python
CURRENT_VERSION = "1.4.0"  # Change this
```

### 2. Build the new executable
```powershell
.\build.ps1
```

### 3. Create a new release
Use the same process as above, but with the new version number (e.g., `v1.4.0`)

### 4. That's it!
Users will be automatically notified of the update when they launch the app!

---

## 📝 Tips

- **Version Numbers:** Always use semantic versioning (e.g., 1.4.0, 1.4.1)
- **Tag Format:** Always prefix with `v` (e.g., v1.4.0)
- **Release Notes:** Be descriptive! Users want to know what changed
- **Testing:** Always test the built .exe before releasing
- **Backup:** Keep a copy of working versions

## 🐛 Troubleshooting

### "Build failed"
- Check all dependencies are installed: `pip install -r requirements.txt`
- Ensure `icon.ico` exists
- Verify all asset folders exist (`assets/`, `sounds/`, `Fonts/`)

### "Auto-update not working"
- Verify the tag format is correct: `v1.3.9` (with lowercase v)
- Check that `RustyBot.exe` is attached to the release
- Ensure version in `auto_updater.py` matches the tag (without the v)

### "Users can't download"
- Make sure the release is published (not draft)
- Check that the repository is public (or users have access)

---

## 🎯 Checklist Before Each Release

- [ ] Update version in `auto_updater.py`
- [ ] Run `.\build.ps1` successfully
- [ ] Test the executable thoroughly
- [ ] Write clear release notes
- [ ] Create GitHub release with correct tag
- [ ] Upload `RustyBot.exe` to the release
- [ ] Test download link works
- [ ] Announce to users!

---

**Need Help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for more detailed instructions.
