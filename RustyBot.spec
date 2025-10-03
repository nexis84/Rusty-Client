# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for RustyBot
Builds a standalone executable with all dependencies included
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project directory
project_dir = Path(SPECPATH)

# Data files to include
datas = [
    ('assets', 'assets'),
    ('sounds', 'sounds'),
    ('Fonts', 'Fonts'),
    ('.env', '.'),
    ('config.json', '.'),
    ('icon.ico', '.'),
    ('Loading.png', '.'),
    ('loading_init.png', '.'),
    ('RUSTY BOT.png', '.'),
    ('*.ttf', '.'),
    ('*.otf', '.'),
]

# Binary dependencies (if needed)
binaries = []

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'twitchio',
    'twitchio.ext.commands',
    'pygame',
    'dotenv',
    'requests',
    'packaging',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements',
]

a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'scipy',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RustyBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disabled to reduce antivirus false positives
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Your application icon
    version_file=None,
)
