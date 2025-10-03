"""
Update Dialog for RustyBot
Displays update information and handles download/installation
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import sys


class UpdateDownloadThread(QThread):
    """Background thread for downloading updates"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, updater):
        super().__init__()
        self.updater = updater
    
    def run(self):
        success, result = self.updater.download_update(
            progress_callback=lambda p: self.progress.emit(p)
        )
        self.finished.emit(success, result)


class UpdateDialog(QDialog):
    """Dialog to display update information and download updates"""
    
    def __init__(self, current_version, latest_version, release_notes, updater, parent=None):
        super().__init__(parent)
        self.updater = updater
        self.download_thread = None
        self.downloaded_file_path = None
        
        self.setWindowTitle("Update Available")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"🎉 New Version Available!")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        version_info = QLabel(
            f"Current Version: <b>v{current_version}</b><br>"
            f"Latest Version: <b style='color: #4CAF50;'>v{latest_version}</b>"
        )
        version_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_info)
        
        # Release notes
        notes_label = QLabel("Release Notes:")
        notes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(notes_label)
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlainText(release_notes)
        self.notes_text.setReadOnly(True)
        self.notes_text.setMaximumHeight(200)
        layout.addWidget(self.notes_text)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.update_button = QPushButton("Download && Install Update")
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.update_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.update_button)
        
        self.skip_button = QPushButton("Skip This Version")
        self.skip_button.clicked.connect(self.reject)
        button_layout.addWidget(self.skip_button)
        
        layout.addLayout(button_layout)
        
        # Info text
        info_text = QLabel(
            "<i>The application will restart automatically after the update is installed.</i>"
        )
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setStyleSheet("color: #666; margin-top: 10px;")
        layout.addWidget(info_text)
        
        self.setLayout(layout)
    
    def start_download(self):
        """Start downloading the update"""
        self.update_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloading update...")
        
        # Start download in background thread
        self.download_thread = UpdateDownloadThread(self.updater)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def on_download_progress(self, progress):
        """Update progress bar"""
        self.progress_bar.setValue(progress)
    
    def on_download_finished(self, success, result):
        """Handle download completion"""
        if success:
            self.downloaded_file_path = result
            self.status_label.setText("Download complete! Installing...")
            self.progress_bar.setVisible(False)
            
            # Apply the update
            success, message = self.updater.apply_update(self.downloaded_file_path)
            
            if success:
                self.status_label.setText("Update installed! Restarting...")
                # The app will close and restart automatically
                QMessageBox.information(
                    self,
                    "Update Complete",
                    "The update has been installed. The application will now restart."
                )
                # Close the entire application (it will restart via the update script)
                sys.exit(0)
            else:
                self.status_label.setText(f"Update failed: {message}")
                self.update_button.setEnabled(True)
                self.skip_button.setEnabled(True)
                QMessageBox.critical(self, "Update Failed", message)
        else:
            self.status_label.setText(f"Download failed: {result}")
            self.progress_bar.setVisible(False)
            self.update_button.setEnabled(True)
            self.skip_button.setEnabled(True)
            QMessageBox.critical(self, "Download Failed", result)


def check_for_updates_with_dialog(parent=None):
    """
    Check for updates and show dialog if update is available.
    Returns True if update check was performed, False otherwise.
    """
    try:
        from auto_updater import AutoUpdater
        
        updater = AutoUpdater()
        has_update, latest_version, notes = updater.check_for_updates()
        
        if has_update is None:
            # Failed to check for updates
            print(f"Update check failed: {notes}")
            return False
        elif has_update:
            # Show update dialog
            dialog = UpdateDialog(
                updater.current_version,
                latest_version,
                notes,
                updater,
                parent
            )
            dialog.exec()
            return True
        else:
            # No update available
            print(f"Running latest version: v{updater.current_version}")
            return False
            
    except Exception as e:
        print(f"Update check error: {e}")
        return False
