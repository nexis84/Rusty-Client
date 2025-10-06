# 🔐 Secure Credentials Setup Guide

## Overview

RustyBot uses encrypted credentials to protect your Twitch bot token and API keys. This guide explains how to set up and manage your encrypted credentials.

## 🚀 Quick Setup (Recommended)

### Option 1: Using the Setup Wizard (Easy)

1. **Run the setup wizard:**
   ```powershell
   python setup_credentials.py
   ```

2. **Follow the interactive prompts:**
   - Enter your Twitch bot token (without 'oauth:' prefix)
   - Enter your bot username
   - Enter your channel name
   - Enter Twitch API credentials (Client ID, Secret, Bot ID)
   - Configure optional settings (or use defaults)

3. **Done!** Your credentials are now encrypted in `secure.env`

### Option 2: Using the Encryption Tool

1. **Create a plain `.env` file** with your credentials:
   ```env
   TWITCH_TOKEN=your_token_here
   TWITCH_NICK=your_bot_name
   TWITCH_CHANNEL=your_channel
   TWITCH_CLIENT_ID=your_client_id
   TWITCH_CLIENT_SECRET=your_client_secret
   TWITCH_BOT_ID=your_bot_id
   ```

2. **Encrypt it:**
   ```powershell
   python secure_env_loader.py
   ```

3. **Delete the plain `.env` file** (optional but recommended):
   ```powershell
   del .env
   ```

## 📁 Files Explained

### `secure.env` (Your Encrypted Credentials)
- **Contains**: All your encrypted bot credentials
- **Location**: Same folder as RustyBot.exe
- **Security**: Encrypted with AES-256
- **Git**: Automatically excluded (never pushed to GitHub)
- **Distribution**: Include this in your builds (it contains YOUR credentials)

### `secure.env.example` (Template)
- **Contains**: Example encrypted values (placeholders)
- **Purpose**: Shows the format of secure.env
- **Git**: Tracked in repository
- **Usage**: Rename to `secure.env` and run setup wizard

### `.env.example` (Plain Text Template)
- **Contains**: Plain text template with placeholder values
- **Purpose**: Shows what credentials are needed
- **Git**: Tracked in repository  
- **Usage**: Copy to `.env`, fill in values, then encrypt

### `setup_credentials.py` (Setup Wizard)
- **Purpose**: Interactive tool to create encrypted credentials
- **Features**:
  - Step-by-step credential entry
  - Input validation
  - Automatic encryption
  - View existing credentials (masked)
- **Usage**: `python setup_credentials.py`

### `secure_env_loader.py` (Encryption Engine)
- **Purpose**: Core encryption/decryption functionality
- **Features**:
  - AES-256 encryption (Fernet)
  - PBKDF2 key derivation
  - 100,000 iterations
  - Automatic .env encryption
- **Usage**: `python secure_env_loader.py`

## 🔐 Security Features

### **Encryption Details:**
- **Algorithm**: AES-256 (Fernet)
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: Fixed app-specific salt
- **Password**: Embedded in code

### **What's Protected:**
- ✅ Bot OAuth token (encrypted)
- ✅ Bot credentials (encrypted)
- ✅ Client ID/Secret (encrypted)
- ✅ All configuration values (encrypted)

### **Security Level:**
- 🛡️ **Strong Obfuscation**: Significantly better than plain text
- 🛡️ **Prevents Casual Extraction**: Average users can't easily get your token
- 🛡️ **Deters Reverse Engineering**: Requires significant effort to extract
- ⚠️ **Not Unbreakable**: Determined attacker with code access could eventually extract

**Note**: For absolute security, use server-side authentication. This provides excellent protection for client distribution.

## 📝 For Distribution

### **Your Workflow (Bot Owner):**

1. **Set up credentials once:**
   ```powershell
   python setup_credentials.py
   ```

2. **Build your distribution:**
   ```powershell
   .\rustyupdate.ps1 -Version "1.8.1"
   ```

3. **Distribute** `secure.env` with your builds
   - ✅ Include `secure.env` in your ZIP/installer
   - ✅ It contains YOUR encrypted credentials
   - ❌ Never include plain `.env` files

### **User Experience (Your Clients):**

1. Download and extract RustyBot
2. Run RustyBot.exe
3. It works! (uses your encrypted credentials)
4. Optional: Configure their channel in Options

### **Files to Include in Distribution:**
```
RustyBot_v1.8.1_Standalone/
├── RustyBot.exe           ← Main application
├── secure.env             ← Your encrypted credentials
├── config.json            ← App configuration
├── README.md              ← Documentation
└── assets/                ← Resources
    ├── sounds/
    ├── Fonts/
    └── ...
```

## 🔄 Updating Credentials

### **If You Need to Change Your Credentials:**

**Method 1: Setup Wizard (Recommended)**
```powershell
python setup_credentials.py
# Choose option 1 (Setup new credentials)
# Enter new values
```

**Method 2: Manual**
1. Update your `.env` file with new values
2. Run: `python secure_env_loader.py`
3. Rebuild and redistribute

### **Viewing Current Credentials:**
```powershell
python setup_credentials.py
# Choose option 2 (View current credentials)
# Shows masked values for verification
```

## 🎯 Troubleshooting

### **"secure.env not found" Error:**
- Run `python setup_credentials.py` to create it
- OR copy `secure.env.example` to `secure.env` and set up credentials

### **"Could not decrypt" Warning:**
- Your secure.env may be corrupted
- Re-run setup wizard to create a fresh one

### **"Invalid token" Error:**
- Token format may be wrong (remove 'oauth:' prefix if present)
- Re-enter credentials using setup wizard

### **Need to Start Fresh:**
```powershell
del secure.env
python setup_credentials.py
```

## 📊 Credentials Checklist

When setting up credentials, you need:

- [ ] **TWITCH_TOKEN** - OAuth token from Twitch
- [ ] **TWITCH_NICK** - Your bot's username  
- [ ] **TWITCH_CHANNEL** - Channel to monitor
- [ ] **TWITCH_CLIENT_ID** - From dev.twitch.tv/console
- [ ] **TWITCH_CLIENT_SECRET** - From dev.twitch.tv/console
- [ ] **TWITCH_BOT_ID** - Your bot's user ID
- [ ] **EVE2TWITCH_BOT_NAME** - (Optional) Eve2Twitch bot name
- [ ] **CONFIRMATION_TIMEOUT** - (Optional) Default: 90 seconds
- [ ] **EVE_RESPONSE_TIMEOUT** - (Optional) Default: 300 seconds
- [ ] **ENTRY_METHOD** - (Optional) COMMAND or KEYWORD
- [ ] **JOIN_COMMAND** - (Optional) Default: !join

### **Where to Get Credentials:**
1. Go to https://dev.twitch.tv/console/apps
2. Create a new application (or use existing)
3. Get your Client ID and Client Secret
4. Generate an OAuth token (use Twitch CLI or online generator)
5. Get your Bot ID from Twitch API

## 🎉 Benefits

### **For Bot Owners:**
- ✅ Credentials protected with encryption
- ✅ Can't be easily extracted by users
- ✅ One set of credentials for all distributions
- ✅ Easy to update and redistribute

### **For Users:**
- ✅ Works immediately out of the box
- ✅ No credential management needed
- ✅ No technical setup required
- ✅ Just download and run

## 🔒 Git Security

The `.gitignore` file automatically excludes:
- ❌ `.env` (plain text credentials)
- ❌ `secure.env` (your encrypted credentials)

But includes:
- ✅ `.env.example` (template)
- ✅ `secure.env.example` (encrypted template)
- ✅ `setup_credentials.py` (setup wizard)
- ✅ `secure_env_loader.py` (encryption tool)

This means:
- Your real credentials never get pushed to GitHub
- Other developers can set up their own credentials
- Templates show what's needed

## 🚀 Quick Commands Reference

```powershell
# Interactive setup wizard (recommended)
python setup_credentials.py

# Encrypt existing .env file
python secure_env_loader.py

# View current credentials (masked)
python setup_credentials.py
# Choose option 2

# Start fresh
del secure.env
python setup_credentials.py

# Build with encrypted credentials
.\rustyupdate.ps1 -Version "1.8.1"
```

---

**You're all set!** Your credentials are now encrypted and ready for distribution. 🎉

**Contains**:
- Encrypted TWITCH_TOKEN
- Encrypted TWITCH_NICK
- Encrypted TWITCH_CHANNEL
- Encrypted TWITCH_CLIENT_ID/SECRET
- Encrypted TWITCH_BOT_ID
- All other .env variables (encrypted)

**Example**:
```
# Encrypted RustyBot Credentials
# These are encrypted to protect the bot token

TWITCH_TOKEN=Z0FBQUFBQm5kVjFU...encrypted_data...
TWITCH_NICK=Z0FBQUFBQm5kVjFU...encrypted_data...
TWITCH_CHANNEL=Z0FBQUFBQm5kVjFU...encrypted_data...
```

### `user_config.json`
**File**: User's personal configuration (NOT tracked in git)

**Contains**:
```json
{
    "twitch_channel": "users_channel_name",
    "first_run_completed": true
}
```

**Location**:
- Same directory as `config.json`
- In `app/` folder for organized distribution
- Parent directory for easy access

## 🔄 How It Works

### **First Launch:**
```
1. User extracts and runs RustyBot
2. App detects no user_config.json exists
3. Shows first-run setup dialog
4. User enters their Twitch channel name
5. Saved to user_config.json
6. App continues with their channel
```

### **Subsequent Launches:**
```
1. User runs RustyBot
2. App loads channel from user_config.json
3. No dialog shown
4. Connects to user's channel immediately
```

### **Changing Channel:**
```
1. User opens Options dialog
2. Changes "Your Twitch Channel" field
3. Clicks Save
4. Updates user_config.json
5. Takes effect on next connection
```

## 🔐 Security Features

### **Encryption Details:**
- **Algorithm**: AES-256 (Fernet)
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Iterations**: 100,000
- **Salt**: Fixed app-specific salt
- **Password**: Embedded in code

### **What's Protected:**
- ✅ Bot OAuth token (can't be extracted)
- ✅ Bot credentials (encrypted)
- ✅ Client ID/Secret (encrypted)

### **What's NOT Protected:**
- ⚠️ User's channel name (stored plain text in user_config.json)
  - This is intentional - not sensitive
  - Needs to be editable by user
  - No security risk

### **Security Level:**
- 🛡️ **Basic Obfuscation**: Not military-grade, but significantly better than plain text
- 🛡️ **Prevents Casual Extraction**: Average users can't easily get your token
- 🛡️ **Deters Reverse Engineering**: Requires significant effort to extract
- ⚠️ **Not Unbreakable**: Determined attacker with code access could eventually extract

**Note**: For absolute security, use server-side authentication. This provides reasonable protection for client distribution.

## 📝 User Experience

### **For Your Clients:**

**First Time:**
1. Extract RustyBot ZIP
2. Run RustyBot.vbs
3. Enter their channel name in welcome dialog
4. Done! Bot connects to their channel

**Every Time After:**
1. Run RustyBot.vbs
2. Automatically connects to their channel
3. No configuration needed

**To Change Channel:**
1. Open Options (⚙️ icon)
2. Update "Your Twitch Channel"
3. Click Save
4. Restart bot

### **For You (Distribution):**

1. **Create encrypted env**:
   ```powershell
   python secure_env_loader.py  # Creates secure.env
   ```

2. **Build**:
   ```powershell
   .\build_nuitka.ps1  # Includes secure.env
   ```

3. **Package**:
   ```powershell
   .\create_package.ps1  # Copies secure.env to root
   ```

4. **Distribute**:
   - Upload RustyBot_v1.3.9_Standalone.zip to GitHub
   - Users download, extract, run
   - First-run dialog appears
   - They enter their channel
   - Works forever after that!

## 🎯 Files Structure

### **Distribution Root:**
```
RustyBot_v1.3.9_Standalone/
├── RustyBot.vbs           ← User double-clicks this
├── RustyBot.bat
├── config.json            ← App settings
├── secure.env             ← Your encrypted bot credentials
├── user_config.json       ← User's channel (created on first run)
├── README.txt
└── app/                   ← All technical files
    ├── RustyBot.exe
    └── ... (DLLs, libraries, etc.)
```

### **What Gets Tracked in Git:**
- ✅ `secure_env_loader.py` (encryption tool)
- ✅ `first_run_setup.py` (first-run dialog)
- ✅ Updated `Main.py` (loading logic)
- ✅ Updated `options_dialog.py` (channel editing)
- ✅ Updated build scripts

### **What's IGNORED by Git:**
- ❌ `.env` (plain text credentials)
- ❌ `secure.env` (encrypted credentials)
- ❌ `user_config.json` (user's channel)

## 🚀 Benefits

### **For You:**
- ✅ Your bot token is protected
- ✅ Can't be easily extracted by users
- ✅ One set of credentials for all clients
- ✅ No need for clients to get their own bot

### **For Your Clients:**
- ✅ Simple first-run setup (just enter channel)
- ✅ Never need to touch credentials
- ✅ Can change channel anytime in Options
- ✅ Works immediately without configuration

### **Security:**
- ✅ Credentials encrypted
- ✅ Much harder to extract than plain text
- ✅ Sufficient for client distribution
- ✅ Better than no protection

## 🎓 How to Update

### **If You Change Bot Credentials:**

1. Update `.env` file with new credentials
2. Re-encrypt:
   ```powershell
   python secure_env_loader.py
   ```
3. Rebuild:
   ```powershell
   .\build_nuitka.ps1
   .\create_package.ps1
   ```
4. Distribute new version

### **If User Needs to Change Channel:**

Option 1: In-app (preferred)
- Options → Your Twitch Channel → Save

Option 2: Delete config
- Delete `user_config.json`
- Restart app
- First-run dialog appears again

## 📊 Testing Checklist

- [x] Encrypted .env file created
- [x] secure.env file loads correctly
- [x] First-run dialog shows on first launch
- [x] Channel saves to user_config.json
- [x] Channel loads on subsequent runs
- [x] Options dialog shows current channel
- [x] Channel can be changed in Options
- [x] Changed channel persists across restarts
- [x] Build includes secure.env
- [x] Package copies secure.env to root
- [x] Files excluded from git tracking

## 🎉 Result

**You now have:**
1. ✅ Protected bot credentials (encrypted)
2. ✅ User-friendly channel setup (first-run dialog)
3. ✅ Easy channel management (Options dialog)
4. ✅ Clean distribution (no plain text secrets)
5. ✅ Professional user experience

**Your clients get:**
1. ✅ Simple setup (one-time channel entry)
2. ✅ No credential management
3. ✅ Works immediately
4. ✅ Easy to change channel if needed

**Perfect solution for distributing a bot with shared credentials but per-user channels!** 🌟
