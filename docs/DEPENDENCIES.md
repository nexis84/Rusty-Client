# Dependency Management for RustyBot

## 📦 Requirements Files

We provide multiple requirements files for different use cases:

### **requirements.txt** (Main)
The standard requirements file with all production dependencies pinned to tested versions.

```bash
pip install -r requirements.txt
```

**Includes:**
- PyQt6 (GUI framework)
- PyQt6-WebEngine (Animation display)
- pygame (Sound effects)
- twitchio (Twitch bot)
- python-twitch-irc (IRC fallback)
- python-dotenv (Environment variables)
- requests (HTTP/API calls)

### **requirements-dev.txt** (Development)
Additional tools for development, testing, and building.

```bash
pip install -r requirements-dev.txt
```

**Includes:**
- Code quality tools (pylint, black, flake8, mypy)
- Testing frameworks (pytest, pytest-qt)
- Build tools (pyinstaller)
- Documentation (sphinx)

### **requirements-min.txt** (Minimal)
Bare minimum dependencies for production/deployment.

```bash
pip install -r requirements-min.txt
```

**Includes:**
- Only essential packages (PyQt6, twitchio, requests, python-dotenv)
- Excludes optional packages like pygame and python-twitch-irc

## 🔄 Version Pinning Strategy

We use **exact version pinning** (`==`) instead of minimum versions (`>=`) because:

✅ **Reproducible builds** - Same versions every time  
✅ **Avoid breaking changes** - New releases won't break your app  
✅ **Consistent behavior** - Same experience across machines  
✅ **Easier debugging** - Everyone tests with same versions  

## 📊 Updating Dependencies

### Check for outdated packages:
```bash
pip list --outdated
```

### Update a specific package:
```bash
pip install --upgrade package-name
```

### Update all packages:
```bash
pip install -r requirements.txt --upgrade
```

**Then regenerate the requirements file:**
```bash
pip freeze > requirements-updated.txt
```

## 🐍 Python Version

**Required:** Python 3.10 or higher

Check your version:
```bash
python --version
```

## 🔧 Virtual Environment Setup

**Recommended:** Always use a virtual environment

### Create virtual environment:
```bash
python -m venv .venv
```

### Activate virtual environment:

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Deactivate when done:
```bash
deactivate
```

## 📝 Key Dependencies Explained

| Package | Purpose | Required? |
|---------|---------|-----------|
| **PyQt6** | Main GUI framework | ✅ Yes |
| **PyQt6-WebEngine** | Winner animations (WebView) | ✅ Yes |
| **pygame** | Sound effects playback | ⚠️ Optional |
| **twitchio** | Twitch bot & chat | ✅ Yes |
| **python-twitch-irc** | IRC fallback connection | ⚠️ Optional |
| **python-dotenv** | Load .env config | ✅ Yes |
| **requests** | ESI & EVE2Twitch APIs | ✅ Yes |

## 🚨 Common Issues

### **Issue:** PyQt6-WebEngine won't install
**Solution:** Make sure you have Python 3.10+ and pip is updated:
```bash
python -m pip install --upgrade pip
pip install PyQt6-WebEngine
```

### **Issue:** pygame audio issues on Windows
**Solution:** Install correct pygame wheel for your Python version

### **Issue:** twitchio version conflicts
**Solution:** We pin to v3.1.0 which is tested and stable

## 🔐 Security Notes

- Never commit your `.env` file (contains API tokens)
- Keep dependencies updated for security patches
- Use virtual environments to isolate dependencies

## 📅 Last Updated

**Date:** October 1, 2025  
**RustyBot Version:** 1.38  
**Python Version:** 3.10+

---

For more information, see the main [README.md](../README.md)
