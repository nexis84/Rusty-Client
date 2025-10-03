# 🛡️ IMPORTANT: Windows Defender Instructions

## ⚠️ Before You Extract!

**Windows Defender will block this application as a false positive.**

This is normal for compiled Python applications. RustyBot is 100% safe and open source.

### 📋 Setup Steps (FOLLOW IN ORDER!)

#### **Step 1: Download the ZIP**
- Download `RustyBot_v1.3.9_Standalone.zip`
- **DO NOT extract yet!**

#### **Step 2: Create Installation Folder**
- Create a folder where you want RustyBot (e.g., `C:\RustyBot` or `D:\Games\RustyBot`)
- Remember this location!

#### **Step 3: Add Windows Defender Exclusion**

**Before extracting**, add an exclusion to Windows Defender:

1. Open **Windows Security** (search in Start menu)
2. Click **"Virus & threat protection"**
3. Under "Virus & threat protection settings", click **"Manage settings"**
4. Scroll down to **"Exclusions"**
5. Click **"Add or remove exclusions"**
6. Click **"Add an exclusion"** → Select **"Folder"**
7. Browse to the folder you created in Step 2
8. Click **"Select Folder"**

✅ You should see your folder listed in exclusions

#### **Step 4: Extract the ZIP**
- Right-click `RustyBot_v1.3.9_Standalone.zip`
- Select **"Extract All..."**
- Extract to the folder you created in Step 2
- Click **"Extract"**

#### **Step 5: Run RustyBot**
- Open the extracted folder
- Double-click **`RustyBot.vbs`** (recommended) or **`RustyBot.bat`**
- First time: Enter your Twitch channel name
- Enjoy! 🎉

---

## 🤔 Why Windows Defender Blocks This

RustyBot is compiled from Python using Nuitka. This is a legitimate tool that:
- Converts Python code to executable files
- Makes the program faster and easier to distribute
- Unfortunately, triggers false positives in antivirus software

**This is completely normal and safe!**

- ✅ Open source: https://github.com/nexis84/Rusty-Client
- ✅ No malicious code
- ✅ Used by many Python developers
- ✅ You can review the source code yourself

---

## 🆘 Troubleshooting

### "Windows Defender deleted my files during extraction"
- You didn't add the exclusion before extracting
- Delete the partially extracted folder
- Follow Step 3 above to add exclusion
- Extract again

### "Can't add exclusion - Access Denied"
- You need Administrator rights on your PC
- Right-click Windows Security → Run as Administrator
- Try adding the exclusion again

### "Still getting blocked even with exclusion"
- Make sure you added the exclusion to the **folder**, not the ZIP file
- The exclusion must match the extraction path exactly
- Try restarting your computer after adding the exclusion

### "RustyBot.vbs does nothing when I double-click"
- The exe was quarantined by Windows Defender
- Check Windows Security → Protection history
- Restore `RustyBot.exe` if quarantined
- Make sure the exclusion is properly added

---

## 📞 Need Help?

- GitHub Issues: https://github.com/nexis84/Rusty-Client/issues
- Check the README.txt inside the extracted folder for more info

---

## 🔒 Alternative: Manual Restore

If Windows Defender quarantined files during extraction:

1. Open **Windows Security**
2. Click **"Virus & threat protection"**
3. Click **"Protection history"**
4. Find `RustyBot.exe` in the list
5. Click **"Actions"** → **"Restore"**
6. Add the folder exclusion (Step 3 above)
7. Run RustyBot again
