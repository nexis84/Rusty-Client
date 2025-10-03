"""
First Run Setup Dialog for RustyBot
Prompts user for their channel name on first launch
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import json
from pathlib import Path


class FirstRunDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.channel_name = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("RustyBot - First Time Setup")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(250)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Welcome header
        welcome_label = QLabel("🎉 Welcome to RustyBot!")
        welcome_font = QFont()
        welcome_font.setPointSize(16)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        # Description
        desc_label = QLabel(
            "Let's get you set up! Please enter your Twitch channel name below.\n\n"
            "This is the channel where RustyBot will monitor for giveaway entries."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Channel input section
        input_layout = QVBoxLayout()
        input_layout.setSpacing(10)
        
        channel_label = QLabel("Your Twitch Channel Name:")
        channel_label_font = QFont()
        channel_label_font.setPointSize(10)
        channel_label_font.setBold(True)
        channel_label.setFont(channel_label_font)
        input_layout.addWidget(channel_label)
        
        self.channel_input = QLineEdit()
        self.channel_input.setPlaceholderText("Enter your Twitch username (e.g., your_channel)")
        self.channel_input.setMinimumHeight(35)
        input_font = QFont()
        input_font.setPointSize(11)
        self.channel_input.setFont(input_font)
        self.channel_input.textChanged.connect(self.validate_input)
        self.channel_input.returnPressed.connect(self.accept_setup)
        input_layout.addWidget(self.channel_input)
        
        # Hint label
        hint_label = QLabel("💡 Tip: Don't include 'twitch.tv/' - just your username")
        hint_label.setStyleSheet("color: #888; font-size: 9pt;")
        input_layout.addWidget(hint_label)
        
        layout.addLayout(input_layout)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.ok_button = QPushButton("Continue")
        self.ok_button.setMinimumWidth(120)
        self.ok_button.setMinimumHeight(35)
        self.ok_button.setEnabled(False)
        self.ok_button.clicked.connect(self.accept_setup)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumWidth(120)
        cancel_button.setMinimumHeight(35)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton[text="Cancel"] {
                background-color: #555555;
            }
            QPushButton[text="Cancel"]:hover {
                background-color: #666666;
            }
        """)
    
    def validate_input(self):
        """Enable OK button only if input is valid"""
        text = self.channel_input.text().strip()
        # Remove common prefixes if user includes them
        text = text.replace("twitch.tv/", "").replace("https://", "").replace("http://", "")
        text = text.replace("www.", "").strip("/")
        
        # Channel name should be alphanumeric with underscores
        is_valid = len(text) > 0 and text.replace("_", "").isalnum()
        self.ok_button.setEnabled(is_valid)
    
    def accept_setup(self):
        """Save channel name and close"""
        channel = self.channel_input.text().strip()
        # Clean up the input
        channel = channel.replace("twitch.tv/", "").replace("https://", "").replace("http://", "")
        channel = channel.replace("www.", "").strip("/").lower()
        
        if not channel:
            QMessageBox.warning(self, "Invalid Input", "Please enter a channel name.")
            return
        
        self.channel_name = channel
        self.accept()
    
    @staticmethod
    def show_first_run_setup(parent=None):
        """Show first run dialog and return channel name"""
        dialog = FirstRunDialog(parent)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted and dialog.channel_name:
            return dialog.channel_name
        return None


def check_first_run():
    """Check if this is the first run (no user_config.json exists)"""
    from config_manager import _get_config_path
    config_path = _get_config_path()
    user_config_path = config_path.parent / "user_config.json"
    return not user_config_path.exists()


def save_user_channel(channel_name):
    """Save user's channel to user_config.json"""
    from config_manager import _get_config_path
    config_path = _get_config_path()
    user_config_path = config_path.parent / "user_config.json"
    
    # Create directory if needed
    user_config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save user configuration
    user_config = {
        "twitch_channel": channel_name,
        "first_run_completed": True
    }
    
    with open(user_config_path, 'w', encoding='utf-8') as f:
        json.dump(user_config, f, indent=4)
    
    print(f"✅ Saved user channel: {channel_name}")
    return user_config_path


def load_user_channel():
    """Load user's channel from user_config.json"""
    from config_manager import _get_config_path
    config_path = _get_config_path()
    user_config_path = config_path.parent / "user_config.json"
    
    if not user_config_path.exists():
        return None
    
    try:
        with open(user_config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            return user_config.get("twitch_channel")
    except Exception as e:
        print(f"Warning: Could not load user config: {e}")
        return None


def update_user_channel(new_channel):
    """Update the user's channel (called from options dialog)"""
    from config_manager import get_config_path
    config_path = get_config_path()
    user_config_path = config_path.parent / "user_config.json"
    
    # Load existing config or create new
    if user_config_path.exists():
        try:
            with open(user_config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
        except:
            user_config = {}
    else:
        user_config = {}
    
    # Update channel
    user_config["twitch_channel"] = new_channel.strip().lower()
    user_config["first_run_completed"] = True
    
    # Save
    user_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(user_config_path, 'w', encoding='utf-8') as f:
        json.dump(user_config, f, indent=4)
    
    print(f"✅ Updated user channel to: {new_channel}")
    return new_channel
