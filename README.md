# 🤖 RustyBot - EVE Online Twitch Giveaway Bot

[![Version](https://img.shields.io/badge/version-1.4.1-blue.svg)](https://github.com/nexis84/Rusty-Client/releases)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

A feature-rich Twitch giveaway bot for EVE Online with advanced animations, sound effects, and **automatic update functionality**.

## ✨ Features

- 🎯 **Twitch Integration** - Automatic participant tracking from chat
- 🎨 **Animated Winner Display** - Eye-catching web animations
- 🔊 **Sound Effects** - Customizable audio feedback
- 🎁 **Prize Management** - Queue and manage multiple prizes
- ⏱️ **Timer System** - Confirmation and response timers
- 🔄 **Auto-Update** - Automatically checks and installs updates from GitHub
- 🎮 **EVE2Twitch Integration** - Verify EVE Online character names
- 📊 **Analytics** - Track giveaway statistics

## 📥 Installation

### Professional One-Click Installer (Recommended)

1. **Download the installer:**
   - Visit [Releases](https://github.com/nexis84/Rusty-Client/releases/latest)
   - Download `RustyBot_Setup_v1.4.1.exe`

2. **Run the installer:**
   - Double-click the downloaded file
   - Follow the professional setup wizard
   - Choose installation location (default: `C:\Program Files\RustyBot`)
   - Select optional desktop shortcut
   - Click Install

3. **Launch RustyBot:**
   - Use the desktop shortcut (if created)
   - Or: Start Menu → RustyBot

**The installer automatically handles:**
- ✅ Windows Defender exclusion
- ✅ Windows Firewall configuration
- ✅ All file placement
- ✅ Desktop and Start Menu shortcuts

### For Developers

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nexis84/Rusty-Client.git
   cd Rusty-Client
   ```

2. **Install dependencies:**
   ```bash
   pip install nuitka pyqt6 twitchio
   ```

3. **Configure credentials:**
   - Edit `secure.env` with your Twitch credentials
   - Or use first-run setup dialog

4. **Run from source:**
   ```bash
   python Main.py
   ```

5. **Build executable:**
   ```powershell
   .\build_nuitka.ps1
   ```

6. **Build installer:**
   ```powershell
   .\build_professional_installer.ps1
   ```

## 🔧 Configuration

Create a `.env` file with your Twitch credentials:

```env
TWITCH_TOKEN=your_oauth_token
TWITCH_NICK=your_bot_username
TWITCH_CHANNEL=your_channel_name
```

## 🏗️ Building from Source

### Build Application

```powershell
# Build the main executable
.\build_nuitka.ps1

# Output: dist\Main.dist\Main.exe
```

### Build Professional Installer

```powershell
# Build the Windows installer (requires Inno Setup)
.\build_professional_installer.ps1

# Output: installer_output\RustyBot_Setup_v1.4.1.exe
```

**Requirements:**
- Nuitka compiler
- [Inno Setup 6](https://jrsoftware.org/isdl.php) (for installer)
- PyQt6, TwitchIO

## 📖 Documentation

- [Secure Credentials Setup](SECURE_CREDENTIALS_SETUP.md) - How to configure Twitch credentials
- [Asset Migration](docs/MIGRATION_ASSETS_v1.38.md) - Asset structure information
- [Dependencies](docs/DEPENDENCIES.md) - Dependency information

## 🚀 Quick Start Guide

1. **Launch RustyBot**
2. **Set your prize** in the Prize field
3. **Click "Start"** to begin monitoring chat
4. **Users type your keyword** (e.g., `!giveaway`) to enter
5. **Click "Draw Winner"** when ready
6. **Winner confirmation** via chat or manual selection

## 🔄 Updates

**Automatic updates coming in future version!**

For now, to update:
1. Download the latest installer from [Releases](https://github.com/nexis84/Rusty-Client/releases/latest)
2. Run the installer (it will update your existing installation)
3. Your settings and credentials are preserved

## 🎮 EVE2Twitch Integration

RustyBot can verify EVE Online character names through EVE2Twitch:

1. Winner enters their IGN (In-Game Name) in chat
2. RustyBot automatically looks up their EVE2Twitch registration
3. Verification happens in the background
4. Clear status updates in the UI

## 📦 Project Structure

```
RustyBot/
├── Main.py                           # Main application
├── animation_manager.py              # Animation system
├── sound_manager.py                  # Sound effects
├── ui_manager.py                     # User interface
├── config_manager.py                 # Configuration
├── secure_env_loader.py              # Secure credentials
├── first_run_setup.py                # First-run dialog
├── build_nuitka.ps1                  # Build application
├── build_professional_installer.ps1  # Build installer
├── installer_improved.iss            # Inno Setup script
├── assets/                           # Web animations
├── sounds/                           # Sound effects
├── Fonts/                            # Custom fonts
└── dist/                             # Build output

```

## �️ Requirements

- **Python 3.10+**
- **PyQt6 6.9.1+**
- **TwitchIO 3.1.0+**
- **See [requirements.txt](requirements.txt) for complete list**

## 🐛 Troubleshooting

### Installation Issues
- **Windows Defender warning**: The Inno Setup installer is trusted and safe. Click "More info" → "Run anyway" if prompted
- **Installation fails**: Run installer as Administrator
- **Can't find installed app**: Check Start Menu or installation folder

### Runtime Issues
- **First run**: You'll be prompted to enter your Twitch channel name
- **Connection issues**: Verify your internet connection
- **Missing features**: Make sure you're running the latest version from [Releases](https://github.com/nexis84/Rusty-Client/releases/latest)

### For Developers
- Ensure Nuitka is installed: `pip install nuitka`
- Verify all folders exist: `assets/`, `sounds/`, `Fonts/`
- Check Python version: 3.10+ required

## 📝 Version History

### v1.4.1 (Current)
- Test auto-update functionality
- Minor improvements

### v1.4.0
- ✅ **NEW: Professional Windows installer** using Inno Setup
- ✅ **No more Windows Defender issues**
- ✅ One-click installation with automatic configuration
- ✅ Proper uninstaller included
- ✅ Built with Nuitka for better performance
- ✅ Improved security with automatic exclusions

See [Releases](https://github.com/nexis84/Rusty-Client/releases) for full changelog.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/nexis84/Rusty-Client/issues)
- **Discussions:** [GitHub Discussions](https://github.com/nexis84/Rusty-Client/discussions)

## � Acknowledgments

- Built with PyQt6
- Powered by TwitchIO
- EVE Online integration via EVE2Twitch

---

**Made with ❤️ for the EVE Online community**
