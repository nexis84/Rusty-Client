# RustyBot V1.38 - Project Structure

A Twitch giveaway bot for EVE Online with advanced animation features.

## 📁 Project Structure

```
RustyBot/
├── Main.py                    # Main application entry point
├── config.json                # Configuration file
├── requirements.txt           # Python dependencies
│
├── Core Modules/
│   ├── animation_manager.py   # Animation system
│   ├── config_manager.py      # Configuration management
│   ├── irc_fallback.py        # IRC connection fallback
│   ├── logging_utils.py       # Logging utilities
│   ├── options_dialog.py      # Options UI dialog
│   ├── sound_manager.py       # Sound effects manager
│   ├── ui_manager.py          # UI management
│   └── widget_handler.py      # Widget handling
│
├── assets/                    # Web assets (HTML/JS/CSS)
│   ├── animation.html         # Winner animation page
│   ├── mini_test.html         # Mini test page
│   ├── portrait_test.html     # Portrait test page
│   ├── background_lists.js    # Background configurations
│   ├── network_animation.js   # Network animation effects
│   ├── qwebchannel.js        # Qt WebChannel bridge
│   ├── script.js             # Main JavaScript
│   └── style.css             # Stylesheets
│
├── tests/                     # Test files
│   ├── debug_test.py
│   ├── direct_test.py
│   ├── test.py
│   ├── test_debug_filter.py
│   ├── test_prize_removal.py
│   ├── Maintest.py
│   ├── newtest.py
│   └── mini.py
│
├── specs/                     # PyInstaller spec files
│   ├── main.spec
│   ├── RustyBot_Main.spec
│   ├── RustyBotGiveaway_Main2.spec
│   ├── RustyBotGiveaway.spec
│   └── giveaway_app.spec.bk
│
├── docs/                      # Documentation
│   ├── UPDATE_1.2.6.md
│   ├── UPDATE_1.2.6.txt
│   └── output_entry_method.txt
│
├── backup/                    # Backup files
│   ├── config.json.bk
│   ├── run_main_dev_e2t_404.err
│   ├── run_main_dev_e2t_404.log
│   ├── Hacking Successful.wav.bk
│   ├── stop R1.wav.bk
│   ├── stop R2.wav.bk
│   ├── Stop R3.wav.bk
│   └── wheel_tick.wav.bk
│
├── Fonts/                     # Font files
├── sounds/                    # Sound effects
├── build/                     # Build artifacts
├── dist/                      # Distribution files
├── .venv/                     # Virtual environment
└── __pycache__/               # Python cache

```

## 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your `.env` file with Twitch credentials

3. Run the application:
   ```bash
   python Main.py
   ```

## 📝 Notes

- All test files have been moved to `tests/`
- Web assets (HTML/JS/CSS) are now in `assets/`
- PyInstaller spec files are in `specs/`
- Documentation is in `docs/`
- Backup files (.bk, logs, errors) are in `backup/`

## 🔧 Building

To build an executable, use the spec files in the `specs/` folder:
```bash
pyinstaller specs/RustyBot_Main.spec
```

## 📖 Version

Current version: 1.38 (Update 1.2.6)
