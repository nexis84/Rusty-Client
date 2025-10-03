# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller .spec file for building the RustyBotGiveaway executable.
FINAL VERSION: This version uses a fully manual data collection method
to bypass the stubborn 'ValueError: too many values to unpack'.
"""

import sys
import os
from pathlib import Path

# --- Define the application's main script and version ---
MAIN_SCRIPT = 'Main.py'
APP_NAME = "RustyBotGiveaway"
APP_VERSION = "1.2.5"  # Ensure this matches the version in Main.py

# --- Get the directory containing this .spec file ---
# This is the correct and robust way to find assets relative to the spec file.
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# --- Application Icon Path ---
ICON_PATH = os.path.join(spec_dir, 'icon.ico')
if not os.path.exists(ICON_PATH):
    raise FileNotFoundError(f"Application icon not found at: {ICON_PATH}")

# --- FULLY MANUAL DATA COLLECTION ---

# This helper function will walk a directory and create the list of
# (source_path, destination_folder) tuples that PyInstaller needs.
def collect_data_files(source_folder_name, destination_folder_name):
    """
    Walks a source folder and collects all files, creating tuples for PyInstaller's
    'datas' list. This preserves the subdirectory structure.
    """
    source_path = os.path.join(spec_dir, source_folder_name)
    if not os.path.isdir(source_path):
        print(f"WARNING: Data directory '{source_folder_name}' not found. Skipping.")
        return []

    data_tuples = []
    for root, dirs, files in os.walk(source_path):
        for filename in files:
            # Full path to the source file
            source_file_path = os.path.join(root, filename)
            # Path of the directory relative to the initial source folder
            relative_dir = os.path.relpath(root, source_path)
            # Destination directory inside the bundle
            if relative_dir == '.':
                # Files in the root of the source folder
                destination_dir = destination_folder_name
            else:
                # Files in subdirectories
                destination_dir = os.path.join(destination_folder_name, relative_dir)
            
            data_tuples.append((source_file_path, destination_dir))
            
    return data_tuples

# --- Start building the master 'datas' list ---
datas_list = []

# 1. Collect all files from the 'sounds' directory recursively.
# This will place them in a 'sounds' folder in the final bundle.
datas_list.extend(collect_data_files('sounds', 'sounds'))

# 2. Add individual files that go in the root of the bundle.
files_to_include = [
    'qwebchannel.js',
    'style.css',
    'network_animation.js',
    'background_lists.js',
    'animation.html',
    'mini_test.html',
    'loading_init.png',
]

for file_name in files_to_include:
    file_path = os.path.join(spec_dir, file_name)
    if os.path.exists(file_path):
        # The destination '.' means the root folder of the bundle.
        datas_list.append((file_path, '.'))
    else:
        print(f"WARNING: Data file not found: {file_path}. It will not be bundled.")

# --- The main Analysis object ---
a = Analysis(
    [MAIN_SCRIPT],
    pathex=[spec_dir],
    binaries=[],
    datas=datas_list,  # Use our manually constructed list
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=f'{APP_NAME}-{APP_VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=f'{APP_NAME}-{APP_VERSION}',
)