"""
RustyBot Launcher - Handles updates before starting main application
This small launcher manages the update process to avoid file locking issues
"""
import sys
import os
import time
import subprocess
import shutil
from pathlib import Path
import json

# Add PyQt6 imports for GUI
try:
    from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel, 
                                  QPushButton, QProgressBar, QMessageBox, QTextEdit)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Import the auto_updater module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auto_updater import AutoUpdater, CURRENT_VERSION


def find_main_executable():
    """Search for the main executable in a set of likely locations.
    Returns a Path to the executable or None if not found.
    """
    candidate_names = ["Main.exe", "RustyBot.exe"]
    tried = []

    search_dirs = []
    if getattr(sys, 'frozen', False):
        # Directory containing the running launcher
        exe_dir = Path(sys.executable).parent
        # Common layouts to check (app subfolder, root, current working dir)
        search_dirs.extend([
            exe_dir / 'dist',  # Check dist directory first
            exe_dir / 'app',
            exe_dir,
            Path.cwd(),
            exe_dir.parent,
        ])
        # If PyInstaller onefile, _MEIPASS may contain bundled files
        if hasattr(sys, '_MEIPASS'):
            search_dirs.insert(0, Path(sys._MEIPASS))
    else:
        script_dir = Path(__file__).parent
        search_dirs.extend([
            script_dir / 'dist',  # Check dist directory first
            script_dir / 'app',
            script_dir,
            script_dir.parent,
            Path.cwd(),
        ])

    # Deduplicate while preserving order
    seen = set()
    dedup_dirs = []
    for d in search_dirs:
        try:
            d = d.resolve()
        except Exception:
            pass
        if d not in seen:
            seen.add(d)
            dedup_dirs.append(d)

    for d in dedup_dirs:
        for name in candidate_names:
            candidate = d / name
            tried.append(str(candidate))
            if candidate.exists():
                return candidate

    return None


class UpdateWorker(QThread):
    """Background thread for update checks and downloads"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, updater):
        super().__init__()
        self.updater = updater
        self.action = None  # 'check' or 'download'
        
    def run(self):
        try:
            if self.action == 'check':
                self.status.emit("Checking for updates...")
                has_update, version, notes = self.updater.check_for_updates()
                
                if has_update is None:
                    self.finished.emit(False, "Failed to check for updates")
                elif has_update:
                    self.finished.emit(True, f"Update available: v{version}")
                else:
                    self.finished.emit(False, "No updates available")
                    
            elif self.action == 'download':
                self.status.emit("Downloading update...")
                success, result = self.updater.download_update(
                    progress_callback=lambda p: self.progress.emit(p)
                )
                
                if success:
                    self.finished.emit(True, result)  # result is file path
                else:
                    self.finished.emit(False, result)  # result is error message
                    
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class LauncherDialog(QDialog):
    """Simple launcher dialog with update capability"""
    
    def __init__(self):
        super().__init__()
        self.updater = AutoUpdater()
        self.downloaded_file = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f"RustyBot Launcher v{CURRENT_VERSION}")
        self.setMinimumSize(500, 400)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        # Apply RustyBot theme
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2a1a0a, stop:0.5 #3a2a1a, stop:1 #2f1f0f);
                color: #ffddaa;
            }
            QLabel {
                color: #ffddaa;
                background: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a3520, stop:1 #3a2510);
                color: #ffddaa;
                border: 2px solid #ff9500;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a4530, stop:1 #4a3520);
                border: 2px solid #ffaa00;
            }
            QPushButton:disabled {
                background: #2a2520;
                color: #7a7560;
                border: 2px solid #4a4540;
            }
            QProgressBar {
                border: 2px solid #ff9500;
                border-radius: 5px;
                text-align: center;
                background: #1a1510;
                color: #ffddaa;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff9500, stop:1 #ffaa00);
            }
            QTextEdit {
                background: #1a1510;
                color: #ffddaa;
                border: 2px solid #ff9500;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title with RustyBot theme
        title = QLabel("⚙️ RustyBot Launcher")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #ff9500;
            padding: 15px;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(255, 149, 0, 0.5);
        """)
        layout.addWidget(title)
        
        # Version info with theme
        self.version_label = QLabel(f"Current Version: v{CURRENT_VERSION}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet("""
            color: #e8d900;
            font-size: 11pt;
            padding: 5px;
        """)
        layout.addWidget(self.version_label)
        
        # Status label with theme
        self.status_label = QLabel("Ready to launch")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #ffddaa;
            font-size: 10pt;
            padding: 10px;
            background: rgba(255, 149, 0, 0.1);
            border: 1px solid #ff9500;
            border-radius: 5px;
        """)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Release notes
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setVisible(False)
        self.notes_text.setMaximumHeight(150)
        layout.addWidget(self.notes_text)
        
        # Buttons
        self.check_update_btn = QPushButton("Check for Updates")
        self.check_update_btn.clicked.connect(self.check_updates)
        layout.addWidget(self.check_update_btn)
        
        self.download_btn = QPushButton("Download Update")
        self.download_btn.clicked.connect(self.download_update)
        self.download_btn.setVisible(False)
        layout.addWidget(self.download_btn)
        
        self.install_btn = QPushButton("Install and Restart")
        self.install_btn.clicked.connect(self.install_update)
        self.install_btn.setVisible(False)
        layout.addWidget(self.install_btn)
        
        self.launch_btn = QPushButton("🚀 Launch RustyBot")
        self.launch_btn.clicked.connect(self.launch_rustybot)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9500, stop:1 #e68500);
                color: #1a1510;
                padding: 12px;
                font-size: 14pt;
                font-weight: bold;
                border: 3px solid #ffaa00;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffaa00, stop:1 #ff9500);
                border: 3px solid #ffbb00;
            }
        """)
        layout.addWidget(self.launch_btn)
        
        self.setLayout(layout)
        
        # Auto-check for updates on startup
        self.check_updates()
        
    def check_updates(self):
        """Check for available updates"""
        self.status_label.setText("Checking for updates...")
        self.check_update_btn.setEnabled(False)
        
        worker = UpdateWorker(self.updater)
        worker.action = 'check'
        worker.status.connect(self.status_label.setText)
        worker.finished.connect(self.on_check_finished)
        worker.start()
        
        # Keep reference to prevent garbage collection
        self.worker = worker
        
    def on_check_finished(self, success, message):
        """Handle update check completion"""
        self.check_update_btn.setEnabled(True)
        
        if success:
            # Update available
            self.status_label.setText(f"✅ {message}")
            self.version_label.setText(
                f"Current: v{CURRENT_VERSION} → Available: v{self.updater.latest_version}"
            )
            
            # Show release notes
            if self.updater.release_notes:
                self.notes_text.setVisible(True)
                self.notes_text.setPlainText(self.updater.release_notes)
            
            # Show download button
            self.download_btn.setVisible(True)
        else:
            self.status_label.setText(f"✓ {message}")
            self.notes_text.setVisible(False)
            self.download_btn.setVisible(False)
            
            # AUTO-LAUNCH: If no updates needed, automatically launch main app after brief delay
            from PyQt6.QtCore import QTimer
            self.status_label.setText("✓ No updates needed - Launching RustyBot...")
            QTimer.singleShot(1500, self.launch_rustybot)  # Launch after 1.5 seconds
            
    def download_update(self):
        """Download the update"""
        self.status_label.setText("Downloading update...")
        self.download_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        worker = UpdateWorker(self.updater)
        worker.action = 'download'
        worker.progress.connect(self.progress_bar.setValue)
        worker.status.connect(self.status_label.setText)
        worker.finished.connect(self.on_download_finished)
        worker.start()
        
        self.worker = worker
        
    def on_download_finished(self, success, result):
        """Handle download completion"""
        self.download_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.downloaded_file = result
            self.status_label.setText("✅ Download complete! Ready to install")
            self.install_btn.setVisible(True)
            self.launch_btn.setText("Launch WITHOUT Update")
        else:
            self.status_label.setText(f"❌ {result}")
            QMessageBox.warning(self, "Download Failed", result)
            
    def install_update(self):
        """Apply the downloaded update"""
        if not self.downloaded_file or not os.path.exists(self.downloaded_file):
            QMessageBox.warning(self, "Error", "No update file available")
            return
        
        reply = QMessageBox.question(
            self,
            "Install Update",
            f"This will close RustyBot (if running) and install v{self.updater.latest_version}.\n\n"
            "The application will restart automatically.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText("Installing update...")
            self.install_btn.setEnabled(False)
            self.launch_btn.setEnabled(False)
            
            # Apply update using the auto_updater
            success, message = self.updater.apply_update(self.downloaded_file)
            
            if success:
                QMessageBox.information(
                    self,
                    "Update Complete",
                    "Update installed successfully!\n\nRustyBot will now restart."
                )
                # The apply_update function will handle restart
            else:
                QMessageBox.critical(
                    self,
                    "Update Failed",
                    f"Failed to install update:\n\n{message}"
                )
                self.install_btn.setEnabled(True)
                self.launch_btn.setEnabled(True)
                
    def launch_rustybot(self):
        """Launch the main RustyBot application"""
        try:
            # Find Main.exe (or RustyBot.exe) in likely locations
            main_path = find_main_executable()

            if not main_path:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Main.exe not found in expected locations.\n\n"
                    "Please reinstall RustyBot or ensure the 'app' folder and Main.exe exist."
                )
                return

            # Launch the discovered executable
            subprocess.Popen([str(main_path)], cwd=str(main_path.parent))
            
            # Close launcher
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Failed",
                f"Failed to launch RustyBot:\n\n{str(e)}"
            )


def main():
    """Main launcher entry point"""
    if PYQT_AVAILABLE:
        # GUI mode
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        dialog = LauncherDialog()
        dialog.show()
        
        sys.exit(app.exec())
    else:
        # Console fallback
        print("="*60)
        print(" RustyBot Launcher")
        print("="*60)
        print(f"Current Version: v{CURRENT_VERSION}")
        print()
        
        updater = AutoUpdater()
        print("Checking for updates...")
        
        has_update, version, notes = updater.check_for_updates()
        
        if has_update:
            print(f"\n✅ Update available: v{version}")
            print(f"\nRelease Notes:\n{notes}\n")
            
            try:
                response = input("Download and install update? (y/n): ")
                if response.lower() == 'y':
                    print("Downloading...")
                    success, result = updater.download_update()
                    
                    if success:
                        print("Installing...")
                        success, message = updater.apply_update(result)
                        if not success:
                            print(f"Installation failed: {message}")
                    else:
                        print(f"Download failed: {result}")
            except (EOFError, OSError):
                # No stdin available (windowed mode) - auto-update
                print("Auto-updating (no console input available)...")
                success, result = updater.download_update()
                
                if success:
                    print("Installing...")
                    success, message = updater.apply_update(result)
                    if not success:
                        print(f"Installation failed: {message}")
                else:
                    print(f"Download failed: {result}")
        else:
            print("✓ You're running the latest version")
        
        # Launch Main.exe
        print("\nLaunching RustyBot...")
        
        # Find Main.exe (or RustyBot.exe) in likely locations
        main_path = find_main_executable()

        if main_path and main_path.exists():
            subprocess.Popen([str(main_path)], cwd=str(main_path.parent))
        else:
            print("ERROR: Main.exe not found in expected locations.")
            print("Searched common locations; ensure the 'app' folder and Main.exe exist.")
            try:
                input("Press Enter to exit...")
            except (EOFError, OSError):
                time.sleep(2)


if __name__ == "__main__":
    main()
