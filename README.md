# 🤖 RustyBot - EVE Online Twitch Giveaway Bot

[![Version](https://img.shields.io/badge/version-1.3.9-blue.svg)](https://github.com/nexis84/Rusty-Client/releases)
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

### For End Users (Recommended)

1. **Download the latest executable:**
   - Visit [Releases](https://github.com/nexis84/Rusty-Client/releases/latest)
   - Download `RustyBot.exe`
   
2. **Run the application:**
   - Create a folder (e.g., `C:\RustyBot\`)
   - Move `RustyBot.exe` to that folder
   - Double-click to run

3. **Updates:**
   - The app automatically checks for updates on startup
   - Click "Download & Install Update" when prompted
   - That's it! The app handles everything

### For Developers

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nexis84/Rusty-Client.git
   cd Rusty-Client
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Add your Twitch credentials

5. **Run the application:**
   ```bash
   python Main.py
   ```

## 🔧 Configuration

Create a `.env` file with your Twitch credentials:

```env
TWITCH_TOKEN=your_oauth_token
TWITCH_NICK=your_bot_username
TWITCH_CHANNEL=your_channel_name
```

## 🏗️ Building from Source

### Build Executable

1. **Install build dependencies:**
   ```bash
   pip install pyinstaller packaging
   ```

2. **Run the build script:**
   ```powershell
   .\build.ps1
   ```

3. **Find your executable:**
   ```
   dist\RustyBot\RustyBot.exe
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed build and release instructions.

## 📖 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Building and releasing
- [Requirements](REQUIREMENTS_IMPROVED.md) - Detailed requirements
- [Asset Migration](docs/MIGRATION_ASSETS_v1.38.md) - Asset structure
- [Dependencies](docs/DEPENDENCIES.md) - Dependency information

## 🚀 Quick Start Guide

1. **Launch RustyBot**
2. **Set your prize** in the Prize field
3. **Click "Start"** to begin monitoring chat
4. **Users type your keyword** (e.g., `!giveaway`) to enter
5. **Click "Draw Winner"** when ready
6. **Winner confirmation** via chat or manual selection

## 🔄 Auto-Update System

RustyBot includes an intelligent auto-update system:

- ✅ Checks GitHub for new releases on startup
- ✅ Shows release notes before updating
- ✅ Downloads and installs updates automatically
- ✅ Backs up current version before updating
- ✅ Restarts app with new version

**No technical knowledge required!** Just click update and go.

## 🎮 EVE2Twitch Integration

RustyBot can verify EVE Online character names through EVE2Twitch:

1. Winner enters their IGN (In-Game Name) in chat
2. RustyBot automatically looks up their EVE2Twitch registration
3. Verification happens in the background
4. Clear status updates in the UI

## 📦 Project Structure

```
RustyBot/
├── Main.py                    # Main application
├── auto_updater.py            # Auto-update system
├── update_dialog.py           # Update UI
├── animation_manager.py       # Animation system
├── sound_manager.py           # Sound effects
├── ui_manager.py              # User interface
├── config_manager.py          # Configuration
├── RustyBot.spec              # Build configuration
├── build.ps1                  # Build script
├── assets/                    # Web animations
├── sounds/                    # Sound effects
├── Fonts/                     # Custom fonts
└── tests/                     # Test utilities

```

## �️ Requirements

- **Python 3.10+**
- **PyQt6 6.9.1+**
- **TwitchIO 3.1.0+**
- **See [requirements.txt](requirements.txt) for complete list**

## 🐛 Troubleshooting

### Update Issues
- Ensure internet connection is active
- Check firewall isn't blocking GitHub access
- Try running as administrator (Windows)

### Build Issues
- Ensure all dependencies are installed
- Check that `icon.ico` exists
- Verify `assets/`, `sounds/`, `Fonts/` folders are present

### Runtime Issues
- Verify `.env` file has correct credentials
- Check Twitch OAuth token is valid
- Ensure Python 3.10+ is installed

## 📝 Version History

### v1.3.9 (Current)
- ✅ Auto-update functionality
- ✅ GitHub releases integration
- ✅ Build system improvements
- ✅ Better error handling

### v1.3.8
- Prize management improvements
- EVE2Twitch integration
- UI/UX enhancements

See [Releases](https://github.com/nexis84/Rusty-Client/releases) for full changelog.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

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
