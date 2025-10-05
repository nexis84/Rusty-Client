# 🔒 Windows Defender Blocking the Installer?

## The Problem

Windows Defender may block `Install.exe` from running because it's compiled with Nuitka (a Python-to-executable compiler). This is a **FALSE POSITIVE** - the installer is completely safe.

**Error you might see:**
```
Error, load DLL. ([Error 225] Operation did not complete successfully 
because the file contains a virus or potentially unwanted software.
```

## ✅ Solution 1: Use Run_Installer.bat (EASIEST)

Simply double-click **`Run_Installer.bat`** instead of `Install.exe`.

This batch file will:
1. Add Windows Defender exclusion for the current folder
2. Launch the GUI installer automatically
3. Everything works perfectly!

**Just double-click `Run_Installer.bat` and follow the prompts!**

---

## ✅ Solution 2: Manual Exclusion (if Solution 1 doesn't work)

1. **Extract the ZIP** to a folder (e.g., `C:\RustyBotSetup`)

2. **Add Windows Defender Exclusion:**
   - Open **Windows Security**
   - Go to **Virus & threat protection**
   - Click **Manage settings**
   - Scroll to **Exclusions**
   - Click **Add or remove exclusions**
   - Click **Add an exclusion** → **Folder**
   - Select the folder where you extracted the ZIP (e.g., `C:\RustyBotSetup`)

3. **Run the installer:**
   - Now double-click `Install.exe`
   - The GUI installer will launch without issues

---

## ✅ Solution 3: Use Script Installer Instead

If you don't want to deal with the GUI installer, use the script installer instead:

1. Double-click **`Install.bat`**
2. Follow the prompts in the console
3. It works without any Windows Defender issues!

---

## Why Does This Happen?

- RustyBot is compiled with **Nuitka** (Python → Executable converter)
- Many antivirus programs flag compiled Python applications as suspicious
- This is a **known false positive** with Nuitka-compiled applications
- **RustyBot is 100% safe** - check the source code: https://github.com/nexis84/Rusty-Client

---

## Still Having Issues?

1. **Try the script installer:** `Install.bat` (no GUI but works reliably)
2. **Manual installation:** See WINDOWS_DEFENDER_INSTRUCTIONS.md for manual setup steps
3. **Contact support:** Open an issue on GitHub

---

## ✅ Recommended: Use Run_Installer.bat

**The easiest way is to just use `Run_Installer.bat`** - it handles everything automatically!

Just double-click it and follow the beautiful GUI wizard. 🎉
