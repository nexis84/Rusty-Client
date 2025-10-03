"""
Auto-Updater Module for RustyBot
Checks GitHub releases for updates and downloads new versions
"""
import os
import sys
import requests
import zipfile
import tempfile
import shutil
import subprocess
from pathlib import Path
from packaging import version
import json

# Current version - UPDATE THIS WITH EACH RELEASE
CURRENT_VERSION = "1.3.9"

# GitHub repository info
GITHUB_OWNER = "nexis84"
GITHUB_REPO = "Rusty-Client"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"


class AutoUpdater:
    def __init__(self, current_version=CURRENT_VERSION):
        self.current_version = current_version
        self.latest_version = None
        self.download_url = None
        self.asset_name = None
        self.release_notes = None
        
    def check_for_updates(self):
        """Check if a new version is available on GitHub"""
        try:
            response = requests.get(GITHUB_API_URL, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            self.latest_version = release_data['tag_name'].lstrip('v')
            self.release_notes = release_data.get('body', 'No release notes available')
            
            # Find the ZIP or EXE asset
            for asset in release_data.get('assets', []):
                if asset['name'].endswith('.zip') or asset['name'].endswith('.exe'):
                    self.download_url = asset['browser_download_url']
                    self.asset_name = asset['name']
                    break
            
            # Compare versions
            if version.parse(self.latest_version) > version.parse(self.current_version):
                return True, self.latest_version, self.release_notes
            
            return False, self.current_version, "You're running the latest version"
            
        except requests.exceptions.RequestException as e:
            print(f"Update check failed: {e}")
            return None, None, f"Failed to check for updates: {str(e)}"
        except Exception as e:
            print(f"Unexpected error checking updates: {e}")
            return None, None, f"Error: {str(e)}"
    
    def download_update(self, progress_callback=None):
        """Download the latest version"""
        if not self.download_url:
            return False, "No download URL available"
        
        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="rustybot_update_")
            download_name = self.asset_name or os.path.basename(self.download_url)
            temp_file_path = os.path.join(temp_dir, download_name)
            
            # Download with progress
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            progress_callback(progress)
            
            return True, temp_file_path
            
        except Exception as e:
            return False, f"Download failed: {str(e)}"
    
    def apply_update(self, downloaded_file):
        """Replace current executable/folder with new version and restart"""
        try:
            if getattr(sys, 'frozen', False):
                # Running as executable
                current_exe = sys.executable
                current_dir = os.path.dirname(current_exe)
                
                # Check if downloaded file is ZIP (folder distribution)
                if downloaded_file.endswith('.zip'):
                    return self._apply_zip_update(downloaded_file, current_dir, current_exe)
                else:
                    # Single EXE update
                    return self._apply_exe_update(downloaded_file, current_exe)
            else:
                return False, "Auto-update only works with compiled executable"
                
        except Exception as e:
            return False, f"Update failed: {str(e)}"
    
    def _apply_zip_update(self, zip_file, current_dir, current_exe):
        """Apply update from ZIP file (folder distribution)"""
        try:
            # Extract ZIP to temp location
            temp_extract_dir = tempfile.mkdtemp(prefix="rustybot_extract_")
            
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            
            # Find the extracted folder (usually named RustyBot_vX.X.X_Standalone)
            extracted_folders = [f for f in os.listdir(temp_extract_dir) 
                               if os.path.isdir(os.path.join(temp_extract_dir, f))]
            
            if not extracted_folders:
                return False, "Invalid update package: no folder found in ZIP"
            
            new_app_dir = os.path.join(temp_extract_dir, extracted_folders[0])
            
            # Create update script for Windows
            if sys.platform == 'win32':
                update_script = self._create_windows_folder_update_script(
                    new_app_dir, current_dir, current_exe
                )
                # Run update script and exit
                subprocess.Popen(update_script, shell=True)
                return True, "Update will complete after restart"
            else:
                return False, "Auto-update only supported on Windows"
                
        except Exception as e:
            return False, f"Failed to apply ZIP update: {str(e)}"
    
    def _apply_exe_update(self, new_exe_path, current_exe):
        """Apply single EXE update (legacy)"""
        try:
            backup_exe = current_exe + ".bak"
            
            # Create backup
            if os.path.exists(backup_exe):
                os.remove(backup_exe)
            shutil.copy2(current_exe, backup_exe)
            
            # Create update script
            if sys.platform == 'win32':
                update_script = self._create_windows_update_script(
                    new_exe_path, current_exe, backup_exe
                )
                # Run update script and exit
                subprocess.Popen(update_script, shell=True)
                return True, "Update will complete after restart"
            else:
                return False, "Auto-update only supported on Windows"
                
        except Exception as e:
            return False, f"Failed to apply EXE update: {str(e)}"
    
    def _create_windows_update_script(self, new_exe, current_exe, backup_exe):
        """Create a Windows batch script to perform the update"""
        script = f"""
@echo off
timeout /t 2 /nobreak >nul
echo Applying update...

:RETRY
del /F /Q "{current_exe}" 2>nul
if exist "{current_exe}" (
    timeout /t 1 /nobreak >nul
    goto RETRY
)

move /Y "{new_exe}" "{current_exe}"
if errorlevel 1 (
    echo Update failed! Restoring backup...
    move /Y "{backup_exe}" "{current_exe}"
    pause
    exit /b 1
)

echo Update complete! Restarting...
start "" "{current_exe}"
del /F /Q "{backup_exe}" 2>nul
exit
"""
        script_path = os.path.join(tempfile.gettempdir(), "rustybot_update.bat")
        with open(script_path, 'w') as f:
            f.write(script)
        return script_path
    
    def _create_windows_folder_update_script(self, new_app_dir, current_dir, current_exe):
        """Create a Windows batch script to update the entire folder"""
        backup_dir = current_dir + "_backup"
        script = f"""
@echo off
echo ========================================
echo   RustyBot Auto-Update
echo ========================================
echo.
echo Waiting for application to close...
timeout /t 3 /nobreak >nul

echo Creating backup...
if exist "{backup_dir}" (
    rmdir /S /Q "{backup_dir}"
)
mkdir "{backup_dir}"

echo Backing up current installation...
xcopy /E /I /Y /Q "{current_dir}" "{backup_dir}" >nul

echo Applying update...
xcopy /E /I /Y /Q "{new_app_dir}\*" "{current_dir}" >nul

if errorlevel 1 (
    echo.
    echo Update failed! Restoring backup...
    xcopy /E /I /Y /Q "{backup_dir}\*" "{current_dir}" >nul
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Cleaning up...
rmdir /S /Q "{backup_dir}" 2>nul
rmdir /S /Q "{os.path.dirname(new_app_dir)}" 2>nul

echo.
echo ========================================
echo   Update Complete!
echo ========================================
echo.
echo Restarting RustyBot...
timeout /t 2 /nobreak >nul
start "" "{current_exe}"
exit
"""
        script_path = os.path.join(tempfile.gettempdir(), "rustybot_folder_update.bat")
        with open(script_path, 'w') as f:
            f.write(script)
        return script_path


def check_for_updates_simple():
    """Simple function to check for updates - returns (has_update, version, notes)"""
    updater = AutoUpdater()
    return updater.check_for_updates()


if __name__ == "__main__":
    # Test the updater
    updater = AutoUpdater()
    has_update, latest_ver, notes = updater.check_for_updates()
    
    if has_update is None:
        print("Failed to check for updates")
        print(notes)
    elif has_update:
        print(f"Update available: v{latest_ver}")
        print(f"Current version: v{updater.current_version}")
        print(f"\nRelease notes:\n{notes}")
    else:
        print(f"You're running the latest version (v{updater.current_version})")
