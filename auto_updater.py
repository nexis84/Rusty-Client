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
CURRENT_VERSION = "1.8.3"

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
        """Download the latest version with optimized speed"""
        if not self.download_url:
            return False, "No download URL available"

        try:
            # Create temp directory
            temp_dir = tempfile.mkdtemp(prefix="rustybot_update_")
            download_name = self.asset_name or os.path.basename(self.download_url)
            temp_file_path = os.path.join(temp_dir, download_name)

            # Use a session for connection reuse and better performance
            with requests.Session() as session:
                # Configure session for better performance
                adapter = requests.adapters.HTTPAdapter(
                    pool_connections=10,
                    pool_maxsize=10,
                    max_retries=3,
                    pool_block=False
                )
                session.mount('http://', adapter)
                session.mount('https://', adapter)

                # Set headers for better performance
                headers = {
                    'Accept-Encoding': 'gzip, deflate, br',
                    'User-Agent': 'RustyBot-Updater/1.0',
                    'Accept': '*/*'
                }

                # Download with optimized settings
                response = session.get(
                    self.download_url,
                    stream=True,
                    timeout=60,  # Increased timeout for large files
                    headers=headers
                )
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                start_time = os.times()[4] if hasattr(os, 'times') else 0  # CPU time for speed calc

                # Use larger chunk size for better performance (128KB)
                chunk_size = 128 * 1024  # 128KB chunks

                with open(temp_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size > 0:
                                progress = int((downloaded / total_size) * 100)
                                progress_callback(progress)

                # Log download speed
                if start_time and total_size > 0:
                    end_time = os.times()[4] if hasattr(os, 'times') else 0
                    duration = max(end_time - start_time, 0.1)  # Avoid division by zero
                    speed_mbps = (downloaded / duration) / (1024 * 1024)
                    print(f"DOWNLOAD: Completed {downloaded} bytes in {duration:.1f}s ({speed_mbps:.2f} MB/s)")

            return True, temp_file_path

        except Exception as e:
            return False, f"Download failed: {str(e)}"
    
    def apply_update(self, downloaded_file):
        """Replace current executable/folder with new version and restart"""
        try:
            # Check if running as compiled executable
            # Nuitka sets __compiled__ attribute instead of sys.frozen
            # Also check if sys.executable ends with .exe and isn't python.exe
            is_frozen = getattr(sys, 'frozen', False) or hasattr(sys, '__compiled__')
            is_exe = sys.executable.lower().endswith('.exe') and 'python' not in os.path.basename(sys.executable).lower()
            
            # Check if RustyBot.exe exists in current directory or parent directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            main_exe_path = os.path.join(current_dir, 'RustyBot.exe')
            if not os.path.exists(main_exe_path):
                # Try parent directory
                main_exe_path = os.path.join(os.path.dirname(current_dir), 'RustyBot.exe')
            
            has_main_exe = os.path.exists(main_exe_path)
            
            print(f"DEBUG: sys.frozen = {getattr(sys, 'frozen', False)}")
            print(f"DEBUG: sys.__compiled__ = {hasattr(sys, '__compiled__')}")
            print(f"DEBUG: sys.executable = {sys.executable}")
            print(f"DEBUG: is_exe check = {is_exe}")
            print(f"DEBUG: RustyBot.exe found = {has_main_exe} at {main_exe_path if has_main_exe else 'N/A'}")
            
            # Consider it frozen if any check passes OR if RustyBot.exe exists nearby
            if is_frozen or is_exe or has_main_exe:
                # Use RustyBot.exe if found, otherwise use sys.executable
                current_exe = main_exe_path if has_main_exe else sys.executable
                current_dir = os.path.dirname(current_exe)
                
                print(f"DEBUG: Using exe path: {current_exe}")
                
                # Check if downloaded file is ZIP (folder distribution)
                if downloaded_file.endswith('.zip'):
                    return self._apply_zip_update(downloaded_file, current_dir, current_exe)
                elif 'Setup' in downloaded_file or 'setup' in downloaded_file or 'installer' in downloaded_file.lower():
                    # It's an installer - run it detached and exit
                    return self._apply_installer_update(downloaded_file)
                else:
                    # Single EXE update
                    return self._apply_exe_update(downloaded_file, current_exe)
            else:
                error_msg = f"Auto-update only works with compiled executable.\nDetected: frozen={getattr(sys, 'frozen', False)}, compiled={hasattr(sys, '__compiled__')}, exe={sys.executable}"
                print(f"ERROR: {error_msg}")
                return False, error_msg
                
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
                # Run update script in separate process
                subprocess.Popen(update_script, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0)
                
                # CRITICAL: Force immediate exit so update script can replace files
                import time
                time.sleep(0.5)  # Give script time to start
                
                # Quit Qt application first
                try:
                    from PyQt6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        app.quit()
                except:
                    pass
                
                # Force immediate process termination (no cleanup, just exit)
                os._exit(0)  # More forceful than sys.exit() - bypasses cleanup
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
    
    def _apply_installer_update(self, installer_path):
        """Apply update using an installer executable"""
        try:
            import subprocess
            import time
            
            print(f"DEBUG: Launching installer: {installer_path}")
            
            # Launch installer with CREATE_NO_WINDOW and DETACHED_PROCESS flags
            # This ensures the installer runs independently and won't close when parent dies
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            
            # Run installer completely detached from current process
            subprocess.Popen(
                [installer_path],
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True
            )
            
            print("DEBUG: Installer launched successfully, exiting RustyBot...")
            
            # Give installer time to start
            time.sleep(1)
            
            # Force immediate exit so installer can replace files
            try:
                from PyQt6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    app.quit()
            except:
                pass
            
            # Force exit
            import os
            os._exit(0)
            
        except Exception as e:
            return False, f"Failed to launch installer: {str(e)}"
    
    def _create_windows_update_script(self, new_exe, current_exe, backup_exe):
        """Create a Windows batch script to perform the update"""
        # Ensure we always restart RustyBot.exe
        current_dir = os.path.dirname(current_exe)
        rustybot_exe = os.path.join(current_dir, "RustyBot.exe")
        
        script = r"""
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
timeout /t 2 /nobreak >nul
cd /d "{current_dir}"
if exist "{rustybot_exe}" (
    start "" "{rustybot_exe}"
) else (
    start "" "{current_exe}"
)
del /F /Q "{backup_exe}" 2>nul
exit
""".format(current_exe=current_exe, new_exe=new_exe, backup_exe=backup_exe, current_dir=current_dir, rustybot_exe=rustybot_exe)
        script_path = os.path.join(tempfile.gettempdir(), "rustybot_update.bat")
        with open(script_path, 'w') as f:
            f.write(script)
        return script_path
    
    def _cleanup_old_files(self, install_dir):
        """Remove old/unused files from previous versions"""
        old_files = [
            'Launcher.exe',
            'simple_launcher.py',
            'launcher.py',
            'transition_launcher.py',
            'Main.exe',
            'RustyBot_Web_Updater.exe'
        ]
        
        removed_files = []
        for old_file in old_files:
            file_path = os.path.join(install_dir, old_file)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    removed_files.append(old_file)
                except Exception as e:
                    print(f"WARNING: Could not remove {old_file}: {e}")
        
        return removed_files
    
    def _create_windows_folder_update_script(self, new_app_dir, current_dir, current_exe):
        """Create a Windows batch script to update the entire folder"""
        backup_dir = current_dir + "_backup"
        log_file = os.path.join(current_dir, "update_log.txt")
        script = r"""
@echo off
set LOGFILE={log_file}
echo ======================================== > "%LOGFILE%"
echo   RustyBot Auto-Update v1.8.0 >> "%LOGFILE%"
echo   Started: %DATE% %TIME% >> "%LOGFILE%"
echo ======================================== >> "%LOGFILE%"

echo ========================================
echo   RustyBot Auto-Update v1.8.0
echo   Log: {log_file}
echo ========================================
echo.
echo Waiting for application to close...
echo [%TIME%] Waiting 5 seconds for app to close... >> "%LOGFILE%"
timeout /t 5 /nobreak >nul

REM Force kill any RustyBot.exe processes (repeat multiple times)
echo Terminating RustyBot...
echo [%TIME%] Killing RustyBot.exe and QtWebEngineProcess.exe... >> "%LOGFILE%"
taskkill /F /IM RustyBot.exe >nul 2>&1
echo [%TIME%] First kill attempt done >> "%LOGFILE%"
taskkill /F /IM QtWebEngineProcess.exe >nul 2>&1
timeout /t 1 /nobreak >nul
taskkill /F /IM RustyBot.exe >nul 2>&1
echo [%TIME%] Second kill attempt done >> "%LOGFILE%"
taskkill /F /IM QtWebEngineProcess.exe >nul 2>&1

REM Wait for Windows to release all file handles (extended)
echo Waiting for file handles to release...
echo [%TIME%] Waiting 5 seconds for file handles... >> "%LOGFILE%"
timeout /t 5 /nobreak >nul

REM Additional safety check - verify RustyBot.exe is not running
:CHECK_PROCESS
tasklist /FI "IMAGENAME eq RustyBot.exe" 2>NUL | find /I /N "RustyBot.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Still waiting for RustyBot.exe to close...
    echo [%TIME%] RustyBot.exe still running, killing again... >> "%LOGFILE%"
    taskkill /F /IM RustyBot.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    goto CHECK_PROCESS
)

echo All processes closed. Proceeding with update...
echo [%TIME%] All processes confirmed closed >> "%LOGFILE%"

echo Creating backup...
echo [%TIME%] Creating backup directory... >> "%LOGFILE%"
if exist "{backup_dir}" (
    rmdir /S /Q "{backup_dir}"
)
mkdir "{backup_dir}"

echo Backing up current installation...
echo [%TIME%] Backing up files... >> "%LOGFILE%"
xcopy /E /I /Y /Q "{current_dir}" "{backup_dir}" >nul

echo Applying update...
echo [%TIME%] Copying new files... >> "%LOGFILE%"
xcopy /E /I /Y /Q "{new_app_dir}\*" "{current_dir}" >nul

if errorlevel 1 (
    echo.
    echo Update failed! Restoring backup...
    echo [%TIME%] UPDATE FAILED! Restoring backup... >> "%LOGFILE%"
    xcopy /E /I /Y /Q "{backup_dir}\*" "{current_dir}" >nul
    echo [%TIME%] Backup restored >> "%LOGFILE%"
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo Removing old unused files...
echo [%TIME%] Cleaning up old files... >> "%LOGFILE%"
del /F /Q "{current_dir}\Launcher.exe" 2>nul
echo [%TIME%] Removed Launcher.exe (if existed) >> "%LOGFILE%"
del /F /Q "{current_dir}\Main.exe" 2>nul
echo [%TIME%] Removed Main.exe (if existed) >> "%LOGFILE%"
del /F /Q "{current_dir}\RustyBot_Web_Updater.exe" 2>nul
echo [%TIME%] Removed RustyBot_Web_Updater.exe (if existed) >> "%LOGFILE%"
del /F /Q "{current_dir}\simple_launcher.py" 2>nul
del /F /Q "{current_dir}\launcher.py" 2>nul
del /F /Q "{current_dir}\transition_launcher.py" 2>nul
echo [%TIME%] Old files cleanup complete >> "%LOGFILE%"

echo Cleaning up...
echo [%TIME%] Cleaning up backup and temp files... >> "%LOGFILE%"
rmdir /S /Q "{backup_dir}" 2>nul
rmdir /S /Q "{os.path.dirname(new_app_dir)}" 2>nul

echo.
echo ========================================
echo   Update Complete!
echo ========================================
echo.
echo Waiting for all file handles to release...
echo [%TIME%] Final wait before restart (10 seconds)... >> "%LOGFILE%"
timeout /t 10 /nobreak >nul

echo Restarting RustyBot...
echo [%TIME%] Restarting application... >> "%LOGFILE%"
cd /d "{current_dir}"
if exist "{current_dir}\RustyBot.exe" (
    echo [%TIME%] Starting RustyBot.exe... >> "%LOGFILE%"
    start "" "{current_dir}\RustyBot.exe"
) else (
    echo [%TIME%] WARNING: RustyBot.exe not found, trying fallback... >> "%LOGFILE%"
    start "" "{current_exe}"
)
echo [%TIME%] Update script finished successfully >> "%LOGFILE%"
timeout /t 2 /nobreak >nul
exit
""".format(log_file=log_file, backup_dir=backup_dir, current_dir=current_dir, new_app_dir=new_app_dir, current_exe=current_exe)
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
