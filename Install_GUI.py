"""
RustyBot GUI Installer
Beautiful PyQt6 installer with RustyBot styling
"""

import sys
import os
import json
import shutil
import zipfile
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QProgressBar,
                             QLineEdit, QFileDialog, QTextEdit, QRadioButton,
                             QButtonGroup, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap

class InstallWorker(QThread):
    """Background thread for installation"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, install_path, source_path, create_shortcut):
        super().__init__()
        self.install_path = install_path
        self.source_path = source_path
        self.create_shortcut = create_shortcut
        
    def run(self):
        try:
            # Step 1: Create directory
            self.progress.emit(10, "Creating installation directory...")
            os.makedirs(self.install_path, exist_ok=True)
            
            # Step 2: Add Windows Defender exclusion
            self.progress.emit(20, "Adding Windows Defender exclusion...")
            try:
                import subprocess
                subprocess.run(
                    ['powershell', '-Command', f'Add-MpPreference -ExclusionPath "{self.install_path}"'],
                    check=True,
                    capture_output=True
                )
            except Exception as e:
                self.progress.emit(25, f"Warning: Could not add exclusion: {e}")
            
            # Step 3: Copy files
            self.progress.emit(30, "Copying application files...")
            total_files = sum(1 for _ in Path(self.source_path).rglob('*') if _.is_file())
            copied = 0
            
            for item in Path(self.source_path).iterdir():
                if item.name in ['Install.ps1', 'Install.bat', 'Install.exe']:
                    continue
                    
                dest = Path(self.install_path) / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                    copied += 1
                elif item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                    copied += len(list(item.rglob('*')))
                
                progress_val = 30 + int((copied / total_files) * 50)
                self.progress.emit(progress_val, f"Copying files... {copied}/{total_files}")
            
            # Step 4: Create desktop shortcut
            if self.create_shortcut:
                self.progress.emit(85, "Creating desktop shortcut...")
                try:
                    from win32com.client import Dispatch
                    desktop = Path.home() / "Desktop"
                    shortcut_path = desktop / "RustyBot.lnk"
                    
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(str(shortcut_path))
                    shortcut.Targetpath = str(Path(self.install_path) / "RustyBot.vbs")
                    shortcut.WorkingDirectory = str(self.install_path)
                    shortcut.Description = "RustyBot - Twitch Giveaway Bot"
                    shortcut.save()
                except Exception as e:
                    self.progress.emit(90, f"Note: Could not create shortcut: {e}")
            
            # Step 5: Complete
            self.progress.emit(100, "Installation complete!")
            self.finished.emit(True, f"RustyBot installed successfully to:\n{self.install_path}")
            
        except Exception as e:
            self.finished.emit(False, f"Installation failed:\n{str(e)}")


class RustyBotInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.install_path = "C:\\RustyBot"
        self.source_path = Path(__file__).parent
        self.create_shortcut = True
        self.current_page = 0
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("RustyBot Installer")
        self.setFixedSize(600, 500)
        
        # Set RustyBot color scheme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
            QLabel {
                color: #eee;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e94560, stop:1 #c41e3a);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff5577, stop:1 #e94560);
            }
            QPushButton:pressed {
                background: #c41e3a;
            }
            QPushButton:disabled {
                background: #555;
                color: #888;
            }
            QLineEdit {
                background: #2a2a3e;
                color: #eee;
                border: 2px solid #e94560;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #ff5577;
            }
            QProgressBar {
                background: #2a2a3e;
                border: 2px solid #e94560;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e94560, stop:1 #ff5577);
                border-radius: 3px;
            }
            QTextEdit {
                background: #2a2a3e;
                color: #eee;
                border: 2px solid #e94560;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
            QRadioButton {
                color: #eee;
                font-size: 13px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #e94560;
                background: #2a2a3e;
            }
            QRadioButton::indicator:checked {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5, stop:0 #ff5577, stop:1 #e94560);
            }
            QCheckBox {
                color: #eee;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #e94560;
                background: #2a2a3e;
            }
            QCheckBox::indicator:checked {
                background: #e94560;
                image: url(checkmark.png);
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🤖 RustyBot Installer")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ff5577;")
        layout.addWidget(title)
        
        # Subtitle
        self.subtitle = QLabel("Welcome! Let's get RustyBot installed.")
        self.subtitle.setFont(QFont("Arial", 12))
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)
        
        # Content area (stacked pages)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        layout.addWidget(self.content_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setVisible(False)
        button_layout.addWidget(self.back_btn)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.go_next)
        button_layout.addWidget(self.next_btn)
        
        self.install_btn = QPushButton("🚀 Install")
        self.install_btn.clicked.connect(self.start_installation)
        self.install_btn.setVisible(False)
        button_layout.addWidget(self.install_btn)
        
        self.finish_btn = QPushButton("✨ Finish")
        self.finish_btn.clicked.connect(self.finish_installation)
        self.finish_btn.setVisible(False)
        button_layout.addWidget(self.finish_btn)
        
        layout.addLayout(button_layout)
        
        # Show first page
        self.show_welcome_page()
        
    def clear_content(self):
        """Clear current content"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def show_welcome_page(self):
        """Page 0: Welcome"""
        self.clear_content()
        self.current_page = 0
        self.subtitle.setText("Welcome! Let's get RustyBot installed.")
        
        # Welcome text
        welcome = QLabel("""
        <div style='text-align: center; line-height: 1.6;'>
        <p style='font-size: 14px;'>
        RustyBot is a powerful Twitch giveaway bot with:
        </p>
        <ul style='text-align: left; margin-left: 100px; font-size: 13px;'>
        <li>🎨 Beautiful animated interface</li>
        <li>🔒 Encrypted credentials for security</li>
        <li>⚡ Fast and reliable giveaway system</li>
        <li>🎵 Sound effects and notifications</li>
        <li>🔄 Automatic updates</li>
        </ul>
        <p style='font-size: 13px; margin-top: 20px;'>
        This installer will:
        </p>
        <ul style='text-align: left; margin-left: 100px; font-size: 13px;'>
        <li>✓ Add Windows Defender exclusion</li>
        <li>✓ Copy all necessary files</li>
        <li>✓ Create a desktop shortcut</li>
        <li>✓ Set up everything for you</li>
        </ul>
        </div>
        """)
        welcome.setWordWrap(True)
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(welcome)
        
        self.content_layout.addStretch()
        
        # Button states
        self.back_btn.setVisible(False)
        self.next_btn.setVisible(True)
        self.install_btn.setVisible(False)
        self.finish_btn.setVisible(False)
    
    def show_location_page(self):
        """Page 1: Installation location"""
        self.clear_content()
        self.current_page = 1
        self.subtitle.setText("Choose where to install RustyBot")
        
        # Installation location
        loc_label = QLabel("Installation Folder:")
        loc_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.content_layout.addWidget(loc_label)
        
        loc_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.install_path)
        self.path_input.setPlaceholderText("Select installation folder...")
        loc_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setMaximumWidth(120)
        browse_btn.clicked.connect(self.browse_folder)
        loc_layout.addWidget(browse_btn)
        
        self.content_layout.addLayout(loc_layout)
        
        # Presets
        preset_label = QLabel("\nQuick Select:")
        preset_label.setFont(QFont("Arial", 10))
        self.content_layout.addWidget(preset_label)
        
        self.preset_group = QButtonGroup()
        
        preset1 = QRadioButton(f"📂 C:\\RustyBot (Recommended)")
        preset1.setChecked(True)
        preset1.toggled.connect(lambda: self.path_input.setText("C:\\RustyBot"))
        self.preset_group.addButton(preset1)
        self.content_layout.addWidget(preset1)
        
        preset2 = QRadioButton(f"📂 C:\\Program Files\\RustyBot")
        preset2.toggled.connect(lambda: self.path_input.setText("C:\\Program Files\\RustyBot"))
        self.preset_group.addButton(preset2)
        self.content_layout.addWidget(preset2)
        
        preset3 = QRadioButton(f"📂 {Path.home()}\\RustyBot")
        preset3.toggled.connect(lambda: self.path_input.setText(str(Path.home() / "RustyBot")))
        self.preset_group.addButton(preset3)
        self.content_layout.addWidget(preset3)
        
        # Options
        options_label = QLabel("\nOptions:")
        options_label.setFont(QFont("Arial", 10))
        self.content_layout.addWidget(options_label)
        
        self.shortcut_check = QCheckBox("Create desktop shortcut")
        self.shortcut_check.setChecked(True)
        self.content_layout.addWidget(self.shortcut_check)
        
        # Info
        info = QLabel("\n⚠️ Note: Installation requires Administrator rights to add Windows Defender exclusion.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #ffaa00; font-size: 11px;")
        self.content_layout.addWidget(info)
        
        self.content_layout.addStretch()
        
        # Button states
        self.back_btn.setVisible(True)
        self.next_btn.setVisible(True)
        self.install_btn.setVisible(False)
        self.finish_btn.setVisible(False)
    
    def show_ready_page(self):
        """Page 2: Ready to install"""
        self.clear_content()
        self.current_page = 2
        self.subtitle.setText("Ready to install RustyBot!")
        
        # Get values
        self.install_path = self.path_input.text()
        self.create_shortcut = self.shortcut_check.isChecked()
        
        # Summary
        summary = QLabel(f"""
        <div style='font-size: 13px; line-height: 1.8;'>
        <p><b>Installation Summary:</b></p>
        <p>📁 <b>Location:</b><br>{self.install_path}</p>
        <p>🔒 <b>Windows Defender:</b><br>Exclusion will be added automatically</p>
        <p>🔗 <b>Desktop Shortcut:</b><br>{'Yes' if self.create_shortcut else 'No'}</p>
        <p>📦 <b>Size:</b><br>~413 MB (extracted)</p>
        <p style='margin-top: 20px; color: #77ff77;'>
        ✨ Click "Install" to begin!
        </p>
        </div>
        """)
        summary.setWordWrap(True)
        self.content_layout.addWidget(summary)
        
        self.content_layout.addStretch()
        
        # Button states
        self.back_btn.setVisible(True)
        self.next_btn.setVisible(False)
        self.install_btn.setVisible(True)
        self.finish_btn.setVisible(False)
    
    def show_installing_page(self):
        """Page 3: Installing"""
        self.clear_content()
        self.current_page = 3
        self.subtitle.setText("Installing RustyBot... Please wait.")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(30)
        self.content_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Preparing installation...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: #aaa;")
        self.content_layout.addWidget(self.status_label)
        
        # Log
        log_label = QLabel("\nInstallation Log:")
        log_label.setFont(QFont("Arial", 10))
        self.content_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.content_layout.addWidget(self.log_text)
        
        self.content_layout.addStretch()
        
        # Button states
        self.back_btn.setVisible(False)
        self.next_btn.setVisible(False)
        self.install_btn.setVisible(False)
        self.finish_btn.setVisible(False)
    
    def show_complete_page(self, success, message):
        """Page 4: Installation complete"""
        self.clear_content()
        self.current_page = 4
        
        if success:
            self.subtitle.setText("🎉 Installation Complete!")
            
            complete = QLabel(f"""
            <div style='text-align: center; font-size: 14px; line-height: 1.8;'>
            <p style='color: #77ff77; font-size: 16px;'>
            <b>✨ RustyBot is ready to use!</b>
            </p>
            <p style='margin-top: 20px;'>
            {message.replace(chr(10), '<br>')}
            </p>
            <p style='margin-top: 30px; font-size: 13px;'>
            <b>First Run:</b><br>
            When you launch RustyBot, you'll be asked to enter your Twitch channel name.<br>
            Just type it in and click Continue - that's it!
            </p>
            <p style='margin-top: 20px; font-size: 13px;'>
            <b>Launch RustyBot:</b><br>
            {'• Double-click the desktop shortcut<br>' if self.create_shortcut else ''}
            • Or run: {self.install_path}\\RustyBot.vbs
            </p>
            </div>
            """)
        else:
            self.subtitle.setText("❌ Installation Failed")
            complete = QLabel(f"""
            <div style='text-align: center; font-size: 14px; line-height: 1.8;'>
            <p style='color: #ff7777; font-size: 16px;'>
            <b>Installation encountered an error</b>
            </p>
            <p style='margin-top: 20px;'>
            {message.replace(chr(10), '<br>')}
            </p>
            <p style='margin-top: 30px; font-size: 12px; color: #aaa;'>
            Please try running the installer as Administrator<br>
            or use the manual installation method from README.txt
            </p>
            </div>
            """)
        
        complete.setWordWrap(True)
        self.content_layout.addWidget(complete)
        
        self.content_layout.addStretch()
        
        # Button states
        self.back_btn.setVisible(False)
        self.next_btn.setVisible(False)
        self.install_btn.setVisible(False)
        self.finish_btn.setVisible(True)
    
    def browse_folder(self):
        """Browse for installation folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Installation Folder", self.install_path)
        if folder:
            self.path_input.setText(folder)
    
    def go_back(self):
        """Go to previous page"""
        if self.current_page == 1:
            self.show_welcome_page()
        elif self.current_page == 2:
            self.show_location_page()
    
    def go_next(self):
        """Go to next page"""
        if self.current_page == 0:
            self.show_location_page()
        elif self.current_page == 1:
            self.show_ready_page()
    
    def start_installation(self):
        """Start the installation process"""
        self.show_installing_page()
        
        # Start worker thread
        self.worker = InstallWorker(self.install_path, str(self.source_path), self.create_shortcut)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.installation_finished)
        self.worker.start()
    
    def update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.log_text.append(f"[{value}%] {message}")
    
    def installation_finished(self, success, message):
        """Installation completed"""
        self.show_complete_page(success, message)
    
    def finish_installation(self):
        """Close installer"""
        self.close()


def main():
    # Check if running as administrator
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    
    if not is_admin:
        # Relaunch as administrator
        import sys
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    
    installer = RustyBotInstaller()
    installer.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
