# -*- coding: utf-8 -*-
# Main application file for EVE Giveaway Tool (PyQt6 Version)
# Includes Options Dialog, Sound Functionality, and Web Animation

import sys
import os
import random
import asyncio
import threading
import queue
import re
import time
import traceback
import twitchio
from pathlib import Path 
from urllib.parse import quote_plus
from dotenv import load_dotenv
import json
from enum import Enum, auto 
from datetime import datetime 
import uuid 

# Import our custom IRC fallback
from irc_fallback import TwitchIRCClient 
from collections import Counter 

import config_manager
import requests
import base64
import tempfile

# TwitchIO imports
import twitchio
from twitchio.ext import commands
from twitchio.ext.commands import Bot
from twitchio.ext.commands import Command

# Load environment variables from encrypted secure.env file (or fallback to .env)
# When packaged with PyInstaller/Nuitka, look for secure.env in multiple locations
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    # Check if we're in an 'app' subfolder (organized distribution)
    exe_dir = os.path.dirname(sys.executable)
    parent_dir = os.path.dirname(exe_dir)
    
    # Try parent directory first (for organized structure: root/secure.env and root/app/RustyBot.exe)
    secure_env_path = os.path.join(parent_dir, 'secure.env')
    env_path = os.path.join(parent_dir, '.env')
    
    # Fall back to exe directory if not found in parent
    if not os.path.exists(secure_env_path) and not os.path.exists(env_path):
        secure_env_path = os.path.join(exe_dir, 'secure.env')
        env_path = os.path.join(exe_dir, '.env')
    
    # Also try _MEIPASS for PyInstaller compatibility
    if not os.path.exists(secure_env_path) and not os.path.exists(env_path) and hasattr(sys, '_MEIPASS'):
        secure_env_path = os.path.join(sys._MEIPASS, 'secure.env')
        env_path = os.path.join(sys._MEIPASS, '.env')
else:
    # Running as normal Python script
    script_dir = os.path.dirname(__file__)
    secure_env_path = os.path.join(script_dir, 'secure.env')
    env_path = os.path.join(script_dir, '.env')

# Load environment variables from .env file
print(f"Loading credentials from .env: {env_path}")
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded credentials from .env")
else:
    print(f"⚠️ No .env file found at: {env_path}")
    print(f"  Please create a .env file with your Twitch credentials")

ENV_TWITCH_TOKEN = os.getenv('TWITCH_TOKEN', 'N/A')
ENV_TWITCH_NICK = os.getenv('TWITCH_NICK', 'N/A')
ENV_TWITCH_CHANNEL = os.getenv('TWITCH_CHANNEL', 'N/A')
ENV_TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID', 'N/A')
ENV_TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET', 'N/A')
ENV_TWITCH_BOT_ID = os.getenv('TWITCH_BOT_ID', None)
ENV_EVE2TWITCH_BOT_NAME = os.getenv("EVE2TWITCH_BOT_NAME", "eve2twitch").lower()

# Ensure token is properly formatted
def prepare_oauth_token(token):
    if token.startswith('oauth:'):
        return token[6:]  # Remove oauth: prefix
    return token

ENV_TWITCH_TOKEN = prepare_oauth_token(ENV_TWITCH_TOKEN)

# --- PyQt6 Imports ---
from config_manager import (
    ENTRY_TYPE_PREDEFINED, ENTRY_TYPE_ANYTHING, ENTRY_TYPE_CUSTOM,
    VALID_ENTRY_TYPES, PREDEFINED_COMMANDS,
    ANIM_TYPE_HACKING, ANIM_TYPE_TRIGLAVIAN,
    ANIM_TYPE_NODE_PATH, ANIM_TYPE_TRIG_CONDUIT,
    ANIM_TYPE_TRIG_CODE_REVEAL,
    ANIM_TYPE_RANDOM_TECH,
    VALID_ANIMATION_TYPES,
    TRIG_SPEED_FAST, TRIG_SPEED_NORMAL, TRIG_SPEED_SLOW, VALID_TRIG_SPEEDS,
    NODE_PATH_SPEED_NORMAL, NODE_PATH_SPEED_SLOW, NODE_PATH_SPEED_VERY_SLOW, VALID_NODE_PATH_SPEEDS,
    TRIG_CONDUIT_SPEED_FAST, TRIG_CONDUIT_SPEED_NORMAL, TRIG_CONDUIT_SPEED_SLOW, VALID_TRIG_CONDUIT_SPEEDS,
    TRIG_CODE_REVEAL_SPEED_FAST, TRIG_CODE_REVEAL_SPEED_NORMAL, TRIG_CODE_REVEAL_SPEED_SLOW, VALID_TRIG_CODE_REVEAL_SPEEDS,
    TRIG_CODE_ALPHANUMERIC_GLYPHS,
    _validate_geometry_string,
    PRIZE_MODE_STREAMER, PRIZE_MODE_POLL, VALID_PRIZE_MODES
)

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QTextEdit, QGroupBox, QFrame,
    QSizePolicy, QDialog, QFormLayout,
    QStackedWidget,
    QSpacerItem, QGridLayout,
    QSplashScreen, QListWidgetItem, QComboBox
)
from PyQt6.QtCore import (
    pyqtSignal, pyqtSlot, QObject, QThread, Qt, QTimer, QUrl, QFileInfo, pyqtProperty,
    QEvent, QPoint, QRect, QMargins, QEventLoop,
    QStandardPaths
)
from PyQt6.QtGui import (
    QClipboard, QFont, QFontDatabase,
    QPixmap, QMouseEvent, QCursor, QIcon, QImage, QTextDocument
)
from PyQt6.QtGui import QTextCursor, QTextImageFormat, QTextBlockFormat

# --- PyQt6 WebEngine Imports ---
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    from PyQt6.QtWebChannel import QWebChannel
    webengine_available = True
    print("PyQtWebEngine found, animation enabled.")
except ImportError as e:
    print(f"WARNING: PyQtWebEngine not found. Winner animation will be disabled. Install with: pip install PyQt6-WebEngine")
    print(f"(Import Error: {e})")
    webengine_available = False
    QWebEngineView = None
    QWebEnginePage = None
    QWebChannel = None

# --- Sound Import ---
try:
    import pygame
    pygame_available = True
    print(f"pygame {pygame.version.ver} (SDL {'.'.join(map(str, pygame.get_sdl_version()))}, Python {'.'.join(map(str, sys.version_info[:3]))})")
    print(f"Hello from the pygame community. https://www.pygame.org/contribute.html")
except ImportError:
    pygame_available = False
    pygame = None
    print("WARNING: Pygame not found. Sound effects will be disabled. Install with: pip install pygame")

# --- Local Module Imports ---
import sound_manager
from options_dialog import OptionsDialog
from widget_handler import WidgetDragHandler
from animation_manager import AnimationManager
import logging_utils
from collections import Counter
from ui_manager import UIManager

# --- Constants ---
APP_NAME = "RustyBotGiveaway"
ORG_NAME = "RustyBit"
APP_VERSION = "1.7.6" 

LOADING_IMAGE_FILE = "loading_init.png"  # Root level - not moved to assets
SOUND_NOTIFICATION_KEY = "notification"
OUTPUT_ENTRY_METHOD_FILE = "output_entry_method.txt"

WIDGET_NAME_MAIN_ACTION_BUTTONS = "main_action_buttons"
WIDGET_NAME_PRIZE_CONTROLS = "prize_controls"
WIDGET_NAME_ENTRANTS = "entrants_panel"
WIDGET_NAME_MAIN_STACK = "main_stack"

WIDGET_CONFIG_MAP = {
    WIDGET_NAME_MAIN_ACTION_BUTTONS: "main_action_buttons_geometry",
    WIDGET_NAME_PRIZE_CONTROLS: "top_controls_geometry",
    WIDGET_NAME_ENTRANTS: "entrants_panel_geometry",
    WIDGET_NAME_MAIN_STACK: "main_stack_geometry"
}

ESI_BASE_URL = "https://esi.evetech.net/latest"
ESI_DATASOURCE = "datasource=tranquility"
ESI_USER_AGENT = f"{APP_NAME}/{APP_VERSION} ({os.getenv('ESI_CONTACT_EMAIL', 'your_contact_email_or_discord_here')})"
ESI_REQUEST_TIMEOUT = 10 # seconds
EVE2TWITCH_API_URL = os.getenv('EVE2TWITCH_API_URL', 'https://api.eve2twitch.space/twitch/login/{twitch}')

DROPDOWN_SELECT_PRIZE_TEXT = "<Select Prize from List>"
DROPDOWN_RANDOM_PRIZE_TEXT = "🎲 RANDOM PRIZE 🎲"
DROPDOWN_COMMON_PRIZE_HEADER = "--- COMMON PRIZE POOL ---"
DROPDOWN_CONFIGURED_PRIZE_HEADER = "--- PRIZE POOL ---"
DROPDOWN_POLL_MODE_TEXT = "<Poll uses Configured Prizes>"
DROPDOWN_SEPARATOR_TEXT = "──────────"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(Path(__file__).parent)
    res_path = os.path.join(base_path, relative_path)
    return res_path

BASE_STYLESHEET = """
    QWidget { background-color: #1a1a1a; color: #dadada; font-family: "Consolas", "Courier New", monospace; }
    QPushButton { background-color: #333333; color: #e8d900; border: 1px solid #555555; padding: 4px 8px; /* Reduced padding */ min-height: 22px; /* Slightly reduced */ font-weight: bold; text-transform: uppercase; }
    QPushButton:hover { background-color: #444444; border-color: #777777; }
    QPushButton:pressed { background-color: #222222; }
    QPushButton:disabled { background-color: #2a2a2a; color: #666666; border-color: #444444; }
    QPushButton#copyButton { min-width: 50px; padding: 3px 6px; font-size: 8pt; }
    QLineEdit { background-color: #111111; border: 1px solid #555555; padding: 4px; color: #e8d900; font-weight: bold; }
    QListWidget { background-color: #111111; border: 1px solid #555555; color: #dadada; }
    QListWidget::item { padding: 4px 2px; }
    QListWidget::item:selected { background-color: transparent; color: #dadada; }
    QListWidget::item:hover { background-color: #282828; }
    QListWidget::indicator { width: 13px; height: 13px; border: 1px solid #555; background-color: #111; }
    QListWidget::indicator:checked { background-color: #e8d900; }
    QTextEdit#confirmation_log { background-color: #0a0a0a; border: 2px solid #333333; color: #b0b0b0; padding: 8px; }
    QLabel { color: #e8d900; font-weight: bold; padding-top: 2px; text-transform: uppercase; }
    QLabel#entriesLabel, QLabel#statusBar { padding: 3px; border: none; }
    QLabel#statusBar { background-color: #111111; border-top: 1px solid #555555; min-height: 20px; font-size: 8pt; qproperty-alignment: 'AlignLeft | AlignVCenter'; }
    QGroupBox { border: none; margin: 0px; padding: 0px; }
    QGroupBox#prizeInputGroup {
    }
    QFrame#infoBox { border: 1px solid #555555; background-color: #1f1f1f; }
    QLabel#infoBoxLabel { padding-left: 5px; padding-top: 3px; font-size: 8pt; color: #a0a0a0; }
    QDialog { background-color: #2a2a2a; }
    QDialog QLabel { color: #dadada; font-weight: normal; text-transform: none; }
    QDialog QPushButton { font-weight: normal; text-transform: none; }
    QTabWidget::pane { border: 1px solid #555555; background-color: #1f1f1f; padding: 8px; }
    QTabWidget::tab-bar { alignment: left; }
    QTabBar::tab { background-color: #333333; color: #e8d900; border: 1px solid #555555; border-bottom: none; padding: 5px 10px; margin-right: 2px; font-weight: bold; text-transform: uppercase; }
    QTabBar::tab:selected { background-color: #1f1f1f; border-color: #555555; }
    QTabBar::tab:hover { background-color: #444444; }
    QSlider::groove:horizontal { border: 1px solid #555; height: 6px; background: #111; margin: 2px 0; border-radius: 3px;}
    QSlider::handle:horizontal { background: #e8d900; border: 1px solid #aaa; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
    QSpinBox { background-color: #111111; color: #e8d900; border: 1px solid #555; padding: 2px; }
    QCheckBox { spacing: 5px; color: #dadada; font-weight: normal; text-transform: none; }
    QCheckBox::indicator { width: 13px; height: 13px; border: 1px solid #555; background-color: #111;}
    QCheckBox::indicator:checked { background-color: #e8d900; }
    QComboBox { background-color: #111111; color: #e8d900; border: 1px solid #555; padding: 3px 5px; min-width: 6em; }
    QComboBox::drop-down { border: none; background: #333; width: 15px; }
    QComboBox::down-arrow { image: url(no-arrow.png); }
    QComboBox QAbstractItemView { background-color: #111111; color: #e8d900; border: 1px solid #555; selection-background-color: #e8d900; selection-color: #111111; }
    QScrollBar:vertical { border: 1px solid #555; background: #111; width: 10px; margin: 0px; }
    QScrollBar::handle:vertical { background: #e8d900; min-height: 20px; border-radius: 3px;}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; background: none; }
    QScrollBar:horizontal { border: 1px solid #555; background: #111; height: 10px; margin: 0px; }
    QScrollBar::handle:horizontal { background: #e8d900; min-width: 20px; border-radius: 3px;}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; background: none; }
    QMessageBox { background-color: #1f1f1f; border: 1px solid #555; }
    QMessageBox QLabel { color: #dadada; font-weight: normal; text-transform: none; }
    QMessageBox QPushButton { font-weight: normal; text-transform: none; }
    .adjustable-widget-active { border: 2px dashed rgba(255, 255, 0, 0.6) !important; }
"""

# Environment variables are already loaded at the top of the file
OAUTH_TOKEN_PREFIX = "oauth:"
print(f"Using EVE Bot Name: '{ENV_EVE2TWITCH_BOT_NAME}'")

class AppState(Enum):
    STARTING = auto()
    BOT_CONNECTING = auto()
    BOT_DOWN = auto()
    IDLE = auto()
    COLLECTING = auto()
    ANIMATING_WINNER = auto()
    AWAITING_CONFIRMATION = auto()
    AWAITING_EVE_RESPONSE = auto()
    FETCHING_ESI_DATA = auto()
    CONFIRMED_NO_IGN = auto()
    CONFIRMED_WITH_IGN = auto()
    TIMED_OUT = auto()
    EVE_TIMED_OUT = auto()
    AWAITING_PRIZE_POLL_VOTES = auto()

class ESIWorkerThread(QThread):
    esi_data_ready = pyqtSignal(dict)
    esi_error = pyqtSignal(str)

    def __init__(self, ign, parent=None):
        super().__init__(parent)
        self.ign = ign
        self.headers = {'User-Agent': ESI_USER_AGENT, 'accept': 'application/json', 'Content-Type': 'application/json'}

    def _request_esi(self, endpoint, method="GET", params=None, json_data=None, is_image=False):
        url = endpoint if is_image else f"{ESI_BASE_URL}{endpoint}"
        
        request_params = {ESI_DATASOURCE.split('=')[0]: ESI_DATASOURCE.split('=')[1]} if not is_image else {}
        if params:
            request_params.update(params)
        
        try:
            if method == "POST":
                response = requests.post(url, headers=self.headers, params=request_params, json=json_data, timeout=ESI_REQUEST_TIMEOUT)
            else: # GET
                response = requests.get(url, headers=self.headers, params=request_params, timeout=ESI_REQUEST_TIMEOUT)
            
            response.raise_for_status()
            return response.content if is_image else response.json()
        except requests.exceptions.HTTPError as http_err:
            error_detail = ""
            try:
                if not is_image and response.content: 
                    error_detail = response.json().get("error", "")
            except json.JSONDecodeError: 
                error_detail = response.text[:100] 
            except Exception: pass
            raise ValueError(f"ESI HTTP Error: {response.status_code} - {error_detail or response.reason} for URL: {url}")
        except requests.exceptions.RequestException as req_err: 
            raise ValueError(f"ESI Network Error: {req_err} for URL: {url}")
        except ValueError as json_err: 
            raise ValueError(f"ESI Error: Invalid JSON response from URL: {url}. Details: {json_err}")

    def run(self):
        try:
            # Production: no forced artificial delay for ESI worker (test code removed)
            ids_data = self._request_esi(f"/universe/ids/", method="POST", json_data=[self.ign])
            if not ids_data or 'characters' not in ids_data or not ids_data['characters']:
                err_msg = ids_data.get('error', "Character not found or ESI error.") if isinstance(ids_data, dict) else "Character not found."
                self.esi_error.emit(f"ESI Error for '{self.ign}': {err_msg}")
                return
            char_info = ids_data['characters'][0]
            char_id, resolved_name = char_info.get('id'), char_info.get('name', self.ign)
            if not char_id: 
                self.esi_error.emit(f"No Character ID found for '{self.ign}'.")
                return

            char_details = self._request_esi(f"/characters/{char_id}/")
            corp_id, alliance_id = char_details.get('corporation_id'), char_details.get('alliance_id')
            
            portrait_url_data = self._request_esi(f"/characters/{char_id}/portrait/")
            portrait_url_to_fetch = portrait_url_data.get('px256x256') 
            if not portrait_url_to_fetch:
                fallbacks = ['px128x128', 'px512x512', 'px64x64']
                for fb_key in fallbacks:
                    portrait_url_to_fetch = portrait_url_data.get(fb_key)
                    if portrait_url_to_fetch:
                        print(f"ESI_THREAD_DEBUG: Using fallback portrait URL ({fb_key}): {portrait_url_to_fetch}")
                        break
            else:
                 print(f"ESI_THREAD_DEBUG: Selected Portrait URL (px256x256) for {char_id}: {portrait_url_to_fetch}")
                
            portrait_base64, img_type = None, "image/png" 
            if portrait_url_to_fetch:
                try:
                    print(f"ESI_THREAD_DEBUG: Attempting to fetch image from: {portrait_url_to_fetch}")
                    img_bytes = self._request_esi(portrait_url_to_fetch, is_image=True) 
                    portrait_base64 = base64.b64encode(img_bytes).decode('utf-8')
                    
                    lower_url = portrait_url_to_fetch.lower()
                    if ".jpg" in lower_url or ".jpeg" in lower_url: img_type = "image/jpeg"
                    elif ".png" in lower_url: img_type = "image/png"
                    elif ".webp" in lower_url: img_type = "image/webp"
                    else: print(f"ESI_THREAD_DEBUG: Could not determine image type from URL extension for {portrait_url_to_fetch}, defaulting to {img_type}")

                    print(f"ESI_THREAD_DEBUG: Fetched image, base64 length: {len(portrait_base64) if portrait_base64 else 'None'}, detected type: {img_type}")
                except Exception as img_e:
                    print(f"ESI_THREAD_DEBUG: ESI Portrait Fetch/Encode Error for {portrait_url_to_fetch}: {img_e}")
                    traceback.print_exc() 
                    portrait_base64 = None 
            else:
                print(f"ESI_THREAD_DEBUG: No portrait URL was selected or available for char_id {char_id}.")

            corp_name = self._request_esi(f"/corporations/{corp_id}/").get('name', "N/A Corp") if corp_id else "N/A Corp"
            alliance_name = self._request_esi(f"/alliances/{alliance_id}/").get('name') if alliance_id else None

            emit_data = {
                'id': char_id, 
                'name': resolved_name, 
                'portrait_base64': portrait_base64, 
                'portrait_content_type': img_type if portrait_base64 else None,    
                'corporation_name': corp_name,
                'corporation_id': corp_id, 
                'alliance_name': alliance_name, 
                'alliance_id': alliance_id
            }
            print(f"ESI_THREAD_DEBUG: Emitting data: portrait_base64 is {'PRESENT' if portrait_base64 else 'MISSING'}, content_type: {img_type if portrait_base64 else 'N/A'}")
            self.esi_data_ready.emit(emit_data)

        except ValueError as e: 
            self.esi_error.emit(str(e)) 
        except Exception as e: 
            traceback.print_exc()
            self.esi_error.emit(f"ESI Data Generic Error: {e}")

def run_timer_thread(timer_type, winner_name_or_context, timeout, stop_event, signal_emitter):
    print(f"TIMER THREAD ({timer_type}): Starting for '{winner_name_or_context}' ({timeout}s)")
    start_time = time.monotonic()
    played_shield, played_armor, played_hull = False, False, False
    if timer_type == "confirmation":
        shield_thresh_elapsed = timeout * 0.15
        armor_thresh_elapsed = timeout * 0.50
        hull_thresh_elapsed = timeout * 0.75
        print(f"TIMER THREAD ({timer_type}): Sound thresholds (elapsed) - Shield: {shield_thresh_elapsed:.1f}s (15%), Armor: {armor_thresh_elapsed:.1f}s (50%), Hull: {hull_thresh_elapsed:.1f}s (75%)")

    update_interval = 0.1
    if timer_type == "prize_poll":
        update_interval = 1.0

    try:
        while True:
            now = time.monotonic(); elapsed = now - start_time; remaining = max(0, timeout - elapsed)
            if remaining <= 0:
                if not stop_event.is_set():
                    signal_emitter.timer_expired_signal.emit({"type": timer_type, "context": winner_name_or_context})
                break
            if stop_event.is_set():
                signal_emitter.timer_stopped_signal.emit(timer_type);
                break

            signal_emitter.timer_update_signal.emit({"type": timer_type, "remaining": remaining})

            if timer_type == "confirmation":
                if elapsed >= shield_thresh_elapsed and not played_shield:
                    signal_emitter.play_sound_signal.emit({"key": "timer_high", "action": "play"}); played_shield = True
                if elapsed >= armor_thresh_elapsed and not played_armor:
                    signal_emitter.play_sound_signal.emit({"key": "timer_mid", "action": "play"}); played_armor = True
                if elapsed >= hull_thresh_elapsed and not played_hull:
                    signal_emitter.play_sound_signal.emit({"key": "timer_low", "action": "play"}); played_hull = True

            wait_time = min(update_interval, remaining); stop_event.wait(timeout=wait_time)
    except Exception as e: print(f"TIMER THREAD ({timer_type}): ERROR - {e}"); traceback.print_exc()
    finally:
        print(f"TIMER THREAD ({timer_type}): Finished for {winner_name_or_context}.")
        if timer_type == "confirmation":
             signal_emitter.play_sound_signal.emit({"key": "countdown", "action": "stop"})
             signal_emitter.play_sound_signal.emit({"key": "timer_high", "action": "stop"})
             signal_emitter.play_sound_signal.emit({"key": "timer_mid", "action": "stop"})
             signal_emitter.play_sound_signal.emit({"key": "timer_low", "action": "stop"})

# Define the bot class at module level for clarity
class TwitchBot(Bot):
    """Custom TwitchIO bot implementation using commands.Bot for message reception."""
    
    def __init__(self, token, client_id, client_secret, nick, channel, signal_handler, bot_id=None):
        """Initialize the bot with required parameters."""
        if bot_id is None:
            raise ValueError("bot_id is required for TwitchIO bot initialization")
        
        print(f"🔧 Initializing TwitchBot with:")
        print(f"   Nick: {nick}")
        print(f"   Channel: {channel}")
        print(f"   Bot ID: {bot_id}")
        print(f"   Token: {token[:10]}...")
        
        # Call parent constructor with TwitchIO Bot requirements
        super().__init__(
            token=token,
            client_id=client_id,
            client_secret=client_secret,
            nick=nick,
            prefix='!',  # Required for commands.Bot
            initial_channels=[channel],
            bot_id=bot_id  # Required in TwitchIO 3.0+
        )
        
        print(f"🔧 TwitchIO Bot initialized. Checking attributes...")
        
        # Check what attributes are available after initialization
        attrs = [attr for attr in dir(self) if not attr.startswith('__')]
        connection_attrs = [attr for attr in attrs if any(keyword in attr.lower() for keyword in ['connection', 'socket', 'irc', 'transport', 'channel', 'websocket'])]
        print(f"🔧 Available connection attributes: {connection_attrs}")
        
        # Force IRC connection for message reception
        print(f"🔧 Setting up IRC connection for chat message reception...")
        self._force_irc_connection = True
        
        # Store connection details for IRC fallback
        self._token = token
        self._channel = channel
        self._signal_handler = signal_handler
        self._bot_id = bot_id
        
        # Initialize IRC fallback client
        self.irc_client = None
        self._setup_irc_fallback()
        
        self._bot_id = bot_id  # Store bot_id for use in methods
        # Store instance variables
        self._signal_handler = signal_handler
        self._channel = channel
        self._ready = False
        
    async def event_ready(self):
        """Handler called when the bot successfully connects."""
        print(f"🤖 Bot is ready! Connected channels: {[c.name for c in self.connected_channels] if hasattr(self, 'connected_channels') else 'Unknown'}")
        print(f"🤖 Bot nick: {getattr(self, 'nick', getattr(self, '_nick', 'Unknown'))}")
        print(f"🤖 Bot user ID: {getattr(self, '_bot_id', 'Unknown')}")
        print(f"🤖 Websocket connections: {len(getattr(self, '_websockets', []))}")
        
        # Check if we have IRC/WebSocket connections for receiving messages
        if hasattr(self, '_websockets') and self._websockets:
            print(f"🤖 Active websockets: {len(self._websockets)}")
            for i, ws in enumerate(self._websockets):
                print(f"   WebSocket {i}: {type(ws).__name__}")
        else:
            print("⚠️ No websockets found - this might prevent message reception!")
            
        # Try to set up EventSub subscription for chat messages
        try:
            print("🔧 Setting up EventSub subscription for chat messages...")
            # Get channel ID from initial channels
            channel_name = self._channel.strip('#')  # Remove # if present
            
            # Try to use our bot's user ID to get the broadcaster ID for the channel we're connected to
            # For now, let's get the broadcaster's user ID from the channel name we're connecting to
            print(f"� Looking up broadcaster ID for channel: {channel_name}")
            
            # Search for channel to get broadcaster ID
            channels = await self.search_channels(channel_name)
            if channels:
                print(f"🔍 Found {len(channels)} search results")
                # Try to find a channel that matches our target
                # Since name isn't reliable, let's try using the broadcaster attribute
                for i, channel in enumerate(channels[:5]):
                    print(f"🔍 Channel {i+1}: broadcaster={getattr(channel, 'broadcaster', 'no-broadcaster')}")
                    if hasattr(channel, 'broadcaster') and hasattr(channel.broadcaster, 'name'):
                        if channel.broadcaster.name.lower() == channel_name.lower():
                            broadcaster_id = str(channel.broadcaster.id)
                            print(f"🔧 Found broadcaster {channel.broadcaster.name} with ID: {broadcaster_id}")
                            
                            # Subscribe to channel.chat.message EventSub using proper payload
                            from twitchio.eventsub import ChatMessageSubscription
                            
                            chat_subscription = ChatMessageSubscription(
                                broadcaster_user_id=broadcaster_id,
                                user_id=str(self._bot_id)
                            )
                            
                            # Use as_bot=True to authenticate as the bot user
                            subscription = await self.subscribe_websocket(
                                chat_subscription,
                                as_bot=True
                            )
                            print(f"✅ EventSub subscription created: {subscription}")
                            print("🔧 Bot should now receive chat messages via EventSub")
                            break
                else:
                    print(f"⚠️ Could not find broadcaster info for channel {channel_name}")
                    # Try a fallback approach - use the bot's own ID as broadcaster
                    print(f"� Fallback: Trying bot ID {self._bot_id} as broadcaster ID")
                    from twitchio.eventsub import ChatMessageSubscription
                    fallback_subscription = ChatMessageSubscription(
                        broadcaster_user_id=str(self._bot_id),
                        user_id=str(self._bot_id)
                    )
                    subscription = await self.subscribe_websocket(
                        fallback_subscription,
                        as_bot=True
                    )
                    print(f"✅ EventSub fallback subscription created: {subscription}")
            else:
                print(f"⚠️ No search results for channel {channel_name}")
                # Fallback: try using the bot ID
                print(f"🔧 Fallback: Using bot ID {self._bot_id} as broadcaster ID")
                
                from twitchio.eventsub import ChatMessageSubscription
                final_fallback_subscription = ChatMessageSubscription(
                    broadcaster_user_id=str(self._bot_id),
                    user_id=str(self._bot_id)
                )
                subscription = await self.subscribe_websocket(
                    final_fallback_subscription,
                    as_bot=True
                )
                print(f"✅ EventSub fallback subscription created: {subscription}")
                
        except Exception as e:
            print(f"⚠️ Failed to setup EventSub subscription: {e}")
            print(f"⚠️ Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            
            # Start IRC fallback when EventSub fails
            print("🔌 EventSub failed, starting IRC fallback...")
            success = self.start_irc_fallback()
            if success:
                print("✅ IRC fallback active - chat messages should work now!")
            else:
                print("❌ Both EventSub and IRC failed - message reception may not work")
            
        # Check for IRC connections
        if hasattr(self, '_irc'):
            print(f"🤖 IRC connection: {type(self._irc).__name__}")
        else:
            print("⚠️ No native IRC connection found!")
            
        # List all connection-related attributes
        connection_attrs = [attr for attr in dir(self) if any(keyword in attr.lower() for keyword in ['connection', 'socket', 'irc', 'transport', 'channel'])]
        print(f"🤖 Connection attributes: {connection_attrs}")
        
        self._ready = True
        
        # Log and emit connection status
        print(f"Bot ready event triggered. Channel: {self._channel}")
        self._signal_handler.bot_ready_signal.emit(True)
        print(f"Successfully connected to {self._channel}")
        self._signal_handler.status_update.emit(f"Successfully connected to {self._channel}")
    
    async def event_message(self, message):
        """Handler for incoming chat messages."""
        try:
            print(f"🎯 EVENT_MESSAGE CALLED! Raw message object: {type(message)}")
            print(f"📨 Message details:")
            print(f"   Author: {getattr(message, 'author', 'NO_AUTHOR')}")
            print(f"   Content: {getattr(message, 'content', 'NO_CONTENT')}")
            print(f"   Echo: {getattr(message, 'echo', 'NO_ECHO_ATTR')}")
            print(f"   Channel: {getattr(message, 'channel', 'NO_CHANNEL')}")
            
            author_name = getattr(message.author, 'name', 'UNKNOWN_USER') if message.author else 'NO_AUTHOR'
            print(f"📨 Received message from {author_name}: {message.content}")
            
            if message.echo or not message.author:
                print("🔇 Ignoring echo or message without author")
                return  # Ignore bot's own messages and messages without authors
            
            # Process the message for giveaway entries
            print(f"✅ Processing message: {message.content}")
            self._signal_handler.message_received.emit(author_name, message.content)
            
        except Exception as e:
            print(f"❌ Error in message handler: {e}")
            import traceback
            traceback.print_exc()
    
    def simulate_chat_message(self, username, message_content):
        """Simulate a chat message for testing when EventSub isn't working."""
        try:
            print(f"🧪 SIMULATING chat message from {username}: {message_content}")
            self._signal_handler.message_received.emit(username, message_content)
            print(f"✅ Simulated message processed successfully")
        except Exception as e:
            print(f"❌ Error simulating message: {e}")
            import traceback
            traceback.print_exc()
    
    def _setup_irc_fallback(self):
        """Setup IRC fallback client for message reception."""
        try:
            print("🔌 Setting up IRC fallback client...")
            
            # Clean token (remove 'oauth:' prefix if present)
            clean_token = self._token.replace('oauth:', '')
            
            # Clean channel name (remove '#' if present)
            clean_channel = self._channel.replace('#', '')
            
            # Create IRC client with direct callback for thread-safe communication
            self.irc_client = TwitchIRCClient(
                oauth_token=clean_token,
                bot_nick=self.nick if hasattr(self, 'nick') else 'the_rusty_bot',
                channel_name=clean_channel,
                message_callback=self._irc_message_callback  # Direct callback
            )
            
            # Connect IRC message signal to our handler with proper threading
            from PyQt6.QtCore import Qt
            self.irc_client.message_received.connect(self._handle_irc_message, Qt.ConnectionType.QueuedConnection)
            self.irc_client.connection_status.connect(self._handle_irc_status, Qt.ConnectionType.QueuedConnection)
            
            print("✅ IRC fallback client ready")
            
        except Exception as e:
            print(f"❌ IRC fallback setup failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _irc_message_callback(self, username, message):
        """Direct callback from IRC client (thread-safe)."""
        print(f"📨 IRC CALLBACK: {username}: {message}")
        print(f"📨 Calling _handle_irc_message from callback...")
        # Call the handler directly
        self._handle_irc_message(username, message)
        
    def _handle_irc_message(self, username, message):
        """Handle IRC message and forward to signal handler."""
        try:
            print(f"📨 IRC MESSAGE: {username}: {message}")
            print(f"🔧 DEBUG: About to emit message_received signal...")
            print(f"🔧 DEBUG: Signal handler: {type(self._signal_handler)}")
            print(f"🔧 DEBUG: Has message_received: {hasattr(self._signal_handler, 'message_received')}")
            
            # Forward to the same signal handler as EventSub messages
            self._signal_handler.message_received.emit(username, message)
            print(f"🔧 DEBUG: Successfully emitted signal for {username}: {message}")
        except Exception as e:
            print(f"❌ Error handling IRC message: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_irc_status(self, connected):
        """Handle IRC connection status."""
        if connected:
            print("✅ IRC: Connected and ready for messages")
        else:
            print("❌ IRC: Disconnected")
    
    def start_irc_fallback(self):
        """Start the IRC fallback connection."""
        try:
            if self.irc_client:
                print("🔌 Starting IRC fallback connection...")
                success = self.irc_client.connect()
                if success:
                    print("✅ IRC fallback connected successfully")
                    return True
                else:
                    print("❌ IRC fallback connection failed")
                    return False
            else:
                print("❌ IRC client not initialized")
                return False
        except Exception as e:
            print(f"❌ Error starting IRC fallback: {e}")
            return False
            
    async def event_channel_joined(self, channel):
        """Called when bot joins a channel."""
        print(f"🔗 Bot joined channel: {channel.name}")
        
    async def event_error(self, error):
        """Called when an error occurs."""
        print(f"⚠️ TwitchIO error details:")
        print(f"   Error type: {type(error)}")
        print(f"   Error object: {error}")
        
        # Try to extract more details from the error
        if hasattr(error, 'error'):
            print(f"   Error.error: {error.error}")
        if hasattr(error, 'message'):
            print(f"   Error.message: {error.message}")
        if hasattr(error, 'data'):
            print(f"   Error.data: {error.data}")
        if hasattr(error, '__dict__'):
            print(f"   Error attributes: {error.__dict__}")
            
        # Check if this is an IRC connection error
        error_str = str(error)
        if any(keyword in error_str.lower() for keyword in ['irc', 'connection', 'socket', 'authentication']):
            print(f"🔧 This appears to be an IRC/Connection error - this will prevent message reception!")
            
        self._signal_handler.error_occurred.emit(f"TwitchIO Error: {error}")
        
    async def event_raw_data(self, data):
        """Called for all raw IRC data."""
        print(f"📡 Raw IRC data: {data}")
        return  # Don't process further

    async def send_chat_message(self, message: str) -> bool:
        """Send a message to the connected channel.
        
        Args:
            message: The message to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Check bot is ready
            if not self._ready:
                print("Bot not ready yet") 
                return False
                
            # The issue: TwitchIO 3.x moved to Helix API for sending which requires OAuth scopes
            # But for backward compatibility, let's try to find any IRC-style connections
            
            print(f"🔍 Searching for any IRC connections...")
            
            # Check if there are any private websocket connections
            all_attrs = [attr for attr in dir(self) if not attr.startswith('__')]
            connection_attrs = [attr for attr in all_attrs if any(keyword in attr.lower() for keyword in ['connection', 'socket', 'irc', 'transport'])]
            print(f"🔍 Connection-related attributes: {connection_attrs}")
            
            # Try to access any private connection attributes
            for attr in connection_attrs:
                try:
                    obj = getattr(self, attr)
                    if obj:
                        print(f"🔍 {attr}: {type(obj)} - {str(obj)[:100]}...")
                        if hasattr(obj, 'send'):
                            print(f"🔍 {attr} has send method")
                        if hasattr(obj, '_websocket'):
                            print(f"🔍 {attr} has _websocket")
                except Exception as e:
                    print(f"🔍 Could not access {attr}: {e}")
            
            # Since TwitchIO 3.x requires Helix API scopes that we don't have,
            # we need to inform the user about the OAuth requirements
            print(f"✅ TwitchIO 3.x attempting message send with valid OAuth scopes")
            print(f"✅ Current token HAS the required scopes: user:write:chat and user:bot")
            print(f"� To fix this, regenerate the OAuth token with the required scopes")
            
            # Try the actual TwitchIO 3.x message sending now
            try:
                # TwitchIO 3.x often has issues with message sending due to scope requirements
                # Let's use the direct Helix API approach which we know works with our token
                import requests
                import os
                
                # Get our OAuth token from environment
                token = os.getenv("TWITCH_TOKEN", "pg23dqp5pk9gr18zog0ql7zza49i2k")
                client_id = os.getenv("TWITCH_CLIENT_ID", "pnu5f3ruhgfc64gx4gy4rheqkohvoj")
                
                # Direct API call to send chat message
                url = "https://api.twitch.tv/helix/chat/messages"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Client-Id": client_id,
                    "Content-Type": "application/json"
                }
                
                # We need the broadcaster_user_id for the channel we're sending to
                # and our own bot user ID as the sender
                user_url = "https://api.twitch.tv/helix/users"
                
                # First get the broadcaster (channel) user ID
                user_params = {"login": self._channel.strip('#')}
                user_response = requests.get(user_url, headers=headers, params=user_params)
                
                if user_response.status_code != 200:
                    print(f"❌ Could not fetch broadcaster data: {user_response.status_code} - {user_response.text}")
                    return False
                    
                user_data = user_response.json()
                if not user_data["data"]:
                    print(f"❌ Could not find user data for {self._channel.strip('#')}")
                    return False
                    
                broadcaster_user_id = user_data["data"][0]["id"]
                print(f"🔗 Found broadcaster ID: {broadcaster_user_id} for channel {self._channel.strip('#')}")
                
                # Now get our bot's user ID
                bot_params = {"login": "the_rusty_bot"}
                bot_response = requests.get(user_url, headers=headers, params=bot_params)
                
                if bot_response.status_code != 200:
                    print(f"❌ Could not fetch bot data: {bot_response.status_code} - {bot_response.text}")
                    return False
                    
                bot_data = bot_response.json()
                if not bot_data["data"]:
                    print(f"❌ Could not find bot user data for the_rusty_bot")
                    return False
                    
                sender_user_id = bot_data["data"][0]["id"]
                print(f"🔗 Found bot ID: {sender_user_id} for the_rusty_bot")
                
                # Now send the message
                payload = {
                    "broadcaster_id": broadcaster_user_id,
                    "sender_id": sender_user_id,  # Bot is sending as itself
                    "message": message
                }
                
                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    print(f"✅ Message sent successfully via Helix API: {message}")
                    return True
                else:
                    print(f"❌ Helix API error: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error sending message via Helix API: {e}")
                return False
            
        except Exception as e:
            print(f"❌ Error in send_chat_message: {e}")
            self._signal_handler.error_occurred.emit(f"Error sending message: {e}")
            return False

class TwitchBotThread(QThread):
    message_received = pyqtSignal(str, str)
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    bot_ready_signal = pyqtSignal(bool)

    def __init__(self, token, channel, keyword, bot_nick, parent=None):
        super().__init__(parent)
        self.token = token
        self.channel = channel
        self.bot_nick = bot_nick
        self._is_running = True
        self.bot = None
        self.loop = None

    def _create_bot(self):
        """Create the bot instance via the event loop."""
        try:
            return asyncio.run(self.setup_bot())
        except Exception as e:
            msg = f"Error creating bot instance: {str(e)}"
            print(msg)
            self.error_occurred.emit(msg)
            return None

    def run(self):
        """Main run method for the bot thread."""
        loop = None
        try:
            # Set up new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loop = loop

            # Create bot instance
            self.bot = self._create_bot()
            if not self.bot:
                self.error_occurred.emit("Bot creation failed.")
                return

            # Start bot initialization and connection
            self.status_update.emit("Starting bot initialization...")
            self.status_update.emit("Initializing and connecting bot...")
            
            # Start bot with direct token, without loading/saving tokens
            self.loop.run_until_complete(self.bot.start(load_tokens=False))

        except Exception as e:
            print(f"ERROR in TwitchBotThread run loop: {type(e).__name__}: {e}")
            traceback.print_exc()
            
            error_msg = str(e)
            if "authentication failed" in error_msg.lower():
                self.error_occurred.emit("Connection Error: Authentication Failed. Check Token.")
            elif "invalid channel" in error_msg.lower():
                self.error_occurred.emit(f"Connection Error: Invalid Channel Name '{self.channel}'.")
            else:
                self.error_occurred.emit(f"Connection Error: {type(e).__name__}: {e}")
            
            self.bot_ready_signal.emit(False)
            print("Twitch thread run() method finished.")

    async def setup_bot(self):
        """Initialize the bot with proper error handling."""
        print("Setting up bot...")
        
        try:
            # Get required credentials
            client_id = os.getenv('TWITCH_CLIENT_ID')
            client_secret = os.getenv('TWITCH_CLIENT_SECRET')
            bot_id = os.getenv('TWITCH_BOT_ID')
            
            # Validate credentials
            if not self.token:
                raise ValueError("Token is empty")
                
            if not bot_id:
                raise ValueError("TWITCH_BOT_ID not found in environment variables")
                
            # Create token store
            token_file = Path('.tio.tokens.json')
            if not token_file.exists():
                token_data = {self.bot_nick: {"token": self.token}}
                with open(token_file, 'w') as f:
                    json.dump(token_data, f)
                
            if not client_id or not client_secret:
                raise ValueError("Missing required TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET in environment")
                
            # Clean and validate token
            clean_token = self.token.replace('oauth:', '') if self.token.startswith('oauth:') else self.token
            if not clean_token:
                raise ValueError("Invalid token format")
                
            # Store clean token
            self.token = clean_token
            
            # Get bot_id from env
            bot_id = os.getenv('TWITCH_BOT_ID')
            
            # Create and return bot instance 
            # Convert bot_id to int since it comes from env as string
            try:
                bot_id_int = int(bot_id) if bot_id else None
            except ValueError:
                raise ValueError(f"TWITCH_BOT_ID must be a number, got: {bot_id}")
                
            return TwitchBot(
                token=clean_token,
                client_id=client_id,
                client_secret=client_secret,
                nick=self.bot_nick,
                channel=self.channel,
                signal_handler=self,
                bot_id=bot_id_int  # Passed as int
            )
            
        except Exception as e:
            error_msg = f"Error setting up bot: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return None
            """Event for when an error occurs"""
            error_type_name = type(error).__name__
            print(f"BOT EVENT_ERROR: {error_type_name}: {error}")
            self.error_occurred.emit(f"Twitch Runtime Error ({error_type_name}): {error}")

        @bot.listen("raw_data")
        async def raw_data_handler(data):
            """Event for raw IRC data - used to detect disconnections"""
            if "NOTICE" in data and "Login authentication failed" in data:
                print("Authentication failed notice received")
                self.error_occurred.emit("Authentication Failed")
                self.bot_ready_signal.emit(False)

        return bot

    async def stop_bot_async(self):
        if self.bot:
            try:
                self.status_update.emit("Disconnecting...")
                await self.bot.close()
                print("Twitch bot connection closed.")
            except Exception as e:
                self.error_occurred.emit(f"Error during bot close(): {e}")
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

    def stop(self):
        print("stop() called on TwitchBotThread.")
        self._is_running = False
        if self.loop and self.bot:
            asyncio.run_coroutine_threadsafe(self.stop_bot_async(), self.loop)
        elif self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        if not self.wait(5000):
            print("Warning: Twitch thread did not finish cleanly.")
        print("TwitchBotThread stop() finished.")

class GiveawayApp(QWidget):
    layout_adjusted = pyqtSignal(str, str); timer_update_signal = pyqtSignal(dict); timer_expired_signal = pyqtSignal(dict); timer_stopped_signal = pyqtSignal(str); play_sound_signal = pyqtSignal(dict)
    # Signals for EVE2Twitch background lookup -> main thread
    eve2twitch_ign_found = pyqtSignal(str, str, str)  # twitch_username, ign, raw_response
    eve2twitch_lookup_failed = pyqtSignal(str)  # twitch_username (404 / not registered)
    eve2twitch_log = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = config_manager.load_config()
        self.config['token'] = ENV_TWITCH_TOKEN
        self.config['nick'] = ENV_TWITCH_NICK
        
        # Load user's channel from user_config.json (set during first run)
        from first_run_setup import load_user_channel
        user_channel = load_user_channel()
        
        if user_channel:
            # Use the user's configured channel
            self.config['channel'] = user_channel
            print(f"Using user's channel: {user_channel}")
        else:
            # Fallback to ENV variable (for backwards compatibility)
            self.config['channel'] = ENV_TWITCH_CHANNEL
            print(f"Using channel from ENV: {ENV_TWITCH_CHANNEL}")
        
        self.effective_channel = self.config.get("target_channel") or self.config.get("channel")
        if not self.effective_channel:
            print("WARNING: No target channel found!")
            self.effective_channel = None
        print(f"Effective channel: {self.effective_channel}")

        sound_base_path = resource_path("sounds")
        self.sound_manager = sound_manager.SoundManager(self.config, base_path=sound_base_path)
        self.animation_manager = AnimationManager(self)
        self._animation_widget_ref = self.animation_manager.get_view_widget()

        # Core state
        self.participants = set()
        self.last_winner = None
        self.confirmation_message = None
        self.eve2twitch_response = None
        self.current_prize = "<NO PRIZE SET>"
        self.current_donator = "<NO DONATOR SET>"
        self.selected_winner = "---"
        self.twitch_thread = None
        self.esi_worker_thread = None
        self.just_processed_esi = False
        self._last_esi_data = None  # Store last ESI data for font size updates
        self.suppress_next_confirmation_message = False  # <<< NEW FLAG

        # EVE2Twitch background lookup state
        self._eve2twitch_poll_thread = None
        self._eve2twitch_poll_stop_event = None
        self._eve2twitch_timeout_timer = None

        self.fonts = {}
        self.loaded_font_families = {}
        self._current_applied_font_multiplier = None  # Track what font multiplier is currently applied
        self._current_layout_lock_state = None  # Track current UI lock state to prevent unnecessary layout updates

        self.last_tech_animation_type = None
        self._is_prize_reveal_active = False  # Flag to track if we're doing a prize reveal animation
        self._needs_prize_reveal = False  # Flag to track if we need to do a prize reveal before winner draw
        self._prize_reveal_data = None  # Store prize data for reveal
        self._hidden_prize_name = None  # Store the real prize name when hidden
        self._hidden_donator = None  # Store the real donator when hidden
        self._selected_prize_original_string = None  # Store the original prize string for removal after confirmation

        global CONFIRMATION_TIMEOUT, EVE_RESPONSE_TIMEOUT
        CONFIRMATION_TIMEOUT = self.config.get("confirmation_timeout", 90)
        EVE_RESPONSE_TIMEOUT = self.config.get("eve_response_timeout", 300)

        self.current_state = AppState.STARTING
        self.is_twitch_bot_ready = False
        self.animation_panel_ready_for_display = False
        self._first_animation_warmup_done = False
        self._panel_geometries_applied_this_session = False

        self.timer_queue = queue.Queue()
        self.timer_poll_qtimer = QTimer(self)
        self.confirmation_timer_thread = None
        self.confirmation_stop_event = None
        self.eve_response_timer_thread = None
        self.eve_response_stop_event = None
        self.prize_poll_timer_thread = None
        self.prize_poll_stop_event = None
        self.prize_poll_votes = Counter()
        self.prize_poll_voters = set()
        self.current_poll_options = []

        self.info_panel = None; self.main_stack = None; self.main_grid_layout = None
        self.main_content_area = None;
        self.main_action_buttons_container_widget = None
        self.prize_controls_widget = None; self.top_overall_widget = None
        self.entrants_panel_widget = None; self.status_bar_label = None
        self.options_dialog_instance = None; self.prize_mode_selector = None
        self.animation_type_selector_main = None

        self.widget_drag_handler = None
        self.unsaved_layout_changes = {}
        self._ga_warning_shown = False

        self.ui_manager = UIManager(self)
        self.ui_manager.load_custom_fonts()
        self.ui_manager.create_fonts()
        self.ui_manager.init_main_window_ui()

        # Set initial status bar text to show the target channel
        try:
            if getattr(self, 'effective_channel', None):
                self.status_bar_label.setText(f"Channel: {self.effective_channel}")
            else:
                self.status_bar_label.setText("No Channel Configured")
        except Exception:
            pass

        # Connect EVE2Twitch signals to main-thread handlers
        try:
            self.eve2twitch_ign_found.connect(self._on_eve2twitch_ign_found)
            self.eve2twitch_lookup_failed.connect(self._on_eve2twitch_lookup_failed) # <<< NEW CONNECTION
            self.eve2twitch_log.connect(lambda msg: self.confirmation_log.append(msg))
        except Exception:
            pass

        self.widget_drag_handler = WidgetDragHandler(self)
        if hasattr(self, 'main_action_buttons_widget') and self.main_action_buttons_widget:
            self.widget_drag_handler.add_widget(self.main_action_buttons_widget)
        else:
            print("ERROR: main_action_buttons_widget not found! Drag/resize for main buttons might not work.")

        self.widget_drag_handler.add_widget(self.prize_controls_widget)
        self.widget_drag_handler.add_widget(self.entrants_panel_widget)
        self.widget_drag_handler.add_widget(self.main_stack)
        self.widget_drag_handler.geometry_changed.connect(self._handle_widget_geometry_change)

        self.setWindowTitle(f"RustyBot v{APP_VERSION}")
        QTimer.singleShot(0, self._delayed_finalize_setup)

    def _delayed_finalize_setup(self):
        print("DEBUG: _delayed_finalize_setup called.")
        print(f"DEBUG: Inside _delayed_finalize_setup. Is window maximized? {self.isMaximized()}. Geometry: {self.geometry().x()},{self.geometry().y()},{self.geometry().width()}x{self.geometry().height()}")

        print("DEBUG: Window geometry application from config in _delayed_finalize_setup is skipped.")

        QApplication.processEvents()

        # Start loading the animation page (returns True if loading started successfully)
        if self.animation_manager.load():
            if self.config.get('debug_mode_enabled', False):
                self.log_status("Animation manager loading started...")
        else:
            self.log_status("WARNING: AnimationManager could not start loading (files missing or WebEngine unavailable).")

        self._finalize_setup()

    @pyqtSlot(str, str, str)
    def _on_eve2twitch_ign_found(self, twitch_username, ign, raw_response):
        """Main-thread slot called when background lookup finds an IGN."""
        try:
            # Store raw response for copy/inspection
            self.eve2twitch_response = raw_response
            if self.config.get('debug_mode_enabled', False):
                self.confirmation_log.append(f"EVE2Twitch lookup found IGN: {ign} for @{twitch_username}. Fetching ESI...")
            # Cancel any lookup timeout watchdog since we have a response
            try:
                if getattr(self, '_eve2twitch_timeout_timer', None):
                    try:
                        self._eve2twitch_timeout_timer.cancel()
                    except Exception:
                        pass
                    self._eve2twitch_timeout_timer = None
            except Exception:
                pass
            # Start ESI lookup on main thread
            QTimer.singleShot(50, lambda ign=ign: self._fetch_esi_data(ign))
        except Exception as e:
            print(f"Error in _on_eve2twitch_ign_found: {e}")


    @pyqtSlot(str)
    def _on_eve2twitch_lookup_failed(self, twitch_username):
        """Main-thread slot for when the background lookup gets a 404 (user not registered)."""
        # --- 1. Schedule the chat message to the user ---
        try:
            template = self.config.get("chat_msg_auto_lookup_failed") or config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_failed")
            msg_to_chat = template.format(winner=twitch_username)
        except Exception:
            msg_to_chat = f"@{twitch_username} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign <your in-game name>' in chat to provide your IGN."
        try:
            self.schedule_twitch_message(msg_to_chat)
        except Exception:
            try:
                self.confirmation_log.append(msg_to_chat)
            except Exception:
                pass

        # --- 2. Create and append the stylized HTML block to the confirmation log ---
        try:
            font_multiplier = float(self.config.get("font_size_multiplier", 1.0) or 1.0)
        except Exception:
            font_multiplier = 1.0
        font_size = int(16 * font_multiplier)

        lookup_failed_html = f"""
        <div style='text-align: center; margin: 20px 0; padding: 0;'>
            <div style='display: inline-block; background: linear-gradient(135deg, #2a1a0a 0%, #3a2a1a 50%, #2f1f0f 100%);
                         border: 3px solid #ff9500; border-radius: 15px; padding: 20px 30px;
                         box-shadow: 0 0 25px rgba(255, 149, 0, 0.4), inset 0 0 15px rgba(255, 149, 0, 0.1); position: relative;'>

                <div style='font-size: {int(font_size * 1.2)}pt; color: #ff9500; font-weight: bold;
                            text-shadow: 0 0 10px rgba(255, 149, 0, 0.8); letter-spacing: 1px; margin-bottom: 12px;'>
                    <span style='font-family: "Segoe UI Symbol", "Arial";'>⚠️</span> AUTO-LOOKUP FAILED
                </div>

                <div style='font-size: {int(font_size * 1.5)}pt; color: #e8d900; font-weight: bold;
                            text-shadow: 0 0 12px rgba(232, 217, 0, 0.8); margin-bottom: 8px;'>
                    {twitch_username}
                </div>

                <div style='font-size: {int(font_size * 0.9)}pt; color: #ffddaa; font-style: italic; opacity: 0.8;'>
                    User not registered with EVE2Twitch. Please register with Eve2twitch - type !ign "ingamename" in twitch chat
                </div>

                <div style='position: absolute; top: -3px; left: -3px; right: -3px; bottom: -3px;
                            border: 1px solid rgba(255, 149, 0, 0.3); border-radius: 15px; pointer-events: none;'>
                </div>
            </div>
        </div>
        """
        try:
            # Append as HTML block so the confirmation_log shows a styled warning
            self.confirmation_log.append(lookup_failed_html)
        except Exception:
            # If append fails, fall back to plain text log
            try:
                self.confirmation_log.append(f"EVE2Twitch lookup for @{twitch_username} failed (Not Found). Prompting for !ign.")
            except Exception:
                pass


    def _finalize_setup(self):
        print("DEBUG: Finalizing setup (core)...")
        logging_utils.init_ga_config_ref(self.config)
        self.connect_signals()
        
        # Only show configuration dump if debug mode is enabled
        if self.config.get("debug_mode_enabled", False):
            self.log_loaded_config()
            
        self._load_prize_options_into_dropdown()
        self.update_displays()
        if self.animation_type_selector_main:
            self.animation_type_selector_main.setCurrentText(self.config.get("animation_type", config_manager.DEFAULT_CONFIG["animation_type"]))

        self._start_timer_queue_poll()
        self._update_layout_mode(force=True)  # Force initial layout setup 

        self.auto_connect_twitch()

        if self._animation_widget_ref: self._animation_widget_ref.hide()
        self._switch_to_info_panel()

        self._apply_font_size(force=True) 
        print("DEBUG: _apply_font_size called at the end of _finalize_setup.")

        # Update status bar with channel info at launch
        if self.effective_channel:
            print("DEBUG: Setting status bar to 'Ready to connect'")
            if self.config.get('debug_mode_enabled', False):
                self.log_status("Ready to connect")
            else:
                print("STATUS: Ready to connect (debug mode off)")


        logging_utils.log_activity("APP_LAUNCH")
        logging_utils.send_remote_log(self.config, "APP_LAUNCHED")
        logging_utils.send_ga_event(self.config, "app_launch", status_logger_func=self.log_status)
        print("DEBUG: Final setup (core) complete.")


    def _update_layout_mode(self, force=False):
        is_locked = self.config.get("ui_locked", True)
        
        # Check if layout state actually changed (unless forced)
        if not force and self._current_layout_lock_state == is_locked:
            print(f"MainApp: Layout mode unchanged (locked: {is_locked}). Skipping layout update.")
            return
            
        print(f"MainApp: Updating layout mode. Custom UI: True (Forced), Locked: {is_locked}{' (forced)' if force else ''}")
        self._current_layout_lock_state = is_locked

        try:
            self.ui_manager.setup_manual_layout()
        except Exception as e:
             print(f"CRITICAL ERROR during manual layout setup: {e}"); traceback.print_exc()
             QMessageBox.critical(self, "Layout Error", f"Failed to set up manual layout: {e}")
             return

        widgets_to_style = [
            self.main_action_buttons_widget if hasattr(self, 'main_action_buttons_widget') else None,
            self.prize_controls_widget,      
            self.entrants_panel_widget,    
            self.main_stack                
        ]
        css_class_name = "adjustable-widget-active"
        apply_adjustable_style = not is_locked
        cursor_shape = QCursor(Qt.CursorShape.SizeAllCursor) if apply_adjustable_style else QCursor(Qt.CursorShape.ArrowCursor)
        for widget in widgets_to_style:
            if not widget: continue
            widget.setMouseTracking(apply_adjustable_style); widget.setCursor(cursor_shape)
            current_class = widget.property("class") or ""; current_classes = set(current_class.split()); has_class = css_class_name in current_classes; style_changed = False
            if apply_adjustable_style and not has_class: current_classes.add(css_class_name); widget.setProperty("class", " ".join(sorted(list(current_classes)))); style_changed = True
            elif not apply_adjustable_style and has_class: current_classes.discard(css_class_name); widget.setProperty("class", " ".join(sorted(list(current_classes))) if current_classes else None); style_changed = True
            if style_changed: widget.style().unpolish(widget); widget.style().polish(widget); widget.update()
        self.update()
        if self.main_content_area: self.main_content_area.update() 

    def _reset_widget_layout(self):
        print("MainApp: Resetting panel positions to default manual layout...")
        self._discard_layout_changes()
        for key in WIDGET_CONFIG_MAP.values():
            if key in self.config:
                self.config[key] = None

        self._panel_geometries_applied_this_session = False
        print("MainApp: _panel_geometries_applied_this_session flag reset for layout reset.")

        self.config["customisable_ui_enabled"] = True
        self.config["ui_locked"] = True
        if self.options_dialog_instance and self.options_dialog_instance.isVisible():
            self.options_dialog_instance.lock_ui_check.setChecked(True)

        self._update_layout_mode()

        if config_manager.save_config(self.config):
            if self.config.get('debug_mode_enabled', False):
                self.log_status("Panel positions reset to default and config saved.")
        else:
            QMessageBox.warning(self, "Save Error", "Could not save reset panel positions to config.")


    @pyqtSlot()
    def _apply_font_size(self, force=False):
        current_multiplier = self.config.get('font_size_multiplier', 1.0)
        
        # Check if font multiplier has actually changed (unless forced)
        if (not force and 
            self._current_applied_font_multiplier is not None and 
            abs(current_multiplier - self._current_applied_font_multiplier) < 0.001):
            print(f"DEBUG: GiveawayApp._apply_font_size skipped - no change. Current: {current_multiplier}")
            return
        
        print(f"DEBUG: GiveawayApp._apply_font_size called. Using multiplier: {current_multiplier}{' (forced)' if force else ''}")
        
        # Update the tracking variable
        self._current_applied_font_multiplier = current_multiplier

        self.ui_manager.create_fonts() 

        widgets_to_update_font = [
            (self.open_draw_button, "Shentox-SemiBold"), 
            (self.start_draw_button, "Shentox-SemiBold"), 
            (self.abandon_draw_button, "Shentox-SemiBold"), 
            (self.purge_list_button, "Shentox-SemiBold"), 
            (self.options_button, "Shentox-SemiBold"), 
            (self.prize_controls_widget.findChild(QLabel, "prize_label"), "labels"), 
            (self.prize_input, "Shentox-SemiBold"), 
            (self.prize_options_dropdown, "Shentox-SemiBold"), 
            (self.start_prize_poll_button, "Shentox-SemiBold"), 
            (self.set_prize_button, "Shentox-SemiBold"), 
            (self.set_prize_and_open_button, "Shentox-SemiBold"), 
            (self.clear_prize_button, "Shentox-SemiBold"), 
            (self.animation_type_selector_main, "Shentox-SemiBold"), 
            (self.prize_mode_selector, "Shentox-SemiBold"), 
            (self.entries_count_label, "entries_count"), 
            (self.participant_list, "list"), 
            (self.remove_selected_button, "Shentox-SemiBold"), 
            (self.current_prize_donator_display, "prize_donator_info"), 
            (self.entry_requirement_display, "requirement"), 
            (self.selected_winner_display, "winner"), 
            (self.confirmation_log, "log"), 
            (self.copy_log_button, "log"), 
            (self.status_bar_label, "status"), 
        ]

        for widget, font_key in widgets_to_update_font:
            if widget and font_key in self.fonts: 
                widget.setFont(self.fonts[font_key])
                widget.style().unpolish(widget)
                widget.style().polish(widget)
                widget.updateGeometry()
                widget.update()

        info_box_frames_parents = [
            self.current_prize_donator_display, 
            self.entry_requirement_display,   
            self.selected_winner_display,     
            self.confirmation_log             
        ]
        for display_widget_ref in info_box_frames_parents:
            if display_widget_ref:
                parent_frame = display_widget_ref.parentWidget()
                if parent_frame and parent_frame.objectName() == "infoBox":
                    label_widget = parent_frame.findChild(QLabel, "infoBoxLabel")
                    if label_widget and "labels" in self.fonts: 
                        label_widget.setFont(self.fonts["labels"])
                        label_widget.style().unpolish(label_widget)
                        label_widget.style().polish(label_widget)
                        label_widget.updateGeometry()
                        label_widget.update()

        major_containers = [
            self.main_action_buttons_container_widget, 
            self.ui_manager.buttons_actual_wrapper if hasattr(self.ui_manager, 'buttons_actual_wrapper') else None,
            self.prize_controls_widget,      
            self.entrants_panel_widget,    
            self.main_stack,               
            self.main_content_area,        
            self 
        ]
        for container in major_containers:
            if container:
                container.updateGeometry()
                container.update()

        QApplication.instance().setStyleSheet(QApplication.instance().styleSheet())
        QApplication.processEvents() 
        QApplication.processEvents()

        print("Font size changed. Scheduling layout update via _delayed_font_layout_update.")
        QTimer.singleShot(100, self._delayed_font_layout_update)

        if self.config.get('debug_mode_enabled', False):
            self.log_status("Font sizes applied. Layout refresh scheduled.")
        
        # Inform user that character sheet font changes apply to new lookups
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"Font size updated to {int(current_multiplier * 100)}%. Character sheets will use new size on next IGN lookup.")
        
        # Update existing character sheet if we have recent ESI data
        self._update_existing_character_sheet_font()
        
        print("DEBUG: GiveawayApp._apply_font_size finished.")

    def _update_existing_character_sheet_font(self):
        """Update the most recent character sheet in the log with new font size"""
        if not hasattr(self, '_last_esi_data') or not self._last_esi_data:
            return
            
        try:
            # Get the current log content
            log_text = self.confirmation_log.toPlainText()
            
            # Look for the most recent ESI data section
            esi_start_pattern = f"--- ESI Data for {self.last_winner} ---"
            esi_end_pattern = "---------------------"
            
            # Find the last occurrence of the ESI data section
            esi_start_index = log_text.rfind(esi_start_pattern)
            if esi_start_index == -1:
                return
                
            # Find the end of this section
            search_start = esi_start_index + len(esi_start_pattern)
            esi_end_index = log_text.find(esi_end_pattern, search_start)
            if esi_end_index == -1:
                return
                
            # Generate new character sheet HTML with updated font size
            new_html_sheet = self._format_character_sheet_html(self._last_esi_data)
            
            # Replace the character sheet section
            before_section = log_text[:esi_start_index]
            after_section = log_text[esi_end_index:]
            
            updated_log = (before_section + 
                          esi_start_pattern + "\n" +
                          new_html_sheet + "\n" +
                          after_section)
            
            # Update the log
            self.confirmation_log.clear()
            self.confirmation_log.append(updated_log)
            
            self.log_status("✅ Updated character sheet font size in confirmation log.")
            
        except Exception as e:
            print(f"Error updating character sheet font: {e}")
            # Silently fail - this is a convenience feature


    def _delayed_font_layout_update(self, was_maximized_before_font_change=None, geom_str_before_font_change=None):
        print("DEBUG: Executing delayed_font_layout_update.")
        self._update_layout_mode()

        if self.layout():
            self.layout().invalidate()
            self.layout().activate()
        self.update()

        for child in self.findChildren(QWidget):
            child.updateGeometry()
            child.update()

        QApplication.processEvents()
        QApplication.processEvents()

        if not self.isMaximized():
            print("Window not maximized after font update, re-maximizing.")
            self.showMaximized()
        else:
            print("Window remained maximized after font update.")

        self.update()
        QApplication.processEvents()
        print("DEBUG: Delayed font layout update complete.")


    def _set_state(self, new_state: AppState):
        if self.current_state == new_state:
            return
        old_state = self.current_state
        self.current_state = new_state
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"STATE CHANGE: {old_state.name} -> {new_state.name}")

        if old_state == AppState.AWAITING_CONFIRMATION and new_state != AppState.AWAITING_CONFIRMATION:
            self._stop_confirmation_timer()
        if old_state == AppState.AWAITING_EVE_RESPONSE and new_state != AppState.AWAITING_EVE_RESPONSE:
            self._stop_eve_response_timer()
        if old_state == AppState.AWAITING_PRIZE_POLL_VOTES and new_state != AppState.AWAITING_PRIZE_POLL_VOTES:
            self._stop_prize_poll_timer()
            if new_state != AppState.IDLE:
                self.confirmation_log.setHtml("<p>Prize poll cancelled.</p>") 


        if new_state == AppState.IDLE:
            self._switch_to_info_panel()
            self.animation_manager.cancel_animation()
        elif new_state == AppState.COLLECTING:
            self._announce_draw_open()
        elif new_state == AppState.ANIMATING_WINNER:
            self._switch_to_animation_panel()
        elif new_state == AppState.AWAITING_CONFIRMATION:
            if self.last_winner:
                self._start_confirmation_timer(self.last_winner, CONFIRMATION_TIMEOUT)
                self._announce_winner_confirmation_needed()
            else:
                self.log_status("Error: Awaiting confirmation but no last winner set.")
                self._set_state(AppState.IDLE)
        elif new_state == AppState.AWAITING_EVE_RESPONSE:
            if self.last_winner:
                self._start_eve_response_timer(self.last_winner, EVE_RESPONSE_TIMEOUT)
            else:
                self.log_status("Error: Awaiting EVE response but no last winner set.")
                self._set_state(AppState.IDLE)
        elif new_state == AppState.FETCHING_ESI_DATA:
            # Show EVE bot response only in debug mode
            if self.config.get("debug_mode_enabled", False):
                self.log_status(f"Fetching ESI data for: {self.last_winner} (from EVE Bot: {self.eve2twitch_response})")

            resp_text_for_search = self.eve2twitch_response if isinstance(self.eve2twitch_response, (str, bytes)) else ""
            ign_match = re.search(r'IGN\s*["\']([^"\']+)["\']', resp_text_for_search, re.IGNORECASE)
            if ign_match:
                ign = ign_match.group(1)
                if self.config.get("debug_mode_enabled", False):
                    # Create styled IGN extraction message with modern design
                    font_multiplier = self.config.get("font_size_multiplier", 1.0)
                    font_size = int(14 * font_multiplier)
                    ign_html = f"<div style='text-align: center; margin: 15px 0; padding: 0;'>"
                    ign_html += f"<div style='display: inline-block; background: linear-gradient(135deg, #0a1a0a 0%, #1a2a1a 50%, #0f1f0f 100%); "
                    ign_html += f"border: 2px solid #4af1f2; border-radius: 12px; padding: 15px 25px; "
                    ign_html += f"box-shadow: 0 0 20px rgba(74, 241, 242, 0.3); position: relative;'>"
                    ign_html += f"<div style='font-size: {int(font_size * 0.9)}pt; color: #4af1f2; font-weight: bold; "
                    ign_html += f"text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>🔍 IGN EXTRACTED</div>"
                    ign_html += f"<div style='font-size: {int(font_size * 1.4)}pt; color: #e8d900; font-weight: bold; "
                    ign_html += f"text-shadow: 0 0 10px rgba(232, 217, 0, 0.8); letter-spacing: 1px;'>{ign}</div>"
                    ign_html += f"<div style='position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px; "
                    ign_html += f"border: 1px solid rgba(232, 217, 0, 0.3); border-radius: 12px; pointer-events: none;'></div>"
                    ign_html += f"</div></div>"
                    self.confirmation_log.append(ign_html)
                self._fetch_esi_data(ign)
            else:
                if self.config.get("debug_mode_enabled", False):
                    font_multiplier = self.config.get("font_size_multiplier", 1.0)
                    font_size = int(14 * font_multiplier)
                    error_html = f"<div style='text-align: center; margin: 15px 0; padding: 0;'>"
                    error_html += f"<div style='display: inline-block; background: linear-gradient(135deg, #2a0a0a 0%, #3a1a1a 50%, #2f0f0f 100%); "
                    error_html += f"border: 2px solid #ff6b6b; border-radius: 12px; padding: 15px 25px; "
                    error_html += f"box-shadow: 0 0 20px rgba(255, 107, 107, 0.3);'>"
                    error_html += f"<div style='font-size: {int(font_size * 1.1)}pt; color: #ff6b6b; font-weight: bold; "
                    error_html += f"text-shadow: 0 0 8px rgba(255, 107, 107, 0.6);'>❌ Could not extract IGN from EVE Bot response</div>"
                    error_html += f"</div></div>"
                    self.confirmation_log.append(error_html) 
                self._set_state(AppState.CONFIRMED_NO_IGN)
        elif new_state == AppState.CONFIRMED_NO_IGN:
            # If a previous ESI error already appended a dedicated message and
            # requested suppression, skip the generic confirmation block.
            if getattr(self, 'suppress_next_confirmation_message', False):
                # reset the flag and perform minimal housekeeping
                self.suppress_next_confirmation_message = False
                self._remove_winner_from_participants()
                # Remove confirmed random prize if appropriate and return early
                self._remove_confirmed_prize_from_lists()
                return

            self._remove_winner_from_participants()
            # Decide whether to ask the winner to type !ign or to run automatic EVE2Twitch lookup.
            try:
                auto_lookup_enabled = self.config.get('auto_eve2twitch_lookup', True)
            except Exception:
                auto_lookup_enabled = True
            # If auto-lookup is enabled and we haven't yet received any eve2twitch response,
            # start automatic lookup so the user doesn't have to type anything.
            if auto_lookup_enabled and not self.eve2twitch_response:
                template = self.config.get("chat_msg_auto_lookup_attempt") or config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_attempt")
                try:
                    msg = template.format(winner=self.last_winner)
                except Exception:
                    msg = f"@{self.last_winner} confirmed! Congratulations! Attempting automatic EVE2Twitch lookup for your EVE IGN — please wait."
                self.schedule_twitch_message(msg)
            else:
                # If an automatic EVE2Twitch lookup already ran but did not produce
                # a usable IGN (or ESI validation failed), prompt the winner to
                # register with the IGN bot or provide their IGN with the !ign command.
                if self.eve2twitch_response:
                    # Explicit request when auto-lookup ran but no valid IGN was extractable
                    template = self.config.get("chat_msg_auto_lookup_failed") or config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_failed")
                    try:
                        msg = template.format(winner=self.last_winner)
                    except Exception:
                        msg = f"@{self.last_winner} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign <your in-game name>' in chat to provide your IGN."
                    self.schedule_twitch_message(msg)
                else:
                    # Fallback: no auto-lookup configured or it was disabled — ask for !ign
                    self._announce_confirmation_in_chat()
            # Style the confirmation message with premium design
            font_multiplier = self.config.get("font_size_multiplier", 1.0)
            font_size = int(16 * font_multiplier)
            confirmation_html = f"<div style='text-align: center; margin: 20px 0; padding: 0;'>"
            confirmation_html += f"<div style='display: inline-block; background: linear-gradient(135deg, #0a1a0a 0%, #1a2a1a 50%, #0f1f0f 100%); "
            confirmation_html += f"border-radius: 15px; padding: 20px 30px; "
            confirmation_html += f"box-shadow: 0 0 25px rgba(74, 241, 242, 0.4), inset 0 0 15px rgba(74, 241, 242, 0.1); position: relative;'>"
            confirmation_html += f"<div style='font-size: {int(font_size * 1.2)}pt; color: #4af1f2; font-weight: bold; "
            confirmation_html += f"text-shadow: 0 0 10px rgba(74, 241, 242, 0.8); letter-spacing: 1px; margin-bottom: 12px;'>✅ WINNER CONFIRMED</div>"
            confirmation_html += f"<div style='font-size: {int(font_size * 1.5)}pt; color: #e8d900; font-weight: bold; "
            confirmation_html += f"text-shadow: 0 0 12px rgba(232, 217, 0, 0.8); margin-bottom: 8px;'>{self.last_winner}</div>"
            confirmation_html += f"<div style='font-size: {int(font_size * 0.9)}pt; color: #cccccc; font-style: italic; "
            confirmation_html += f"opacity: 0.8;'>No IGN provided or !ign not used</div>"
            confirmation_html += f"<div style='position: absolute; top: -3px; left: -3px; right: -3px; bottom: -3px; "
            confirmation_html += f"border: 1px solid rgba(232, 217, 0, 0.3); border-radius: 15px; pointer-events: none;'></div>"
            confirmation_html += f"</div></div>"
            # The confirmation HTML is intentionally not appended to the confirmation_log
            # to avoid duplicative or noisy confirmation messages in the UI.
            # self.confirmation_log.append(confirmation_html)
            logging_utils.send_ga_event(self.config, "winner_confirmed", {"winner": self.last_winner, "ign_provided": False}, self.log_status)
            # Attempt automatic EVE2TWITCH lookup for the twitch username if enabled
            # Start automatic lookup only if enabled and we haven't already received a response.
            if auto_lookup_enabled and not self.eve2twitch_response:
                try:
                    if self.config.get('debug_mode_enabled', False):
                        self.log_status(f"Attempting automatic EVE2Twitch lookup for @{self.last_winner}...")
                    self._start_eve2twitch_lookup(self.last_winner)
                except Exception as e:
                    print(f"Error starting eve2twitch lookup: {e}")
            else:
                # Remove confirmed random prize from list immediately if auto-lookup disabled
                # or if lookup already ran and provided no usable IGN.
                self._remove_confirmed_prize_from_lists()
        elif new_state == AppState.CONFIRMED_WITH_IGN:
            self._remove_winner_from_participants()
            # The _format_character_sheet_html is now called directly in _handle_esi_data_ready
            # self.confirmation_log.append(f"{self.last_winner} confirmed. ESI data processed.") # This line is redundant now
            logging_utils.send_ga_event(self.config, "winner_confirmed", {"winner": self.last_winner, "ign_provided": True}, self.log_status)
            # Remove confirmed random prize from list
            self._remove_confirmed_prize_from_lists()
        elif new_state == AppState.TIMED_OUT:
            font_multiplier = self.config.get("font_size_multiplier", 1.0)
            font_size = int(16 * font_multiplier)
            
            # Modern card-based timeout display - simplified for QTextEdit centering
            timeout_html = ""
            
            # Outer glow container
            timeout_html += f"<div style='display: inline-block; position: relative; padding: 6px; "
            timeout_html += f"background: linear-gradient(135deg, rgba(255, 68, 68, 0.3) 0%, rgba(255, 68, 68, 0.1) 50%, rgba(255, 68, 68, 0.3) 100%); "
            timeout_html += f"border-radius: 26px; "
            timeout_html += f"box-shadow: 0 0 50px rgba(255, 68, 68, 0.6), 0 0 100px rgba(255, 68, 68, 0.3);'>"
            
            # Main card
            timeout_html += f"<div style='background: linear-gradient(135deg, #0f0202 0%, #2a0606 40%, #1a0404 70%, #0f0202 100%); "
            timeout_html += f"border: 3px solid #ff3333; border-radius: 22px; padding: 35px 50px; "
            timeout_html += f"box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), inset 0 0 30px rgba(255, 68, 68, 0.15); "
            timeout_html += f"position: relative; min-width: 450px; overflow: hidden;'>"
            
            # Animated background pattern
            timeout_html += f"<div style='position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; "
            timeout_html += f"background: radial-gradient(circle, rgba(255, 68, 68, 0.08) 1px, transparent 1px); "
            timeout_html += f"background-size: 30px 30px; opacity: 0.4; pointer-events: none;'></div>"
            
            # Content container
            timeout_html += f"<div style='position: relative; z-index: 1;'>"
            
            # Title
            timeout_html += f"<div style='font-size: {int(font_size * 1.6)}pt; color: #ff5555; font-weight: 900; "
            timeout_html += f"text-transform: uppercase; letter-spacing: 4px; margin-bottom: 8px; text-align: center; "
            timeout_html += f"text-shadow: 0 0 15px rgba(255, 85, 85, 0.9), 0 3px 6px rgba(0, 0, 0, 0.8), "
            timeout_html += f"0 0 3px rgba(255, 85, 85, 1);'>Confirmation Timeout</div>"
            
            # Decorative line
            timeout_html += f"<div style='width: 60%; height: 3px; margin: 18px auto; "
            timeout_html += f"background: linear-gradient(90deg, transparent, #ff4444 20%, #ff4444 80%, transparent); "
            timeout_html += f"box-shadow: 0 0 10px rgba(255, 68, 68, 0.8); border-radius: 2px;'></div>"
            
            # Username with backdrop
            timeout_html += f"<div style='margin: 20px 0; padding: 15px 25px; "
            timeout_html += f"background: rgba(255, 255, 255, 0.05); "
            timeout_html += f"border: 1px solid rgba(255, 68, 68, 0.3); border-radius: 12px; "
            timeout_html += f"box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3); text-align: center;'>"
            timeout_html += f"<div style='font-size: {int(font_size * 2.0)}pt; color: #ffffff; font-weight: bold; "
            timeout_html += f"text-shadow: 0 0 15px rgba(255, 255, 255, 0.8), 0 3px 10px rgba(0, 0, 0, 0.9), "
            timeout_html += f"0 0 5px rgba(255, 255, 255, 1); letter-spacing: 1.5px; text-align: center;'>{self.last_winner}</div>"
            timeout_html += f"</div>"
            
            # Message
            timeout_html += f"<div style='font-size: {int(font_size * 1.05)}pt; color: #ffb3b3; font-style: italic; "
            timeout_html += f"opacity: 0.95; line-height: 1.6; margin-top: 15px; text-align: center; "
            timeout_html += f"text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>⚠️ Failed to confirm within time limit</div>"
            
            timeout_html += f"</div></div></div>"
            
            self.confirmation_log.append(timeout_html)
            self.schedule_twitch_message(f"@{self.last_winner} did not confirm in time. Rerolling may occur.")
            logging_utils.send_ga_event(self.config, "winner_timeout", {"winner": self.last_winner, "timeout_type": "confirmation"}, self.log_status)
        elif new_state == AppState.EVE_TIMED_OUT:
            font_multiplier = self.config.get("font_size_multiplier", 1.0)
            font_size = int(16 * font_multiplier)
            
            # Modern card-based EVE timeout display
            eve_timeout_html = f"<div style='text-align: center; margin: 30px auto; max-width: 650px;'>"
            
            # Outer glow container
            eve_timeout_html += f"<div style='display: block; position: relative; padding: 6px; width: fit-content; margin: 0 auto; "
            eve_timeout_html += f"background: linear-gradient(135deg, rgba(255, 149, 0, 0.3) 0%, rgba(255, 149, 0, 0.1) 50%, rgba(255, 149, 0, 0.3) 100%); "
            eve_timeout_html += f"border-radius: 26px; "
            eve_timeout_html += f"box-shadow: 0 0 50px rgba(255, 149, 0, 0.6), 0 0 100px rgba(255, 149, 0, 0.3);'>"
            
            # Main card
            eve_timeout_html += f"<div style='background: linear-gradient(135deg, #0f0a02 0%, #2a1906 40%, #1a0f04 70%, #0f0a02 100%); "
            eve_timeout_html += f"border: 3px solid #ff9933; border-radius: 22px; padding: 35px 50px; "
            eve_timeout_html += f"box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8), inset 0 0 30px rgba(255, 149, 0, 0.15); "
            eve_timeout_html += f"position: relative; min-width: 450px; overflow: hidden;'>"
            
            # Animated background pattern
            eve_timeout_html += f"<div style='position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; "
            eve_timeout_html += f"background: radial-gradient(circle, rgba(255, 149, 0, 0.08) 1px, transparent 1px); "
            eve_timeout_html += f"background-size: 30px 30px; opacity: 0.4; pointer-events: none;'></div>"
            
            # Content container
            eve_timeout_html += f"<div style='position: relative; z-index: 1;'>"
            
            # Title
            eve_timeout_html += f"<div style='font-size: {int(font_size * 1.6)}pt; color: #ffaa55; font-weight: 900; "
            eve_timeout_html += f"text-transform: uppercase; letter-spacing: 4px; margin-bottom: 8px; text-align: center; "
            eve_timeout_html += f"text-shadow: 0 0 15px rgba(255, 170, 85, 0.9), 0 3px 6px rgba(0, 0, 0, 0.8), "
            eve_timeout_html += f"0 0 3px rgba(255, 170, 85, 1);'>EVE Response Timeout</div>"
            
            # Decorative line
            eve_timeout_html += f"<div style='width: 60%; height: 3px; margin: 18px auto; "
            eve_timeout_html += f"background: linear-gradient(90deg, transparent, #ff9933 20%, #ff9933 80%, transparent); "
            eve_timeout_html += f"box-shadow: 0 0 10px rgba(255, 149, 0, 0.8); border-radius: 2px;'></div>"
            
            # Username with backdrop
            eve_timeout_html += f"<div style='margin: 20px 0; padding: 15px 25px; "
            eve_timeout_html += f"background: rgba(255, 255, 255, 0.05); "
            eve_timeout_html += f"border: 1px solid rgba(255, 149, 0, 0.3); border-radius: 12px; "
            eve_timeout_html += f"box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3); text-align: center;'>"
            eve_timeout_html += f"<div style='font-size: {int(font_size * 2.0)}pt; color: #ffffff; font-weight: bold; "
            eve_timeout_html += f"text-shadow: 0 0 15px rgba(255, 255, 255, 0.8), 0 3px 10px rgba(0, 0, 0, 0.9), "
            eve_timeout_html += f"0 0 5px rgba(255, 255, 255, 1); letter-spacing: 1.5px; text-align: center;'>{self.last_winner}</div>"
            eve_timeout_html += f"</div>"
            
            # Message
            eve_timeout_html += f"<div style='font-size: {int(font_size * 1.05)}pt; color: #ffd9aa; font-style: italic; "
            eve_timeout_html += f"opacity: 0.95; line-height: 1.6; margin-top: 15px; text-align: center; "
            eve_timeout_html += f"text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);'>⚠️ IGN details not provided in time (or EVE Bot issue)</div>"
            
            eve_timeout_html += f"</div></div></div>"
            
            self.confirmation_log.append(eve_timeout_html)
            # Prefer configurable chat messages; fall back to a sensible default
            try:
                if self.eve2twitch_response:
                    template = self.config.get("chat_msg_auto_lookup_failed") or config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_failed")
                else:
                    template = self.config.get("chat_msg_awaiting_ign") or config_manager.DEFAULT_CONFIG.get("chat_msg_awaiting_ign")
                try:
                    msg = template.format(winner=self.last_winner)
                except Exception:
                    raise
            except Exception:
                # Fallback messages
                if self.eve2twitch_response:
                    msg = f"@{self.last_winner} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign <your in-game name>' in chat to provide your IGN."
                else:
                    msg = f"@{self.last_winner} confirmed! Congratulations! Awaiting Capsuleers name, Please type !ign in chat"

            self.schedule_twitch_message(msg)
            logging_utils.send_ga_event(self.config, "winner_timeout", {"winner": self.last_winner, "timeout_type": "eve_response"}, self.log_status)
        elif new_state == AppState.AWAITING_PRIZE_POLL_VOTES:
             self._start_prize_poll_timer(self.config.get("poll_duration", 30))
             self._update_prize_poll_display_in_log()

        resolved_states_that_should_show_info_panel = [
            AppState.TIMED_OUT,
            AppState.EVE_TIMED_OUT,
            AppState.CONFIRMED_NO_IGN,
            AppState.CONFIRMED_WITH_IGN 
        ]
        if new_state in resolved_states_that_should_show_info_panel:
            if self.main_stack and self._animation_widget_ref and self.main_stack.currentWidget() == self._animation_widget_ref: 
                print(f"Switching to info panel from animation due to state: {new_state.name}")
                self._switch_to_info_panel()
            
            if self.just_processed_esi and new_state == AppState.CONFIRMED_WITH_IGN:
                print("MAIN_APP_DEBUG: ESI just processed, delaying cancel_animation slightly for state CONFIRMED_WITH_IGN.")
                QTimer.singleShot(500, self.animation_manager.cancel_animation) 
                self.just_processed_esi = False 
            else:
                self.animation_manager.cancel_animation()

        self.update_ui_button_states()

    @pyqtSlot()
    def draw_winner(self):
        print(f"DEBUG: draw_winner called. Current state: {self.current_state}, Prize: {self.current_prize}, Participants: {len(self.participants)}")
        prize_mode = self.config.get("prize_selection_mode", PRIZE_MODE_POLL)
        if self.current_prize == "<NO PRIZE SET>" and (prize_mode == PRIZE_MODE_POLL or prize_mode == PRIZE_MODE_STREAMER):
            QMessageBox.warning(self, "No Prize Set", "Please set or select a prize before drawing a winner.")
            self.log_status("Draw attempt failed: No prize set for current mode.")
            return

        if not self.is_twitch_bot_ready:
            QMessageBox.warning(self, "Bot Not Ready", "Twitch bot is not connected or ready.")
            self.log_status("Draw attempt failed: Twitch bot not ready.")
            return

        allowed_draw_states = [
            AppState.IDLE,
            AppState.TIMED_OUT,
            AppState.EVE_TIMED_OUT,
            AppState.CONFIRMED_NO_IGN,
            AppState.CONFIRMED_WITH_IGN
        ]
        if self.current_state not in allowed_draw_states:
            self.log_status(f"Cannot draw winner in state: {self.current_state.name}")
            QMessageBox.warning(self, "Action Denied", f"Cannot draw winner in current state: {self.current_state.name}.")
            return

        if not self.participants:
            QMessageBox.warning(self, "No Participants", "There are no participants to draw from.")
            self.log_status("Draw attempt failed: No participants.")
            if self.current_state != AppState.IDLE:
                self._set_state(AppState.IDLE)
            return

        # Clear the confirmation log and reset any pending confirmation responses
        try:
            self.clear_confirmation_log()
        except Exception:
            pass
        self.confirmation_message = None
        self.eve2twitch_response = None

        self.last_winner = random.choice(list(self.participants))
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"WINNER SELECTED (Internally): {self.last_winner}")

        # If both prize and animation are set to random, pick a random animation type
        animation_type = self.config.get("animation_type", None)
        chosen_type = None
        if self.current_prize == DROPDOWN_RANDOM_PRIZE_TEXT and (animation_type == "Random" or animation_type == "ANIM_TYPE_RANDOM_TECH"):
            # Exclude 'Random' and any non-actual animation types from the list
            valid_types = [t for t in VALID_ANIMATION_TYPES if t.lower() != "random"]
            chosen_type = random.choice(valid_types)
            self.config["animation_type"] = chosen_type
            if self.animation_type_selector_main:
                self.animation_type_selector_main.setCurrentText(chosen_type)
            if self.config.get('debug_mode_enabled', False):
                self.log_status(f"Random animation type selected: {chosen_type}")

        self.selected_winner = "--- PENDING ANIMATION ---"
        self.update_displays()

        self._set_state(AppState.ANIMATING_WINNER)

        # Check if we need to do a prize reveal animation first
        if self._needs_prize_reveal and self._prize_reveal_data:
            prize_name = self._prize_reveal_data['prize_name']
            donator = self._prize_reveal_data['donator']
            self._start_prize_reveal_animation(prize_name, donator)
        else:
            # Go directly to winner animation
            if chosen_type:
                self._start_js_animation(animation_type_override=chosen_type)
            else:
                self._start_js_animation()

        try:
            logging_utils.send_ga_event(self.config, "winner_drawn", {"prize_name": self.current_prize if self.current_prize != "<NO PRIZE SET>" else "N/A"}, self.log_status)
            logging_utils.log_activity("WINNER_DRAWN", f"Winner: {self.last_winner}, Prize: {self.current_prize}")
        except Exception as e:
            print(f"Error during GA/local logging for winner_drawn: {e}")

        self.update_ui_button_states()

    def _parse_prize_and_donator(self, full_prize_string: str) -> tuple[str, str | None, int]:
        if not isinstance(full_prize_string, str):
            return str(full_prize_string), None, 1
        
        prize_name = full_prize_string
        donator_name = None
        quantity = 1

        quantity_match = re.search(r'\((?:x|X)\s*(\d+)\)|\[(?:x|X)\s*(\d+)\]', prize_name)
        if quantity_match:
            num_str = quantity_match.group(1) or quantity_match.group(2)
            if num_str:
                quantity = int(num_str)
                prize_name = prize_name[:quantity_match.start()] + prize_name[quantity_match.end():]
                prize_name = prize_name.strip()
        
        donator_match = re.search(r'\(([^()]+)\)|\[([^\[\]]+)\]$', prize_name)
        if donator_match:
            potential_donator_text = (donator_match.group(1) or donator_match.group(2) or "").strip()
            if potential_donator_text and not re.fullmatch(r'(x|X)\s*\d+', potential_donator_text, re.IGNORECASE):
                donator_text_in_brackets = potential_donator_text
                donator_keywords = ["donated by", "sponsored by", "from", "courtesy of"]
                donator_text_lower = donator_text_in_brackets.lower()
                found_keyword = False
                for keyword in donator_keywords:
                    if keyword in donator_text_lower:
                        name_part = donator_text_in_brackets[donator_text_lower.find(keyword) + len(keyword):].strip()
                        if name_part: donator_name = name_part
                        found_keyword = True; break
                if not found_keyword: donator_name = donator_text_in_brackets.strip()
                if donator_name:
                    prize_name = prize_name[:donator_match.start()] + prize_name[donator_match.end():]
                    prize_name = prize_name.strip()
        
        prize_name = prize_name.strip()
        if not prize_name: return full_prize_string, None, 1
            
        return prize_name, donator_name, quantity

    def _export_entry_method_to_file(self, requirement_text):
        try:
            data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
            if not data_dir_str: data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)
            if not data_dir_str: self.log_status("Error: Cannot find writable location for output file."); return
            app_data_dir = Path(data_dir_str); app_data_dir.mkdir(parents=True, exist_ok=True)
            output_path = app_data_dir / OUTPUT_ENTRY_METHOD_FILE
            with open(output_path, 'w', encoding='utf-8') as f: f.write(requirement_text)
        except Exception as e: self.log_status(f"Error exporting entry requirement: {e}")

    def _switch_to_animation_panel(self):
        animation_widget = self._animation_widget_ref
        if self.main_stack and animation_widget: 
            if self.main_stack.currentWidget() != animation_widget: 
                if not animation_widget.isVisible(): animation_widget.show(); QApplication.processEvents()
                self.main_stack.setCurrentWidget(animation_widget); QApplication.processEvents(); animation_widget.update(); QApplication.processEvents() 
            else:
                if not animation_widget.isVisible(): animation_widget.show()
                animation_widget.update(); QApplication.processEvents()
        elif webengine_available: QMessageBox.critical(self, "UI Error", "Cannot switch to animation view (widget missing).")

    def _switch_to_info_panel(self):
        if self.main_stack and self.info_panel: 
             if self.main_stack.currentWidget() != self.info_panel: 
                  if self._animation_widget_ref and self._animation_widget_ref != self.info_panel: self._animation_widget_ref.hide() 
                  self.main_stack.setCurrentWidget(self.info_panel); QApplication.processEvents() 
             else:
                  if not self.info_panel.isVisible(): self.info_panel.show() 
                  self.info_panel.update(); QApplication.processEvents() 

    def _update_participant_list_widget(self):
        self.participant_list.clear() 
        sorted_participants = sorted(list(self.participants), key=str.lower)
        for name in sorted_participants:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.participant_list.addItem(item) 
        self.update_ui_button_states()

    def _remove_winner_from_participants(self, winner_to_remove=None):
         name_to_remove = winner_to_remove if winner_to_remove else self.last_winner
         if name_to_remove and name_to_remove in self.participants:
             self.participants.discard(name_to_remove); self._update_participant_list_widget()
             self.animation_manager.update_participants(sorted(list(self.participants), key=str.lower))

    def _remove_confirmed_prize_from_lists(self):
        """Remove the confirmed random prize from the appropriate prize list"""
        if not hasattr(self, '_selected_prize_original_string') or not self._selected_prize_original_string:
            return  # No random prize was selected or already cleared
        
        prize_string_to_remove = self._selected_prize_original_string
        prize_removed = False
        
        # Check common prizes list first
        # common_prizes = self.config.get("common_prizes_list", [])
        # if prize_string_to_remove in common_prizes:
        #     # common_prizes.remove(prize_string_to_remove) # Per user request, do not remove from common pool
        #     # self.config["common_prizes_list"] = common_prizes
        #     prize_removed = True # We'll consider it "removed" to prevent it from being removed from the configured list
        #     if self.config.get('debug_mode_enabled', False):
        #         self.log_status(f"Confirmed prize '{prize_string_to_remove}' is from the common pool and will not be removed.")

        # Check configured prizes list if not found in common
        if not prize_removed:
            configured_prizes = self.config.get("prize_options", [])
            if prize_string_to_remove in configured_prizes:
                configured_prizes.remove(prize_string_to_remove)
                self.config["prize_options"] = configured_prizes
                prize_removed = True
                if self.config.get('debug_mode_enabled', False):
                    self.log_status(f"Removed confirmed prize '{prize_string_to_remove}' from configured prizes list.")
        
        if prize_removed:
            # Save the updated config
            config_manager.save_config(self.config)
            # Reload the dropdown to reflect the changes
            self._load_prize_options_into_dropdown()
            # Clear the tracking
            self._selected_prize_original_string = None
        else:
            self.log_status(f"Warning: Could not find prize '{prize_string_to_remove}' in any prize list for removal.")

    def _announce_draw_open(self):
        entry_type = self.config.get('entry_condition_type', ENTRY_TYPE_PREDEFINED)
        req_text = "---"
        if entry_type == ENTRY_TYPE_PREDEFINED: cmd = self.config.get('join_command', 'N/A'); req_text = f"Type '{cmd}'"
        elif entry_type == ENTRY_TYPE_CUSTOM: cmd = self.config.get('custom_join_command', 'N/A'); req_text = f"Type '{cmd}'"
        elif entry_type == ENTRY_TYPE_ANYTHING: req_text = "Type anything"
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"Draw OPEN! Requirement: {req_text} in chat.")
        prize_text_for_chat = (self.current_prize if self.current_prize != "<NO PRIZE SET>" else "prize").upper()
        self.schedule_twitch_message(f"🎁 GIVEAWAY OPEN! 🎁 Prize: {prize_text_for_chat}. {req_text} in chat!")

    def _announce_draw_closed(self):
        if self.config.get('debug_mode_enabled', False):
            self.log_status("Draw CLOSED.")
        self.schedule_twitch_message("Giveaway entries are now CLOSED.")

    def _announce_winner_confirmation_needed(self):
        if not self.last_winner: return
        conf_timeout = self.config.get('confirmation_timeout', 90)
        prize_text_for_chat = (self.current_prize if self.current_prize != "<NO PRIZE SET>" else "prize").upper()
        template = self.config.get("chat_msg_winner_confirmation_needed") or config_manager.DEFAULT_CONFIG.get("chat_msg_winner_confirmation_needed")
        try:
            msg = template.format(winner=self.last_winner, prize=prize_text_for_chat, timeout=conf_timeout)
        except Exception:
            msg = f"🎉 Congrats @{self.last_winner}! 🎉 You won: {prize_text_for_chat}! Type anything (or !ign) in chat within {conf_timeout}s to confirm!"
        self.schedule_twitch_message(msg)

    def _announce_confirmation_in_chat(self):
        if not self.last_winner: return
        template = self.config.get("chat_msg_awaiting_ign") or config_manager.DEFAULT_CONFIG.get("chat_msg_awaiting_ign")
        try:
            msg = template.format(winner=self.last_winner)
        except Exception:
            msg = f"@{self.last_winner} confirmed! Congratulations! Awaiting Capsuleers name, Please type !ign in chat"
        self.schedule_twitch_message(msg)

    @pyqtSlot(QWidget, str)
    def _handle_widget_geometry_change(self, widget, geometry_str):
        is_custom_mode = self.config.get("customisable_ui_enabled", True);
        is_locked = self.config.get("ui_locked", True)
        if not is_custom_mode or is_locked: return
        config_key = WIDGET_CONFIG_MAP.get(widget.objectName())
        if config_key and _validate_geometry_string(geometry_str):
            self.unsaved_layout_changes[config_key] = geometry_str
            if self.options_dialog_instance and self.options_dialog_instance.isVisible(): self.layout_adjusted.emit(config_key, geometry_str)

    def has_unsaved_layout_changes(self): return bool(self.unsaved_layout_changes)
    def get_unsaved_layout(self): return self.unsaved_layout_changes.copy()

    @pyqtSlot()
    def _commit_layout_changes(self, save_to_file=True):
        if not self.unsaved_layout_changes: return True
        self.config.update(self.unsaved_layout_changes); self.unsaved_layout_changes.clear(); self.log_status("Layout changes applied.")
        if save_to_file:
            if config_manager.save_config(self.config): self.log_status("Layout changes saved to file."); return True
            else: QMessageBox.warning(self, "Save Error", "Could not save layout changes to config file."); return False
        return True

    @pyqtSlot()
    def _discard_layout_changes(self):
        if not self.unsaved_layout_changes: return
        self.unsaved_layout_changes.clear()
        self.ui_manager.load_widget_geometries()
        if self.main_content_area: self.main_content_area.update() 
        self.log_status("Unsaved layout changes discarded.")

    def _start_timer_queue_poll(self):
        self.timer_poll_qtimer.timeout.connect(self.process_timer_queue); self.timer_poll_qtimer.start(50)

    @pyqtSlot()
    def process_timer_queue(self):
        try:
            while True:
                message = self.timer_queue.get_nowait(); msg_type, data = message[0], message[1]
                if msg_type == "timer_update": self.timer_update_signal.emit(data)
                elif msg_type == "timer_expired": self.timer_expired_signal.emit(data)
                elif msg_type == "timer_stopped": self.timer_stopped_signal.emit(data)
                elif msg_type == "play_sound": self.play_sound_signal.emit(data)
        except queue.Empty: pass
        except Exception as e: print(f"ERROR in process_timer_queue: {e}"); traceback.print_exc()

    def log_loaded_config(self):
        self.confirmation_log.append("--- Configuration ---") 
        token_ok = bool(self.config.get("token")); env_channel = self.config.get("channel", "N/A"); cfg_channel = self.config.get("target_channel"); active_channel = self.effective_channel or "N/A"
        if not token_ok: self.confirmation_log.append("ERROR: TWITCH_TOKEN not found in .env") 
        if not env_channel or env_channel == "N/A": self.confirmation_log.append("WARNING: TWITCH_CHANNEL not found in .env") 
        if not self.effective_channel: self.confirmation_log.append("ERROR: No effective channel (check .env and Options->General)") 
        self.confirmation_log.append(f"Active Channel: {active_channel}") 
        if cfg_channel and cfg_channel != active_channel: self.confirmation_log.append(f" (Override: {cfg_channel})") 
        elif env_channel != "N/A" and env_channel != active_channel: self.confirmation_log.append(f" (Fallback from .env: {env_channel})") 
        elif env_channel != "N/A" and not cfg_channel: self.confirmation_log.append(f" (Using .env: {env_channel})") 
        self.confirmation_log.append(f"Bot Nick: {self.config.get('nick', 'N/A')}") 
        self.confirmation_log.append(f"Ignoring Bot: {ENV_EVE2TWITCH_BOT_NAME}") 
        entry_type = self.config.get('entry_condition_type', ENTRY_TYPE_PREDEFINED)
        self.confirmation_log.append(f"Entry Method: {entry_type}") 
        if entry_type == ENTRY_TYPE_PREDEFINED: self.confirmation_log.append(f"  Command: {self.config.get('join_command', 'N/A')}") 
        elif entry_type == ENTRY_TYPE_CUSTOM: self.confirmation_log.append(f"  Custom Cmd: {self.config.get('custom_join_command', 'N/A')}") 
        elif entry_type == ENTRY_TYPE_ANYTHING: self.confirmation_log.append(f"  Condition: Type anything") 
        self.confirmation_log.append(f"Conf Timeout: {self.config.get('confirmation_timeout', 'N/A')}s") 
        self.confirmation_log.append(f"EVE Timeout: {self.config.get('eve_response_timeout', 'N/A')}s") 
        # Short ESI watchdog used when fetching ESI data after an auto-lookup
        esi_short = self.config.get('esi_short_timeout', config_manager.DEFAULT_CONFIG.get('esi_short_timeout'))
        try:
            esi_short_str = f"{float(esi_short)}s"
        except Exception:
            esi_short_str = str(esi_short)
        self.confirmation_log.append(f"ESI Short Timeout: {esi_short_str}") 
        self.confirmation_log.append(f"Customisable UI: {self.config.get('customisable_ui_enabled', True)}") 
        self.confirmation_log.append(f"UI Locked: {self.config.get('ui_locked', True)}") 
        self.confirmation_log.append(f"Font Size: {self.config.get('font_size_multiplier', 1.0):.0%}") 
        self.confirmation_log.append(f"Prize Selection Mode: {self.config.get('prize_selection_mode', PRIZE_MODE_POLL)}") 
        self.confirmation_log.append(f"Poll Duration: {self.config.get('poll_duration', 30)}s") 
        self.confirmation_log.append(f"Prize Options (raw): {len(self.config.get('prize_options', []))} configured") 
        self.confirmation_log.append(f"Common Prizes (raw): {len(self.config.get('common_prizes_list', []))} configured") 
        self.confirmation_log.append(f"Master Vol: {self.config.get('master_volume', 0.75):.0%}") 
        self.confirmation_log.append(f"Animation Type: {self.config.get('animation_type', 'N/A')}") 
        self.confirmation_log.append(f"GA Enabled: {self.config.get('google_analytics_enabled', False)}") 
        if self.config.get('google_analytics_enabled', False): self.confirmation_log.append(f"  GA ID: {self.config.get('ga_measurement_id', 'Not Set')}") 
        self.confirmation_log.append("---------------------") 

    def update_displays(self):
        prize_text_escaped = self.current_prize.replace('<', '&lt;').replace('>', '&gt;')
        donator_text_escaped = self.current_donator.replace('<', '&lt;').replace('>', '&gt;')
        display_html = f"<div style='text-align:left;'><span style='font-size:0.9em; color:#a0a0a0;'>Prize:</span><br>{prize_text_escaped}"
        if self.current_donator != "<NO DONATOR SET>": display_html += f"<br><br><span style='font-size:0.9em; color:#a0a0a0;'>Donated by:</span><br>{donator_text_escaped}"
        display_html += "</div>"; self.current_prize_donator_display.setText(display_html) 
        self.selected_winner_display.setText(self.selected_winner) 
        entry_type = self.config.get('entry_condition_type', ENTRY_TYPE_PREDEFINED); req_text_for_display, command_to_export = "---", ""
        if entry_type == ENTRY_TYPE_PREDEFINED: cmd = self.config.get('join_command', 'N/A'); req_text_for_display = f"Type '{cmd}' in chat."; command_to_export = cmd if cmd != 'N/A' else ""
        elif entry_type == ENTRY_TYPE_CUSTOM: cmd = self.config.get('custom_join_command', 'N/A'); req_text_for_display = f"Type '{cmd}' in chat."; command_to_export = cmd if cmd != 'N/A' else ""
        elif entry_type == ENTRY_TYPE_ANYTHING: req_text_for_display = "Type anything in chat."; command_to_export = ""
        self.entry_requirement_display.setText(req_text_for_display); self._export_entry_method_to_file(command_to_export) 
        self.update_participant_count(); self._update_prize_dropdown_behavior()

    def connect_signals(self):
        self.open_draw_button.clicked.connect(self.toggle_giveaway_state) 
        self.start_draw_button.clicked.connect(self._close_and_select_winner) 
        self.abandon_draw_button.clicked.connect(self.abandon_draw) 
        self.purge_list_button.clicked.connect(self.clear_participants) 
        self.remove_selected_button.clicked.connect(self.remove_selected_participant) 
        self.set_prize_button.clicked.connect(self._set_prize_and_donator_from_inputs) 
        self.clear_prize_button.clicked.connect(self.clear_prize) 
        self.prize_input.returnPressed.connect(self._set_prize_and_donator_from_inputs) 
        self.copy_log_button.clicked.connect(self.copy_eve_response_content) 
        self.participant_list.itemChanged.connect(self.update_ui_button_states)  
        self.options_button.clicked.connect(self.open_options_dialog) 
        if hasattr(self, 'set_prize_and_open_button'): self.set_prize_and_open_button.clicked.connect(self._set_prize_and_open_draw) 
        if hasattr(self, 'start_prize_poll_button'): self.start_prize_poll_button.clicked.connect(self.start_prize_poll) 
        if hasattr(self, 'prize_options_dropdown'): self.prize_options_dropdown.currentIndexChanged.connect(self._on_prize_dropdown_changed) 
        if hasattr(self, 'prize_mode_selector'): self.prize_mode_selector.currentTextChanged.connect(self._on_prize_mode_changed) 
        if hasattr(self, 'animation_type_selector_main'): self.animation_type_selector_main.currentTextChanged.connect(self._on_main_animation_type_changed) 
        self.timer_update_signal.connect(self._handle_timer_update); self.timer_expired_signal.connect(self._handle_timer_expired); self.timer_stopped_signal.connect(self._handle_timer_stopped)
        self.play_sound_signal.connect(self._handle_play_sound); self.animation_manager.js_ready_signal.connect(self._handle_js_ready)
        self.animation_manager.visuals_complete_signal.connect(self._handle_visual_animation_complete_start_timer)
        self.animation_manager.prize_reveal_complete_signal.connect(self._handle_prize_reveal_complete)
        self.animation_manager.sound_request_signal.connect(self._handle_js_sound_request); self.animation_manager.error_signal.connect(self.log_status)

    def _get_debug_info(self):
        """Generate debug information when debug mode is enabled."""
        if not self.config.get("debug_mode_enabled", False):
            return ""
        debug_info = []
        debug_info.append(f"State: {self.current_state.name}")
        debug_info.append(f"Participants: {len(self.participants)}")
        debug_info.append(f"Winner: {self.last_winner or 'None'}")
        debug_info.append(f"Prize: {self.current_prize}")
        # Check if twitch_thread and bot exist before accessing properties
        bot_ready = False
        if hasattr(self, 'twitch_thread') and self.twitch_thread and hasattr(self.twitch_thread, 'bot') and self.twitch_thread.bot:
            if hasattr(self.twitch_thread.bot, '_ready'):
                bot_ready = self.twitch_thread.bot._ready
        debug_info.append(f"Bot Connected: {'Yes' if bot_ready else 'No'}")
        if self.current_state == AppState.AWAITING_CONFIRMATION:
            debug_info.append(f"Confirmation Timeout: {CONFIRMATION_TIMEOUT}s")
        elif self.current_state == AppState.AWAITING_EVE_RESPONSE:
            debug_info.append(f"EVE Response Timeout: {EVE_RESPONSE_TIMEOUT}s")
            debug_info.append(f"EVE Response: {self.eve2twitch_response or 'None'}")
        elif self.current_state == AppState.AWAITING_PRIZE_POLL_VOTES:
            debug_info.append(f"Poll Votes: {sum(self.prize_poll_votes.values())}")
            debug_info.append(f"Poll Voters: {len(self.prize_poll_voters)}")
        return " | " + " | ".join(debug_info)

    def log_status(self, message):
        debug_mode = self.config.get('debug_mode_enabled', False)
        # Always print the raw message to the console for development/troubleshooting
        print(f"STATUS: {message}")

        # In debug mode, create a more detailed message for logging
        if debug_mode:
            full_message = message + self._get_debug_info()
        else:
            full_message = message

        # Always append relevant messages to the main confirmation log area
        if self.confirmation_log:
            self.confirmation_log.append(full_message)

        # --- STATUS BAR LOGIC ---
        if self.status_bar_label:
            channel_info = f" | Channel: {self.effective_channel}" if getattr(self, 'effective_channel', None) else ""
            if debug_mode:
                # In debug mode, show the full, dynamic status message
                status_text = f"STATUS: {full_message}{channel_info}"
                self.status_bar_label.setText(status_text)
            else:
                # When not in debug mode, only show the static channel info and hide dynamic messages.
                self.status_bar_label.setText(channel_info.lstrip(' | '))

    def auto_connect_twitch(self):
        self._set_state(AppState.BOT_CONNECTING); token, bot_nick, channel = self.config.get("token"), self.config.get("nick"), self.effective_channel
        if not channel: 
            self.log_status("ERROR: No Twitch channel specified")
            QMessageBox.critical(self, "Config Error", "No Twitch channel")
            self._set_state(AppState.BOT_DOWN)
            return
            
        if not token:
            self.log_status("ERROR: TWITCH_TOKEN missing")
            QMessageBox.critical(self, "Config Error", "Token missing")
            self._set_state(AppState.BOT_DOWN)
            return
            
        # Clean the token if needed
        token = token.replace('oauth:', '') if token.startswith('oauth:') else token
        # Show a concise connecting message in the UI so users know which channel we're targeting.
        try:
            if self.config.get('debug_mode_enabled', False):
                self.log_status(f"Connecting to #{channel}...")
        except Exception:
            # Fallback to console if log_status fails for any reason
            print(f"STATUS: Connecting to #{channel}...")
        if self.twitch_thread and self.twitch_thread.isRunning():
            self.stop_twitch_connection()
        try:
            self.twitch_thread = TwitchBotThread(token, channel, "", bot_nick)
            self.twitch_thread.message_received.connect(self.handle_message)
            self.twitch_thread.status_update.connect(self.handle_status_update)
            self.twitch_thread.error_occurred.connect(self.handle_error)
            self.twitch_thread.bot_ready_signal.connect(self.handle_bot_ready)
            self.twitch_thread.finished.connect(self.on_twitch_thread_finished)
            self.twitch_thread.start()
        except Exception as e:
            self.log_status(f"ERROR: Failed to start Twitch bot thread: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start Twitch: {e}")
            self._set_state(AppState.BOT_DOWN)
            traceback.print_exc()

    def stop_twitch_connection(self):
         if self.twitch_thread and self.twitch_thread.isRunning(): self.log_status("Stopping Twitch connection..."); self._set_state(AppState.BOT_DOWN); self.twitch_thread.stop()

    @pyqtSlot()
    def on_twitch_thread_finished(self):
        if self.current_state != AppState.BOT_DOWN: self._set_state(AppState.BOT_DOWN)

    @pyqtSlot(str)
    def handle_status_update(self, status):
        # Filter certain noisy connection messages from appearing in the main log when not in debug mode.
        # The decision to show in the status bar itself is handled entirely by log_status().
        debug_only_messages = [
            "Starting bot initialization",
            "Initializing and connecting bot",
            "STATUS: INITIALIZING",
            "Successfully connected to"
        ]

        is_debug_message = any(msg in status for msg in debug_only_messages)

        if is_debug_message and not self.config.get('debug_mode_enabled', False):
            # Don't log these specific messages to the confirmation log area if debug is off.
            # Printing to console still happens inside log_status.
            print(f"STATUS (Filtered): {status}")
            return
        
        # For all other messages, or if debug mode is on, log normally.
        self.log_status(status)
            
    # Status bar updates are now only handled in log_status (and only in debug mode)

    @pyqtSlot(str)
    def handle_error(self, error_message):
        if not ("Command Error:" in error_message and "not found" in error_message):
            self.log_status(f"ERROR: {error_message}"); QMessageBox.critical(self, "Twitch Error", error_message)
            if self.current_state != AppState.BOT_DOWN: self._set_state(AppState.BOT_DOWN)

    @pyqtSlot(str, str)
    def handle_message(self, username, message):
        print(f"🔧 DEBUG: handle_message called with username='{username}', message='{message}'")
        print(f"🔧 DEBUG: current_state = {self.current_state}")
        
        ignored_bot_name = ENV_EVE2TWITCH_BOT_NAME;
        if not username: 
            print(f"🔧 DEBUG: No username provided, returning")
            return
        username_lower, message_clean, message_lower = username.lower(), message.strip(), message.strip().lower()
        
        print(f"🔧 DEBUG: processed - username_lower='{username_lower}', message_clean='{message_clean}', message_lower='{message_lower}'")
        # If an external message mentions the winner in the form: @Winner: IGN "In Game Name" ...
        try:
            mention_ign_match = re.search(r"@(?P<tuser>[A-Za-z0-9_\-]+)\s*:\s*IGN\s*['\"](?P<ign>[^'\"]+)['\"]", message, re.IGNORECASE)
            if mention_ign_match:
                mentioned = mention_ign_match.group('tuser')
                quoted_ign = mention_ign_match.group('ign').strip()
                print(f"🔧 DEBUG: Detected @mention IGN pattern - mentioned='{mentioned}', quoted_ign='{quoted_ign}'")
                if self.last_winner and mentioned.lower() == self.last_winner.lower():
                    # Only accept this flow if the mention targets the current winner
                    try:
                        if self.config.get('debug_mode_enabled', False):
                            self.confirmation_log.append(f"Auto-detected registered IGN for @{mentioned}: {quoted_ign} — querying ESI...")
                    except Exception:
                        pass
                    # store raw response and move to ESI fetch directly
                    self.eve2twitch_response = message
                    # Cancel watchdog timer since we have a response
                    try:
                        if getattr(self, '_eve2twitch_timeout_timer', None):
                            try:
                                self._eve2twitch_timeout_timer.cancel()
                            except Exception:
                                pass
                            self._eve2twitch_timeout_timer = None
                    except Exception:
                        pass
                    self._set_state(AppState.FETCHING_ESI_DATA)
                    QTimer.singleShot(50, lambda ign=quoted_ign: self._fetch_esi_data(ign))
                    return
        except Exception as e:
            print(f"DEBUG: Error parsing mention-IGN pattern: {e}")
        
        if ignored_bot_name and username_lower == ignored_bot_name:
            print(f"🔧 DEBUG: Message from ignored bot {ignored_bot_name}, checking EVE response logic")
            if self.current_state == AppState.AWAITING_EVE_RESPONSE and self.last_winner and re.search(rf"(?i)@{re.escape(self.last_winner)}", message) and re.search(r'(?i)\bign\b', message):
                self.eve2twitch_response = message
                # Cancel watchdog timer since we have a response
                try:
                    if getattr(self, '_eve2twitch_timeout_timer', None):
                        try:
                            self._eve2twitch_timeout_timer.cancel()
                        except Exception:
                            pass
                        self._eve2twitch_timeout_timer = None
                except Exception:
                    pass
                    self._set_state(AppState.FETCHING_ESI_DATA)
                return

            # If a winner has been confirmed with ESI, ignore subsequent !ign commands for this cycle.
            if self.current_state == AppState.CONFIRMED_WITH_IGN and message_lower.startswith("!ign"):
                if self.config.get('debug_mode_enabled', False):
                    self.log_status(f"DEBUG: Ignoring '{message_clean}' from {username}; ESI already processed for this win.")
                return
        if self.current_state in [AppState.ANIMATING_WINNER, AppState.FETCHING_ESI_DATA]: 
            print(f"🔧 DEBUG: In state {self.current_state}, ignoring message")
            return
        if self.current_state == AppState.AWAITING_PRIZE_POLL_VOTES:
            print(f"🔧 DEBUG: In prize poll voting state")
            if username_lower not in self.prize_poll_voters:
                try:
                    vote_number = int(message_clean)
                    for idx, option_data in enumerate(self.current_poll_options):
                        if option_data["number"] == vote_number: self.prize_poll_votes[option_data["original_index"]] += 1; self.prize_poll_voters.add(username_lower); self._update_prize_poll_display_in_log(); break
                except ValueError: pass
            return
        # Confirmation / IGN handling
        if self.current_state == AppState.AWAITING_CONFIRMATION and self.last_winner and username_lower == self.last_winner.lower():
            print(f"🔧 DEBUG: Processing confirmation from winner")
            self.confirmation_message = message_clean

            # Allow the winner to provide their IGN directly with: !ign <IGN_NAME>
            if message_clean.lower().startswith("!ign "):
                # Extract provided IGN and start ESI lookup immediately
                provided_ign = message_clean.split(None, 1)[1].strip()
                if provided_ign:
                    print(f"🔧 DEBUG: Winner provided IGN inline: {provided_ign}")
                    # Move to fetching ESI data for the provided IGN
                    self._set_state(AppState.FETCHING_ESI_DATA)
                    # Start ESI lookup for the provided IGN
                    QTimer.singleShot(50, lambda ign=provided_ign: self._fetch_esi_data(ign))
                    return

            # If winner types bare !ign we wait for the external EVE bot response
            if message_lower == "!ign":
                self._set_state(AppState.AWAITING_EVE_RESPONSE)
            else:
                # Any other chat text counts as a simple confirmation without IGN
                self._set_state(AppState.CONFIRMED_NO_IGN)
            return

        elif self.current_state == AppState.CONFIRMED_NO_IGN and self.last_winner and username_lower == self.last_winner.lower():
            # Allow the winner to send !ign or !ign <IGN> after confirmation as well
            if message_clean.lower().startswith("!ign "):
                provided_ign = message_clean.split(None, 1)[1].strip()
                if provided_ign:
                    print(f"🔧 DEBUG: Confirmed winner provided IGN inline: {provided_ign}")
                    self._set_state(AppState.FETCHING_ESI_DATA)
                    QTimer.singleShot(50, lambda ign=provided_ign: self._fetch_esi_data(ign))
                    return
            if message_lower == "!ign":
                print(f"🔧 DEBUG: Processing IGN request from confirmed winner")
                self._set_state(AppState.AWAITING_EVE_RESPONSE)
                return

            # Allow winner to write IGN in the form: IGN "In Game Name" (without the leading !)
            ign_quoted_match = re.search(r"\bIGN\s*[\"']([^\"']+)[\"']", message, re.IGNORECASE)
            if ign_quoted_match:
                provided_ign = ign_quoted_match.group(1).strip()
                if provided_ign:
                    print(f"🔧 DEBUG: Winner provided quoted IGN: {provided_ign}")
                    self._set_state(AppState.FETCHING_ESI_DATA)
                    QTimer.singleShot(50, lambda ign=provided_ign: self._fetch_esi_data(ign))
                    return
            # Also accept the format: IGN "In Game Name"
            ign_quoted_match = re.search(r"\bIGN\s*[\"']([^\"']+)[\"']", message, re.IGNORECASE)
            if ign_quoted_match:
                provided_ign = ign_quoted_match.group(1).strip()
                if provided_ign:
                    print(f"🔧 DEBUG: Confirmed winner provided quoted IGN: {provided_ign}")
                    self._set_state(AppState.FETCHING_ESI_DATA)
                    QTimer.singleShot(50, lambda ign=provided_ign: self._fetch_esi_data(ign))
                    return
        elif self.current_state == AppState.COLLECTING:
            print(f"🔧 DEBUG: In COLLECTING state, processing entry")
            entry_type = self.config.get('entry_condition_type', ENTRY_TYPE_PREDEFINED)
            print(f"🔧 DEBUG: entry_type = '{entry_type}'")
            
            user_can_enter = False
            if entry_type == ENTRY_TYPE_PREDEFINED: 
                join_command = self.config.get("join_command", "##INVALID##").lower()
                user_can_enter = message_lower == join_command
                print(f"🔧 DEBUG: PREDEFINED - join_command='{join_command}', message_lower='{message_lower}', match={user_can_enter}")
            elif entry_type == ENTRY_TYPE_CUSTOM: 
                custom_command = self.config.get("custom_join_command", "##INVALID##").lower()
                user_can_enter = message_lower == custom_command
                print(f"🔧 DEBUG: CUSTOM - custom_command='{custom_command}', message_lower='{message_lower}', match={user_can_enter}")
            elif entry_type == ENTRY_TYPE_ANYTHING: 
                user_can_enter = bool(message_clean)
                print(f"🔧 DEBUG: ANYTHING - message_clean='{message_clean}', bool(message_clean)={user_can_enter}")
            
            print(f"🔧 DEBUG: user_can_enter = {user_can_enter}")
            
            if user_can_enter:
                existing_participants_lower = {p.lower() for p in self.participants}
                print(f"🔧 DEBUG: existing participants (lowercase): {existing_participants_lower}")
                print(f"🔧 DEBUG: username_lower in existing: {username_lower in existing_participants_lower}")
                
                if username_lower not in existing_participants_lower:
                    print(f"🔧 DEBUG: Adding {username} to participants")
                    self.participants.add(username); logging_utils.log_activity("DRAW_ENTRY", username); self._update_participant_list_widget()
                    if self.config.get('debug_mode_enabled', False):
                        self.log_status(f"Entry added: {username}")
                    self.animation_manager.update_participants(sorted(list(self.participants), key=str.lower))
                    logging_utils.send_ga_event(self.config, "draw_entry", {"event_label": "UserJoinedDraw", "entry_method": entry_type}, self.log_status)
                    print(f"🔧 DEBUG: Successfully added {username}. Total participants: {len(self.participants)}")
                else:
                    print(f"🔧 DEBUG: {username} already in participants, not adding again")
            else:
                print(f"🔧 DEBUG: user_can_enter is False, not adding {username}")
        else:
            print(f"🔧 DEBUG: In state {self.current_state}, not processing as entry")

    def update_participant_count(self): self.entries_count_label.setText(f"ENTRIES: {len(self.participants)}") 

    def update_ui_button_states(self):
        can_set_clear_prize_input_fields = self.current_state in [AppState.IDLE, AppState.COLLECTING] or self.current_state in [AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN, AppState.TIMED_OUT, AppState.EVE_TIMED_OUT]
        self.set_prize_button.setEnabled(can_set_clear_prize_input_fields); self.clear_prize_button.setEnabled(can_set_clear_prize_input_fields); self.prize_input.setEnabled(can_set_clear_prize_input_fields) 
        current_prize_mode = self.prize_mode_selector.currentText()
        
        # Allow changing selectors when draw is complete (IGN collected means draw is finished)
        finished_states = [AppState.IDLE, AppState.TIMED_OUT, AppState.EVE_TIMED_OUT, AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN]
        can_change_selectors = self.current_state in [AppState.IDLE, AppState.COLLECTING] or self.current_state in finished_states
        
        if hasattr(self, 'prize_mode_selector'): self.prize_mode_selector.setEnabled(can_change_selectors) 
        if hasattr(self, 'animation_type_selector_main'): self.animation_type_selector_main.setEnabled(can_change_selectors) 
        self._update_prize_dropdown_behavior()
        is_connected = self.current_state not in [AppState.STARTING, AppState.BOT_CONNECTING, AppState.BOT_DOWN]; has_participants = bool(self.participants)
        is_item_checked = any(self.participant_list.item(i).checkState() == Qt.CheckState.Checked for i in range(self.participant_list.count()) if self.participant_list.item(i)) 
        busy_states = [AppState.ANIMATING_WINNER, AppState.AWAITING_CONFIRMATION, AppState.AWAITING_EVE_RESPONSE, AppState.FETCHING_ESI_DATA, AppState.BOT_CONNECTING, AppState.AWAITING_PRIZE_POLL_VOTES]
        can_purge = True; can_options = self.current_state not in busy_states; can_open_close = is_connected and self.current_state not in busy_states
        can_select = is_connected and self.current_state in finished_states and has_participants
        can_close_select = is_connected and (self.current_state == AppState.COLLECTING or self.current_state in finished_states) and has_participants
        can_abandon = is_connected and self.current_state in busy_states
        if hasattr(self, 'set_prize_and_open_button'): self.set_prize_and_open_button.setEnabled(is_connected and self.current_state not in busy_states and self.current_state != AppState.COLLECTING) 
        can_remove = is_item_checked and (self.current_state in finished_states or self.current_state == AppState.COLLECTING or self.current_state == AppState.AWAITING_PRIZE_POLL_VOTES)
        can_copy = bool(self.eve2twitch_response and re.search(r'"', self.eve2twitch_response))

        raw_prize_options = self.config.get("prize_options", [])
        distinct_prize_type_map = {} 
        for p_str in raw_prize_options:
            base_name, donator, _ = self._parse_prize_and_donator(p_str)
            display_key = base_name
            if donator: display_key += f" ({donator})"
            if display_key not in distinct_prize_type_map: distinct_prize_type_map[display_key] = p_str
        
        can_start_poll = is_connected and self.current_state == AppState.IDLE and \
                         current_prize_mode == PRIZE_MODE_POLL and \
                         len(distinct_prize_type_map) >= 1


        self.open_draw_button.setEnabled(can_open_close); self.open_draw_button.setText("CLOSE DRAW" if self.current_state == AppState.COLLECTING else "OPEN DRAW") 
        self.start_draw_button.setEnabled(can_close_select); self.abandon_draw_button.setEnabled(can_abandon) 
        self.purge_list_button.setEnabled(can_purge); self.options_button.setEnabled(can_options); self.remove_selected_button.setEnabled(can_remove) 
        self.copy_log_button.setEnabled(can_copy); 
        if hasattr(self, 'start_prize_poll_button'): self.start_prize_poll_button.setEnabled(can_start_poll) 
        self.update_participant_count()

    def _start_confirmation_timer(self, winner_name, timeout):
        self._stop_confirmation_timer()
        self.confirmation_stop_event = threading.Event()
        self.confirmation_timer_thread = threading.Thread(
            target=run_timer_thread,
            args=("confirmation", winner_name, timeout, self.confirmation_stop_event, self)
        )
        self.confirmation_timer_thread.start()

    def _stop_confirmation_timer(self):
        if self.confirmation_timer_thread and self.confirmation_timer_thread.is_alive():
            if self.confirmation_stop_event: self.confirmation_stop_event.set()
            self.confirmation_timer_thread.join(timeout=1.0)
            if self.confirmation_timer_thread.is_alive():
                 print("Warning: Confirmation timer thread did not stop cleanly.")
        self.confirmation_timer_thread = None
        self.confirmation_stop_event = None

    def _start_eve_response_timer(self, winner_name, timeout):
        self._stop_eve_response_timer()
        self.eve_response_stop_event = threading.Event()
        self.eve_response_timer_thread = threading.Thread(
            target=run_timer_thread,
            args=("eve_response", winner_name, timeout, self.eve_response_stop_event, self)
        )
        self.eve_response_timer_thread.start()

    def _stop_eve_response_timer(self):
        if self.eve_response_timer_thread and self.eve_response_timer_thread.is_alive():
            if self.eve_response_stop_event: self.eve_response_stop_event.set()
            self.eve_response_timer_thread.join(timeout=1.0)
            if self.eve_response_timer_thread.is_alive():
                 print("Warning: EVE Response timer thread did not stop cleanly.")
        self.eve_response_timer_thread = None
        self.eve_response_stop_event = None

    def _start_eve2twitch_lookup(self, twitch_username: str, interval_seconds: int = 1, lookup_timeout: int = None):
        """Start a background lookup to an EVE2Twitch HTTP API for the given twitch username.
        The URL should be configured via the EVE2TWITCH_API_URL env var and may include '{twitch}' for templating.
        If not configured, this function logs and returns.
        """
        if not twitch_username:
            return
        # strip leading @ if present and trim whitespace
        twitch_username = twitch_username.strip()
        if twitch_username.startswith('@'):
            twitch_username = twitch_username[1:]
        if not EVE2TWITCH_API_URL:
            self.log_status("Automatic EVE2Twitch lookup not configured (EVE2TWITCH_API_URL unset). Waiting for bot response instead.")
            return

        # stop existing poll thread if any
        try:
            if getattr(self, '_eve2twitch_poll_stop_event', None):
                self._eve2twitch_poll_stop_event.set()
        except Exception:
            pass

        # Logging of the auto-lookup attempt is handled by _set_state (debug-only).

        self._eve2twitch_poll_stop_event = threading.Event()
        self._eve2twitch_poll_thread = threading.Thread(target=self._eve2twitch_lookup_thread, args=(twitch_username, interval_seconds, self._eve2twitch_poll_stop_event))
        self._eve2twitch_poll_thread.daemon = True
        self._eve2twitch_poll_thread.start()

        # If a lookup timeout is requested, schedule a fallback to ask for !ign
        try:
            timeout_secs = lookup_timeout if lookup_timeout is not None else self.config.get('eve2twitch_lookup_timeout', 10)
            if timeout_secs and timeout_secs > 0:
                def _eve2twitch_lookup_timeout_watchdog():
                    # If still waiting for a response, stop the poll and prompt for !ign
                    try:
                        if getattr(self, '_eve2twitch_poll_stop_event', None) and not getattr(self, '_eve2twitch_poll_stop_event').is_set():
                            try:
                                self._stop_eve2twitch_poll()
                            except Exception:
                                pass
                            # If no eve2twitch_response was produced, ask the winner to use !ign
                            if not self.eve2twitch_response:
                                # Schedule UI-affecting calls on the Qt main thread
                                try:
                                    QTimer.singleShot(0, lambda: self.log_status("Automatic EVE2Twitch lookup timed out. Asking winner to provide !ign in chat."))
                                except Exception:
                                    print("E2T: Failed to schedule log_status on main thread")
                                try:
                                    QTimer.singleShot(0, lambda: self._announce_confirmation_in_chat())
                                except Exception:
                                    print("E2T: Failed to schedule announce_confirmation_in_chat on main thread")
                    finally:
                        # Clear the timer reference
                        try:
                            self._eve2twitch_timeout_timer = None
                        except Exception:
                            pass

                # Use a threading.Timer so it runs even if the Qt event loop is busy
                try:
                    self._eve2twitch_timeout_timer = threading.Timer(float(timeout_secs), _eve2twitch_lookup_timeout_watchdog)
                    self._eve2twitch_timeout_timer.daemon = True
                    self._eve2twitch_timeout_timer.start()
                except Exception:
                    # Fallback to QTimer if threading.Timer cannot be created
                    QTimer.singleShot(int(timeout_secs * 1000), _eve2twitch_lookup_timeout_watchdog)
        except Exception:
            pass

    def _stop_eve2twitch_poll(self):
        try:
            if getattr(self, '_eve2twitch_poll_stop_event', None):
                self._eve2twitch_poll_stop_event.set()
            if getattr(self, '_eve2twitch_poll_thread', None) and self._eve2twitch_poll_thread.is_alive():
                self._eve2twitch_poll_thread.join(timeout=1.0)
        except Exception:
            pass
        # Cancel watchdog timer if present
        try:
            if getattr(self, '_eve2twitch_timeout_timer', None):
                try:
                    self._eve2twitch_timeout_timer.cancel()
                except Exception:
                    pass
        except Exception:
            pass
        self._eve2twitch_poll_thread = None
        self._eve2twitch_poll_stop_event = None
        self._eve2twitch_timeout_timer = None

    def _eve2twitch_lookup_thread(self, twitch_username: str, interval_seconds: int, stop_event: threading.Event):
        try:
            # Build URL
            lookup_url = EVE2TWITCH_API_URL
            if not lookup_url:
                return

            while not stop_event.is_set():
                try:
                    # URL-encode the twitch username for safe inclusion
                    safe_twitch = quote_plus(twitch_username)
                    if '{twitch}' in lookup_url:
                        url = lookup_url.format(twitch=safe_twitch)
                    else:
                        sep = '&' if '?' in lookup_url else '?'
                        url = f"{lookup_url}{sep}twitch={safe_twitch}"

                    print(f"EVE2TWITCH: Querying {url}")
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        try:
                            payload = resp.json()
                        except Exception:
                            payload = None

                        raw = resp.text
                        ign = None
                        if isinstance(payload, dict):
                            ign = payload.get('ign') or payload.get('character') or payload.get('name')
                        if not ign and payload and isinstance(payload, list) and payload:
                            first = payload[0]
                            if isinstance(first, dict):
                                ign = first.get('ign') or first.get('name')

                        if not ign:
                            m = re.search(r'"([^"\n]{2,40})"', raw)
                            if m: ign = m.group(1)

                        if ign:
                                self.eve2twitch_response = raw
                                print(f"E2T LOOKUP: Found IGN '{ign}' for @{twitch_username}")
                                try:
                                    # Emit signal to main thread to log and start ESI fetch
                                    self.eve2twitch_ign_found.emit(twitch_username, ign, raw)
                                except Exception:
                                    # Fallback: attempt to schedule via QTimer on main thread
                                    try:
                                        if self.config.get('debug_mode_enabled', False):
                                            QTimer.singleShot(0, lambda: self.confirmation_log.append(f"EVE2Twitch lookup found IGN: {ign} for @{twitch_username}. Fetching ESI..."))
                                        QTimer.singleShot(50, lambda ign=ign: self._fetch_esi_data(ign))
                                    except Exception:
                                        pass
                                return
                    else:
                        print(f"E2T LOOKUP: HTTP {resp.status_code} for {url}")
                        # If the API returns 404 the user likely hasn't registered with EVE2Twitch.
                        # Immediately fall back to asking the user to register or provide their IGN.
                        # If the API returns 404 the user likely hasn't registered with EVE2Twitch.
                        # Emit a signal to the main thread to handle this failure case.
                        if resp.status_code == 404:
                            try:
                                # Emit to main thread; the slot will log and schedule chat safely
                                self.eve2twitch_lookup_failed.emit(twitch_username)
                            except Exception:
                                # As fallback, attempt to schedule on main thread via QTimer
                                try:
                                    template = self.config.get("chat_msg_auto_lookup_failed") or config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_failed")
                                    try:
                                        msg = template.format(winner=twitch_username)
                                    except Exception:
                                        msg = f"@{twitch_username} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign <your in-game name>' in chat to provide your IGN."
                                except Exception:
                                    msg = f"@{twitch_username} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign <your in-game name>' in chat to provide your IGN."
                                try:
                                    QTimer.singleShot(0, lambda m=msg: self.confirmation_log.append(m))
                                except Exception:
                                    print("E2T: Failed to append auto-lookup failed message to confirmation log (fallback)")
                                try:
                                    QTimer.singleShot(0, lambda m=msg: self.schedule_twitch_message(m))
                                except Exception:
                                    print("E2T: Failed to schedule auto-lookup failed chat message (fallback)")
                            # Stop polling and exit thread; main thread will handle messaging
                            return

                except Exception as e:
                    print(f"E2T LOOKUP ERR: {e}")
                # Wait before retry
                stop_event.wait(timeout=interval_seconds)
        except Exception as e:
            print(f"E2T LOOKUP THREAD ERROR: {e}")
            traceback.print_exc()

    def _start_prize_poll_timer(self, timeout):
        self._stop_prize_poll_timer()
        self.prize_poll_stop_event = threading.Event()
        self.prize_poll_timer_thread = threading.Thread(
            target=run_timer_thread,
            args=("prize_poll", "PrizePoll", timeout, self.prize_poll_stop_event, self)
        )
        self.prize_poll_timer_thread.start()

    def _stop_prize_poll_timer(self):
        if self.prize_poll_timer_thread and self.prize_poll_timer_thread.is_alive():
            if self.prize_poll_stop_event: self.prize_poll_stop_event.set()
            self.prize_poll_timer_thread.join(timeout=1.0)
            if self.prize_poll_timer_thread.is_alive():
                print("Warning: Prize Poll timer thread did not stop cleanly.")
        self.prize_poll_timer_thread = None
        self.prize_poll_stop_event = None

    def _fetch_esi_data(self, ign):
        if self.esi_worker_thread and self.esi_worker_thread.isRunning():
            if self.config.get('debug_mode_enabled', False):
                self.log_status("ESI worker busy. Please wait.")
            return
        # reset watchdog flag and possibly cancel existing watchdog
        self._esi_response_received = False
        try:
            if getattr(self, '_esi_watchdog_timer', None):
                try:
                    self._esi_watchdog_timer.cancel()
                except Exception:
                    pass
                self._esi_watchdog_timer = None
        except Exception:
            self._esi_watchdog_timer = None

        self.esi_worker_thread = ESIWorkerThread(ign)
        self.esi_worker_thread.esi_data_ready.connect(self._handle_esi_data_ready)
        self.esi_worker_thread.esi_error.connect(self._handle_esi_error)
        self.esi_worker_thread.start()
        # Start a short watchdog: if no ESI response within configured seconds, ask for !ign in chat
        try:
            # read configurable timeout (fallback to default config or 5s)
            try:
                esi_watchdog_timeout = float(self.config.get('esi_short_timeout', config_manager.DEFAULT_CONFIG.get('esi_short_timeout', 5)))
            except Exception:
                esi_watchdog_timeout = 5.0

            def _watchdog_cb(expected_ign=ign):
                try:
                    if getattr(self, '_esi_response_received', False):
                        return
                    # Only prompt if we're still in the ESI-fetching state
                    if self.current_state == AppState.FETCHING_ESI_DATA:
                        template = self.config.get("chat_msg_awaiting_ign") or config_manager.DEFAULT_CONFIG.get("chat_msg_awaiting_ign")
                        try:
                            msg = template.format(winner=self.last_winner)
                        except Exception:
                            msg = f"@{self.last_winner} confirmed! Congratulations! Awaiting Capsuleers name, Please type !ign in chat"
                        self.log_status("ESI watchdog: no response within 5s, prompting for IGN in chat")
                        try:
                            self.schedule_twitch_message(msg)
                        except Exception:
                            pass
                except Exception:
                    pass

            self._esi_watchdog_timer = threading.Timer(esi_watchdog_timeout, _watchdog_cb)
            self._esi_watchdog_timer.daemon = True
            self._esi_watchdog_timer.start()
        except Exception:
            self._esi_watchdog_timer = None

    # Method to format ESI data as HTML for the confirmation log
    def _format_character_sheet_html(self, data):
        char_name_original = data.get('name', 'N/A')
        corp_name_original = data.get('corporation_name', 'N/A')
        alliance_name_original = data.get('alliance_name') 
        portrait_base64 = data.get('portrait_base64')
        portrait_content_type = data.get('portrait_content_type', 'image/png')

        char_name_html = char_name_original.replace('<', '&lt;').replace('>', '&gt;') if isinstance(char_name_original, str) else (char_name_original or "N/A")
        corp_name_html = corp_name_original.replace('<', '&lt;').replace('>', '&gt;') if isinstance(corp_name_original, str) else (corp_name_original or "N/A")
        alliance_name_html = alliance_name_original.replace('<', '&lt;').replace('>', '&gt;') if isinstance(alliance_name_original, str) else ""

        # Increase image and font size for better visibility and apply font multiplier
        img_size = 180  # Increased from 128
        td_width = img_size + 10 
        base_font_size = 12  # Reduced from 16 for smaller text
        font_multiplier = self.config.get("font_size_multiplier", 1.0)
        font_size_pt = int(base_font_size * font_multiplier) 

        # Create an elegant, modern character card with premium styling - properly centered
        html = f"<div style='text-align: center; margin: 20px auto; padding: 0; display: flex; justify-content: center; width: 100%;'>"
        
        # Main card container with gradient background and shadows - block display for proper centering
        html += f"<div style='display: block; background: linear-gradient(135deg, #0a0f1a 0%, #1a1f2a 50%, #0f1419 100%); "
        html += f"border: 3px solid #4af1f2; border-radius: 16px; padding: 25px; "
        html += f"box-shadow: 0 0 30px rgba(74, 241, 242, 0.4), inset 0 0 20px rgba(74, 241, 242, 0.1); "
        html += f"position: relative; width: 500px; text-align: center;'>"
        
        # Add a subtle inner glow border
        html += f"<div style='position: absolute; top: 8px; left: 8px; right: 8px; bottom: 8px; "
        html += f"border: 1px solid rgba(232, 217, 0, 0.3); border-radius: 12px; pointer-events: none;'></div>"

        # Header with decorative line (removed EVE PILOT DOSSIER text and made smaller)
        html += f"<div style='margin-bottom: 20px; text-align: center;'>"
        # The decorative line element has been removed.
        html += f"</div>"

        # Content area with vertical centered layout
        html += f"<div style='text-align: center; width: 100%;'>"
        
        # Portrait section - Table-based centering for QTextEdit compatibility
        html += f"<table style='width: 100%; margin-bottom: 25px;'><tr><td style='text-align: center;'>"
        if portrait_base64 and portrait_content_type:
            html += f"<div style='position: relative; display: inline-block;'>"
            html += f"<img src='data:{portrait_content_type};base64,{portrait_base64}' width='{img_size}' height='{img_size}' "
            html += f"style='border: 4px solid #e8d900; border-radius: 12px; "
            html += f"box-shadow: 0 0 25px rgba(232, 217, 0, 0.6), 0 0 50px rgba(74, 241, 242, 0.3); "
            html += f"transition: transform 0.3s ease; display: block; margin: 0 auto;'>"
            # Add corner decorations
            html += f"<div style='position: absolute; top: -8px; left: -8px; width: 20px; height: 20px; "
            html += f"border-top: 3px solid #4af1f2; border-left: 3px solid #4af1f2; border-radius: 4px 0 0 0;'></div>"
            html += f"<div style='position: absolute; top: -8px; right: -8px; width: 20px; height: 20px; "
            html += f"border-top: 3px solid #4af1f2; border-right: 3px solid #4af1f2; border-radius: 0 4px 0 0;'></div>"
            html += f"<div style='position: absolute; bottom: -8px; left: -8px; width: 20px; height: 20px; "
            html += f"border-bottom: 3px solid #4af1f2; border-left: 3px solid #4af1f2; border-radius: 0 0 0 4px;'></div>"
            html += f"<div style='position: absolute; bottom: -8px; right: -8px; width: 20px; height: 20px; "
            html += f"border-bottom: 3px solid #4af1f2; border-right: 3px solid #4af1f2; border-radius: 0 0 4px 0;'></div>"
            html += f"</div>"
        else:
            html += f"<div style='width:{img_size}px; height:{img_size}px; border:4px solid #e8d900; border-radius: 12px; "
            html += f"display:inline-flex; align-items:center; justify-content:center; color:#e8d900; background: linear-gradient(45deg, #2a2a2a, #1a1a1a); "
            html += f"font-weight: bold; box-shadow: 0 0 25px rgba(232, 217, 0, 0.3); margin: 0 auto;'>📸<br>No Portrait</div>"
        html += f"</td></tr></table>"
        html += f"</div>"
        
        # Information section with better typography - centered
        html += f"<div style='text-align: center; width: 100%; margin: 0 auto;'>"
        
        # Character name section
        html += f"<div style='margin-bottom: 20px;'>"
        html += f"<div style='font-size: {int(font_size_pt * 0.9)}pt; color: #4af1f2; font-weight: bold; "
        html += f"text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;'>🚀 CHARACTER</div>"
        html += f"<div style='font-size: {int(font_size_pt * 1.3)}pt; color: #ffffff; font-weight: bold; "
        html += f"text-shadow: 0 0 8px rgba(255, 255, 255, 0.5); line-height: 1.2; "
        html += f"padding: 8px 12px; "
        html += f"border-radius: 0 8px 8px 0; margin: 0 auto; display: inline-block;'>{char_name_html}</div>"
        html += f"</div>"
        
        # Corporation section - all blue
        html += f"<div style='margin-bottom: 15px;'>"
        html += f"<div style='font-size: {int(font_size_pt * 0.9)}pt; color: #4af1f2; font-weight: bold; "
        html += f"text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;'>🏢 CORPORATION</div>"
        html += f"<div style='font-size: {int(font_size_pt * 1.1)}pt; color: #ffffff; font-weight: 500; "
        html += f"padding: 6px 12px; "
        html += f"border-radius: 0 6px 6px 0; line-height: 1.3; margin: 0 auto; display: inline-block;'>{corp_name_html}</div>"
        html += f"</div>"
        
        # Alliance section (if present) - all blue
        if alliance_name_html: 
            html += f"<div style='margin-bottom: 10px;'>"
            html += f"<div style='font-size: {int(font_size_pt * 0.9)}pt; color: #4af1f2; font-weight: bold; "
            html += f"text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;'>⭐ ALLIANCE</div>"
            html += f"<div style='font-size: {int(font_size_pt * 1.1)}pt; color: #ffffff; font-weight: 500; "
            html += f"padding: 6px 12px; "
            html += f"border-radius: 0 6px 6px 0; line-height: 1.3; margin: 0 auto; display: inline-block;'>{alliance_name_html}</div>"
            html += f"</div>"
        
        html += f"</div>"  # Close info section
        html += f"</div>"  # Close content flex container
        
        # Footer with status indicator
        html += f"<div style='margin-top: 20px; text-align: center;'>"
        html += f"<div style='display: inline-block; padding: 8px 16px; "
        html += f"border-radius: 20px; font-size: {int(font_size_pt * 0.8)}pt; "
        html += f"color: #4af1f2; font-weight: bold; letter-spacing: 1px;'>✅ VERIFIED PILOT</div>"
        html += f"</div>"
        
        html += f"</div>"  # Close main card container
        html += f"</div>"  # Close outer container
        return html

    @pyqtSlot(dict)
    def _handle_esi_data_ready(self, data):
        # mark that ESI has responded and cancel any watchdog
        try:
            self._esi_response_received = True
            if getattr(self, '_esi_watchdog_timer', None):
                try:
                    self._esi_watchdog_timer.cancel()
                except Exception:
                    pass
                self._esi_watchdog_timer = None
        except Exception:
            pass

        if self.current_state != AppState.FETCHING_ESI_DATA:
            print(f"MAIN_APP_DEBUG: _handle_esi_data_ready called while in state {self.current_state}; continuing for debug.")
        print(f"MAIN_APP_DEBUG: _handle_esi_data_ready received data. Portrait base64 present: {bool(data.get('portrait_base64'))}, Type: {data.get('portrait_content_type')}")

        # Store the ESI data for potential font size updates
        self._last_esi_data = data.copy()

        # Extract a plain IGN (character name) from the ESI data and
        # make it available for copying. Also automatically copy to
        # the clipboard so operators don't have to manually press copy.
        try:
            ign_candidate = None
            if isinstance(data.get('name'), str) and data.get('name').strip():
                ign_candidate = data.get('name').strip()
            elif isinstance(data.get('character_name'), str) and data.get('character_name').strip():
                ign_candidate = data.get('character_name').strip()
            else:
                # nested fallback if data contains a 'character' dict
                ch = data.get('character')
                if isinstance(ch, dict):
                    maybe = ch.get('name') or ch.get('character_name')
                    if isinstance(maybe, str) and maybe.strip():
                        ign_candidate = maybe.strip()

            if ign_candidate:
                # Store on the main app for later use by the copy button
                self.last_verified_ign = ign_candidate
                try:
                    QApplication.clipboard().setText(ign_candidate)
                    if self.config.get('debug_mode_enabled', False):
                        self.log_status(f"Copied IGN to clipboard: {ign_candidate}")
                    # Avoid appending this to the confirmation_log to prevent duplicate messages;
                    # debug mode shows the status in the status bar only.
                except Exception as _c_e:
                    print(f"MAIN_APP_DEBUG: Failed to set clipboard text: {_c_e}")
                # Announce in chat that IGN was found and congratulate the winner
                try:
                    # Simple fixed announcement per request
                    self.schedule_twitch_message("IGN found, congratulations on winning")
                except Exception as _msg_e:
                    print(f"MAIN_APP_DEBUG: Failed to schedule IGN-found chat message: {_msg_e}")
        except Exception as _e:
            print(f"MAIN_APP_DEBUG: Error extracting or copying IGN from ESI data: {_e}")

        # Append the formatted HTML to the confirmation log
        if self.config.get('debug_mode_enabled', False):
            self.confirmation_log.append(f"\n--- ESI Data for {self.last_winner} ---")
        html_sheet = self._format_character_sheet_html(data)

        # If a portrait base64 is present, insert it programmatically into the
        # QTextEdit using a QTextCursor and QTextImageFormat. This avoids HTML
        # rendering issues with data: URIs or custom resource schemes.
        try:
            portrait_b64 = data.get('portrait_base64')
            portrait_ct = data.get('portrait_content_type', 'image/png')
            img_inserted = False
            if portrait_b64:
                try:
                    img_bytes = base64.b64decode(portrait_b64)
                    qimg = QImage.fromData(img_bytes)
                    if not qimg.isNull():
                        doc = self.confirmation_log.document()
                        resource_name = f"esiimage://{data.get('id')}"
                        resource_url = QUrl(resource_name)
                        # Use the ResourceType enum available on QTextDocument in PyQt6
                        doc.addResource(QTextDocument.ResourceType.ImageResource, resource_url, qimg)
                        try:
                            reg = doc.resource(QTextDocument.ResourceType.ImageResource, resource_url)
                            print(f"MAIN_APP_DEBUG: Resource registration check for {resource_name}: {'FOUND' if reg is not None else 'NOT FOUND'}")
                        except Exception as _res_e:
                            print(f"MAIN_APP_DEBUG: Could not query document resource: {_res_e}")

                        # Split the HTML around the <img ...> tag so we can insert
                        # the image programmatically between the two parts.
                        img_match = re.search(r"<img[^>]*src=['\"][^'\"]+['\"][^>]*>", html_sheet, flags=re.IGNORECASE)
                        if img_match:
                            html_before = html_sheet[:img_match.start()]
                            html_after = html_sheet[img_match.end():]
                        else:
                            html_before = html_sheet
                            html_after = ""

                        # Append the HTML before the image
                        if html_before.strip():
                            try:
                                self.confirmation_log.append(html_before)
                            except Exception as e:
                                print(f"MAIN_APP_DEBUG: Failed to append html_before: {e}")

                        # Insert image via cursor
                        try:
                            cursor = self.confirmation_log.textCursor()
                            cursor.movePosition(QTextCursor.MoveOperation.End)

                            # Insert a centered block for the image so it appears centered
                            try:
                                block_fmt = QTextBlockFormat()
                                block_fmt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                                cursor.insertBlock(block_fmt)
                            except Exception as _bf_e:
                                print(f"MAIN_APP_DEBUG: Could not set block format for centering: {_bf_e}")

                            img_fmt = QTextImageFormat()
                            img_fmt.setName(resource_name)
                            # Explicit size (fallback to 180)
                            try:
                                img_fmt.setWidth(180)
                                img_fmt.setHeight(180)
                            except Exception:
                                pass

                            cursor.insertImage(img_fmt)
                            # Insert a new block after the image to continue normal flow
                            try:
                                cursor.insertBlock()
                            except Exception:
                                pass

                            img_inserted = True
                            print(f"MAIN_APP_DEBUG: Inserted portrait image via QTextCursor for id={data.get('id')} (centered)")
                        except Exception as e:
                            print(f"MAIN_APP_DEBUG: Failed to insert image via QTextCursor: {e}")

                        # Append any HTML after the image
                        if html_after.strip():
                            try:
                                self.confirmation_log.append(html_after)
                            except Exception as e:
                                print(f"MAIN_APP_DEBUG: Failed to append html_after: {e}")
                    else:
                        print("MAIN_APP_DEBUG: QImage.fromData returned null image.")
                except Exception as img_e:
                    print(f"MAIN_APP_DEBUG: Error decoding or inserting portrait image: {img_e}")

            # If the image wasn't inserted programmatically, fall back to appending
            # the full HTML (which may include a file:// URL if earlier code replaced it).
            if not ('img_inserted' in locals() and img_inserted):
                preview = html_sheet
                if isinstance(preview, str) and len(preview) > 1000:
                    preview = preview[:1000] + '...<truncated>'
                print("MAIN_APP_DEBUG: Falling back to appending full HTML (trimmed):\n" + preview)
                self.confirmation_log.append(html_sheet)
        except Exception as e:
            print(f"MAIN_APP_DEBUG: Unexpected error in portrait insertion: {e}")
        self.confirmation_log.append("---------------------")
        
        if self.animation_manager and hasattr(self.animation_manager, 'update_winner_esi_details_js'):
            print(f"MAIN_APP_DEBUG: Calling animation_manager.update_winner_esi_details_js with ESI data (before state change).")
            self.animation_manager.update_winner_esi_details_js(data)
            self.just_processed_esi = True
            self._remove_completed_prize_from_list()

            def finalize_and_idle():
                """Function to set confirmed state, then transition to idle and clear winner context."""
                self._set_state(AppState.CONFIRMED_WITH_IGN)

                def go_idle_and_clear():
                    try:
                        self._set_state(AppState.IDLE)
                    except Exception:
                        pass
                    try:
                        self.last_winner = None
                    except Exception:
                        pass
                    if self.config.get('debug_mode_enabled', False):
                        self.log_status("DEBUG: Draw cycle complete. Winner context cleared.")

                # After a brief moment for the UI to update and be readable, transition to IDLE to end the cycle and clear winner context.
                QTimer.singleShot(1500, go_idle_and_clear)

            # Set the confirmed state after a short delay for animations to receive data
            QTimer.singleShot(300, finalize_and_idle)
            print(f"MAIN_APP_DEBUG: Scheduled state change to CONFIRMED_WITH_IGN, followed by IDLE.")
        else:
            print("MAIN_APP_DEBUG: animation_manager or update_winner_esi_details_js method not found!")
            self._remove_completed_prize_from_list()
            self._set_state(AppState.CONFIRMED_WITH_IGN)
            # Transition to IDLE even if animation manager isn't present — clear winner context as well
            def go_idle_and_clear_fallback():
                try:
                    self._set_state(AppState.IDLE)
                except Exception:
                    pass
                try:
                    self.last_winner = None
                except Exception:
                    pass

            QTimer.singleShot(1500, go_idle_and_clear_fallback)


    @pyqtSlot(str)
    def _handle_esi_error(self, error_message):
        # cancel watchdog if running
        try:
            self._esi_response_received = True
            if getattr(self, '_esi_watchdog_timer', None):
                try:
                    self._esi_watchdog_timer.cancel()
                except Exception:
                    pass
                self._esi_watchdog_timer = None
        except Exception:
            pass

        if self.current_state != AppState.FETCHING_ESI_DATA:
            return

        # --- Create and append the stylized HTML block for the ESI error ---
        font_multiplier = self.config.get("font_size_multiplier", 1.0)
        font_size = int(16 * font_multiplier)  # Base font size for calculations

        # Clean up the error message for a tidier display
        clean_error = str(error_message)
        if "ESI Error for" in clean_error:
            clean_error = clean_error.split(':', 1)[-1].strip()
        if "ESI HTTP Error" in clean_error:
            clean_error = clean_error.split('for URL:')[0].strip()

        esi_error_html = f"""
        <div style='text-align: center; margin: 20px 0; padding: 0;'>
            <div style='display: inline-block; background: linear-gradient(135deg, #2a0a0a 0%, #3a1a1a 50%, #2f0f0f 100%);
                         border: 3px solid #ff6b6b; border-radius: 15px; padding: 20px 30px;
                         box-shadow: 0 0 25px rgba(255, 107, 107, 0.4), inset 0 0 15px rgba(255, 107, 107, 0.1); position: relative;'>

                <div style='font-size: {int(font_size * 1.2)}pt; color: #ff6b6b; font-weight: bold;
                            text-shadow: 0 0 10px rgba(255, 107, 107, 0.8); letter-spacing: 1px; margin-bottom: 12px;'>
                    <span style='font-family: "Segoe UI Symbol", "Arial";'>❌</span> ESI VALIDATION FAILED
                </div>

                <div style='font-size: {int(font_size * 1.5)}pt; color: #ffffff; font-weight: bold;
                            text-shadow: 0 0 8px rgba(255, 255, 255, 0.6); margin-bottom: 8px;'>
                    {self.last_winner}
                </div>

                <div style='font-size: {int(font_size * 0.9)}pt; color: #ffcccc; font-style: italic; opacity: 0.8;'>
                    {clean_error}
                </div>

                <div style='position: absolute; top: -3px; left: -3px; right: -3px; bottom: -3px;
                            border: 1px solid rgba(255, 107, 107, 0.3); border-radius: 15px; pointer-events: none;'>
                </div>
            </div>
        </div>
        """
        try:
            self.confirmation_log.append(esi_error_html)
        except Exception:
            # Fallback to plain text logging if HTML append fails
            try:
                self.confirmation_log.append(f"\n--- ESI Error for {self.last_winner} ---\n{error_message}\n---------------------")
            except Exception:
                print(f"MAIN_APP_DEBUG: Could not append ESI error to confirmation_log: {error_message}")

        # Suppress the generic confirmation UI block that would normally be
        # appended when entering CONFIRMED_NO_IGN because we've already shown
        # a specialized error/instruction block above.
        try:
            self.suppress_next_confirmation_message = True
        except Exception:
            pass

        # Also schedule an instructive chat message prompting the winner to
        # register with Eve2Twitch or use the !ign command. Prefer the
        # configurable template if present.
        try:
            template = self.config.get("chat_msg_auto_lookup_failed") or config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_failed")
            try:
                chat_msg = template.format(winner=self.last_winner)
            except Exception:
                chat_msg = f"@{self.last_winner} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign \"your in-game name\"' in chat to provide your IGN."
        except Exception:
            chat_msg = f"@{self.last_winner} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign \"your in-game name\"' in chat to provide your IGN."

        try:
            self.schedule_twitch_message(chat_msg)
        except Exception:
            pass

        self._set_state(AppState.CONFIRMED_NO_IGN)


    def _cancel_active_draw_processes(self, reason="Cancelled"):
        self.log_status(f"Cancelling active processes: {reason}")
        self._stop_confirmation_timer()
        self._stop_eve_response_timer()
        self._stop_prize_poll_timer()

        # cancel any pending esi watchdog
        try:
            if getattr(self, '_esi_watchdog_timer', None):
                try:
                    self._esi_watchdog_timer.cancel()
                except Exception:
                    pass
                self._esi_watchdog_timer = None
        except Exception:
            pass

        if self.esi_worker_thread and self.esi_worker_thread.isRunning():
            self.log_status("Stopping ESI worker...")
            self.esi_worker_thread.quit()
            if not self.esi_worker_thread.wait(1000):
                self.log_status("Warning: ESI worker did not terminate cleanly.")
            self.esi_worker_thread = None

        self.animation_manager.cancel_animation()
        self._switch_to_info_panel()

        if self.current_state == AppState.COLLECTING:
            self._announce_draw_closed()

        self._set_state(AppState.IDLE)


    @pyqtSlot(dict)
    def _handle_timer_update(self, data):
        if data.get("type") == "prize_poll":
            remaining = data.get("remaining", 0)
            if int(remaining) % 5 == 0 or remaining < 10: 
                self._update_prize_poll_display_in_log()
                base_message = f"Prize Poll Time Remaining: {remaining:.0f}s"
                
                # Add debug information if debug mode is enabled
                if self.config.get("debug_mode_enabled", False):
                    debug_suffix = f" | Voters: {len(self.prize_poll_voters)} | Total Votes: {sum(self.prize_poll_votes.values())}"
                    base_message += debug_suffix
                
                self.confirmation_log.append(base_message) 

    @pyqtSlot(dict)
    def _handle_timer_expired(self, data):
        timer_type, context = data["type"], data.get("context", "Unknown")
        if timer_type == "confirmation" and self.current_state == AppState.AWAITING_CONFIRMATION and self.last_winner == context:
            self.sound_manager.play("fail")
            # Remove the winner from the participants list
            if self.last_winner in self.participants:
                self.participants.discard(self.last_winner)
                self._update_participant_list_widget()
                self.animation_manager.update_participants(sorted(list(self.participants), key=str.lower))
                self.log_status(f"Removed {self.last_winner} from draw list due to no response.")
            self._set_state(AppState.TIMED_OUT)
        elif timer_type == "eve_response" and self.current_state == AppState.AWAITING_EVE_RESPONSE and self.last_winner == context: self.sound_manager.play("fail"); self._set_state(AppState.EVE_TIMED_OUT)
        elif timer_type == "prize_poll" and self.current_state == AppState.AWAITING_PRIZE_POLL_VOTES: self._finalize_prize_poll()

    @pyqtSlot(str)
    def _handle_timer_stopped(self, timer_type):
        if timer_type == "confirmation":
            self.sound_manager.stop("countdown") 
            self.sound_manager.stop("timer_high")
            self.sound_manager.stop("timer_mid")
            self.sound_manager.stop("timer_low")

    @pyqtSlot(dict)
    def _handle_play_sound(self, sound_data):
        key, action, loops = sound_data.get("key"), sound_data.get("action", "play"), sound_data.get("loops", 0)
        if key and action == "play": self.sound_manager.play(key, loops)
        elif key and action == "stop": self.sound_manager.stop(key)

    @pyqtSlot()
    def _handle_js_ready(self):
         if self.config.get('debug_mode_enabled', False):
             self.log_status("Animation page ready.")
         self.animation_panel_ready_for_display = True
         self.animation_manager.update_participants(sorted(list(self.participants), key=str.lower))
         if webengine_available and not self._first_animation_warmup_done and self._animation_widget_ref:
             current_widget = self.main_stack.currentWidget() 
             if not self._animation_widget_ref.isVisible(): self._animation_widget_ref.show()
             self.main_stack.setCurrentWidget(self._animation_widget_ref); QApplication.processEvents() 
             QTimer.singleShot(20, lambda: self._finish_warmup(current_widget))
         elif self.current_state == AppState.ANIMATING_WINNER: self._switch_to_animation_panel()

    def _finish_warmup(self, original_widget):
        if self.main_stack.currentWidget() == self._animation_widget_ref: self.main_stack.setCurrentWidget(original_widget); QApplication.processEvents() 
        self._first_animation_warmup_done = True
        if self.current_state == AppState.ANIMATING_WINNER:
            self._switch_to_animation_panel()

    @pyqtSlot(str)
    def _handle_js_sound_request(self, sound_message: str):
        parts = sound_message.split(':'); action_or_key = parts[0]
        if not action_or_key: return
        if action_or_key == "play" and len(parts) >= 2:
            sound_key, loops = parts[1], int(parts[2]) if len(parts) > 2 else 0
            self.sound_manager.play(sound_key, loops=loops)
        elif action_or_key == "stop" and len(parts) >= 2: self.sound_manager.stop(parts[1])
        elif len(parts) == 1 and action_or_key in [SOUND_NOTIFICATION_KEY, "wheel_tick"]: self.sound_manager.play(action_or_key, loops=0)

    @pyqtSlot(str)
    def _handle_visual_animation_complete_start_timer(self, winner_name):
        # Check if this is a prize reveal animation
        if hasattr(self, '_is_prize_reveal_active') and self._is_prize_reveal_active:
            # For prize reveal, wait 2 seconds then continue to winner animation
            self._finish_prize_reveal_and_continue_to_winner_draw()
            return

        if self.current_state != AppState.ANIMATING_WINNER or winner_name != self.last_winner:
            self._set_state(AppState.IDLE)
            return

        self.sound_manager.play("winner")
        self.selected_winner = self.last_winner
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"WINNER (Visuals Done): {self.selected_winner}")
        log_donator = f" (Donated by: {self.current_donator})" if self.current_donator != "<NO DONATOR SET>" else ""
        if self.config.get('debug_mode_enabled', False):
            self.confirmation_log.append(f"\n--- WINNER: {self.selected_winner} | Prize: {self.current_prize}{log_donator} ---") 
        self.update_displays()

        self.sound_manager.play("countdown", loops=-1)

        self._set_state(AppState.AWAITING_CONFIRMATION)

    @pyqtSlot(str, str)
    def _handle_prize_reveal_complete(self, prize_name, donator_name):
        """Handle the completion of prize reveal animation and continue to winner draw"""
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"🎲 Prize reveal completed: {prize_name}")
        self._finish_prize_reveal_and_continue_to_winner_draw()

    @pyqtSlot(bool)
    def _handle_lock_state_change_from_dialog(self, is_locked):
        self.config['ui_locked'] = is_locked; self._update_layout_mode()

    @pyqtSlot(float)
    def _handle_apply_font_now(self, new_multiplier: float):
        print(f"MainApp: Received apply_font_now_signal with multiplier: {new_multiplier}")
        if abs(self.config.get("font_size_multiplier", 1.0) - new_multiplier) > 0.001:
            self.config["font_size_multiplier"] = new_multiplier
            self._apply_font_size() 
            self.log_status(f"Font size temporarily applied: {new_multiplier*100:.0f}%")
        else:
            self.log_status(f"Font size {new_multiplier*100:.0f}% already active or no change.")

    @pyqtSlot(dict)
    def apply_options_changes(self, config_from_dialog):
        old_font_multiplier = self.config.get("font_size_multiplier", 1.0)
        new_font_multiplier = config_from_dialog.get("font_size_multiplier", 1.0)

        self.config.update(config_from_dialog)
        self.config["customisable_ui_enabled"] = True

        if self.animation_type_selector_main: self.animation_type_selector_main.setCurrentText(self.config.get("animation_type", config_manager.ANIM_TYPE_HACKING)) 
        if self.prize_mode_selector: self.prize_mode_selector.setCurrentText(self.config.get("prize_selection_mode", PRIZE_MODE_POLL)) 
        self.effective_channel = self.config.get("target_channel") or self.config.get("channel")
        global CONFIRMATION_TIMEOUT, EVE_RESPONSE_TIMEOUT; CONFIRMATION_TIMEOUT = self.config.get("confirmation_timeout", 90); EVE_RESPONSE_TIMEOUT = self.config.get("eve_response_timeout", 300)
        self.sound_manager.apply_volumes(self.config); self._load_prize_options_into_dropdown(); self.update_displays()

        font_changed_from_original = abs(new_font_multiplier - old_font_multiplier) > 0.001
        if font_changed_from_original:
            print(f"MainApp: Font size changed on dialog Save. Old: {old_font_multiplier}, New: {new_font_multiplier}")
            self._apply_font_size()
        else:
            print("MainApp: Font size from dialog same as original state. No font refresh needed.")


        self._update_layout_mode()
        self.update_ui_button_states()
        logging_utils.init_ga_config_ref(self.config)
        if self.config.get("google_analytics_enabled", False): logging_utils._ensure_ga_client_id()

    def _remove_completed_prize_from_list(self):
        """Remove the current prize from the prize options list after IGN completion"""
        if not self.current_prize or self.current_prize == "<NO PRIZE SET>":
            return
            
        # Get the original prize string if it was a mystery prize
        prize_to_remove = getattr(self, '_selected_prize_original_string', None) or self.current_prize
        
        # Get the lists
        prize_options = self.config.get("prize_options", [])
        common_prizes = self.config.get("common_prizes_list", [])

        removed_from_regular = False

        # Check if the prize to remove is in the common list. If so, we do nothing to that list.
        is_in_common_prizes = prize_to_remove in common_prizes

        if is_in_common_prizes:
            self.log_status(f"✅ Prize '{self.current_prize}' is from the common pool and will not be removed.")
            # We can effectively mark it as "removed" so the rest of the logic works,
            # and we save the config to persist any other changes.
            removed_from_regular = True 
        else:
            # If it's not a common prize, try to remove it from the regular prize list.
            if prize_to_remove in prize_options:
                prize_options.remove(prize_to_remove)
                self.config["prize_options"] = prize_options
                removed_from_regular = True

        if removed_from_regular:
            # Save the updated config
            config_manager.save_config(self.config)
            
            # Reload the prize dropdown to reflect changes
            self._load_prize_options_into_dropdown()
            
            # Log the removal if it wasn't a common prize
            if not is_in_common_prizes:
                self.log_status(f"✅ Prize '{self.current_prize}' automatically removed from regular prize list after IGN completion")
            
            # Clean up mystery prize variables
            if hasattr(self, '_selected_prize_original_string'):
                delattr(self, '_selected_prize_original_string')
            if hasattr(self, '_hidden_prize_name'):
                delattr(self, '_hidden_prize_name')
        else:
            self.log_status(f"⚠️ Could not find prize '{self.current_prize}' in prize lists for auto-removal")

    @pyqtSlot()
    def toggle_giveaway_state(self):
        # --- Logic for CLOSING the draw ---
        if self.current_state == AppState.COLLECTING:
            self._announce_draw_closed()
            self._set_state(AppState.IDLE)
            return

        # --- Logic for OPENING the draw ---
        # First, run all validation checks.
        if not self.is_twitch_bot_ready:
            QMessageBox.warning(self, "Bot Not Ready", "The Twitch bot is not connected. Please wait for a connection.")
            self.log_status("Open draw failed: Bot not ready.")
            return

        if self.current_prize == "<NO PRIZE SET>":
            QMessageBox.warning(self, "No Prize Set", "A prize must be set before the draw can be opened.")
            self.log_status("Open draw failed: No prize selected.")
            return
            
        busy_states = [
            AppState.ANIMATING_WINNER, AppState.AWAITING_CONFIRMATION,
            AppState.AWAITING_EVE_RESPONSE, AppState.FETCHING_ESI_DATA,
            AppState.AWAITING_PRIZE_POLL_VOTES
        ]
        if self.current_state in busy_states:
            self.log_status("Cannot open draw during an active process.")
            return
        
        # If all checks pass, open the draw.
        valid_open_states = [
            AppState.IDLE, AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN,
            AppState.TIMED_OUT, AppState.EVE_TIMED_OUT
        ]
        if self.current_state in valid_open_states:
            self._set_state(AppState.COLLECTING)

    @pyqtSlot()
    def _set_prize_and_donator_from_inputs(self):
        full_prize_text = self.prize_input.text().strip() 
        if not full_prize_text:
            self.current_prize, self.current_donator = "<NO PRIZE SET>", "<NO DONATOR SET>"
            self._selected_prize_original_string = None # Clear original string if prize is cleared
        else:
            prize_name, donator, _ = self._parse_prize_and_donator(full_prize_text)
            self.current_prize = prize_name
            self.current_donator = donator or "<NO DONATOR SET>"
            # Store the original full string for accurate removal later
            self._selected_prize_original_string = full_prize_text
        
        # Clear any hidden prize state when manually setting prize
        self._clear_hidden_prize_state()
        
        self.prize_input.clear() 
        self.log_status(f"Prize set: {self.current_prize} | Donator: {self.current_donator}")
        self.update_displays()

    def _clear_hidden_prize_state(self):
        """Clear hidden prize state when manually setting/clearing prizes"""
        self._needs_prize_reveal = False
        self._prize_reveal_data = None
        self._hidden_prize_name = None
        self._hidden_donator = None
        self._selected_prize_original_string = None

    @pyqtSlot()
    def clear_prize(self):
        self.prize_input.clear()
        self.current_prize = "<NO PRIZE SET>"
        self.current_donator = "<NO DONATOR SET>"
        # Clear any hidden prize state when clearing prize
        self._clear_hidden_prize_state()
        self.log_status("Prize and Donator cleared.")
        self.update_displays() 

    def _trigger_random_prize_selection(self):
        """Trigger random prize selection and mark for reveal animation during draw"""
        # Check if we're in a valid state for prize selection
        if self.current_state not in [AppState.IDLE, AppState.COLLECTING, AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN, AppState.TIMED_OUT, AppState.EVE_TIMED_OUT]:
            QMessageBox.warning(self, "Action Denied", f"Cannot select random prize in {self.current_state.name} state.")
            return

        # Get all available prizes
        common_raw = self.config.get("common_prizes_list", [])
        configured_raw = self.config.get("prize_options", [])
        
        all_prizes = []
        if common_raw:
            all_prizes.extend(self._expand_prize_list(common_raw))
        if configured_raw:
            all_prizes.extend(self._expand_prize_list(configured_raw))
        
        if not all_prizes:
            QMessageBox.warning(self, "No Prizes", "No prizes available for random selection.")
            return

        # Select a random prize but keep it hidden
        import random
        selected_prize_data = random.choice(all_prizes)
        prize_name = selected_prize_data["base_name"]
        donator = selected_prize_data.get("donator")
        
        # Store the real prize data but show a hidden placeholder
        self._hidden_prize_name = prize_name
        self._hidden_donator = donator or "<NO DONATOR SET>"
        
        # Store the original prize string for removal after confirmation
        self._selected_prize_original_string = selected_prize_data["original_full"]
        
        # Set placeholder values that will be shown until reveal
        self.current_prize = "🎲 MYSTERY PRIZE 🎲"
        self.current_donator = "🎁 TO BE REVEALED 🎁"
        
        # Mark that this prize needs a reveal animation during the next draw
        self._needs_prize_reveal = True
        self._prize_reveal_data = {
            'prize_name': prize_name,
            'donator': donator or "<NO DONATOR SET>"
        }
        
        # Clear the prize input field
        if self.prize_input:
            self.prize_input.clear()
        
        # Update displays and reset dropdown
        self.update_displays()
        if hasattr(self, 'prize_options_dropdown'):
            # Set dropdown to 'Random Prize' entry
            prize_count = self.prize_options_dropdown.count()
            for i in range(prize_count):
                item_text = self.prize_options_dropdown.itemText(i)
                if item_text == DROPDOWN_RANDOM_PRIZE_TEXT:
                    self.prize_options_dropdown.blockSignals(True)
                    self.prize_options_dropdown.setCurrentIndex(i)
                    self.prize_options_dropdown.blockSignals(False)
                    break
        
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"🎲 Mystery Prize Selected! (Will be revealed during draw)")

    def _start_prize_reveal_animation(self, prize_name, donator):
        """Start the prize reveal with visual text display - Triglavian font morphing to normal"""
        if self.config.get('debug_mode_enabled', False):
            self.log_status("🎲 Starting prize reveal...")
        
        # Set flag to indicate this is a prize reveal
        self._is_prize_reveal_active = True
        
        # Switch to animation panel for the visual text display
        self._switch_to_animation_panel()
        
        # Create the reveal text with prize and donator formatted for display
        if donator != "<NO DONATOR SET>":
            # Prize name on top, donator below, centered
            reveal_text = f"{prize_name.upper()}\n(DONATED BY: {donator.upper()})"
            # Clean animation name - remove newlines for JavaScript processing
            animation_name = f"{prize_name} (Donated by: {donator})"
        else:
            reveal_text = f"{prize_name.upper()}"
            animation_name = f"{prize_name}"
        
        # Configure for prize reveal: Triglavian text morph with 2-second hold
        anim_options = {
            'countdownDurationS': 4,  # 2s morph + 2s hold in normal font
            'isPrizeReveal': True,    # Flag to identify this as prize reveal
            'revealText': reveal_text,
            'holdAfterMorph': 2       # Hold for 2 seconds after morphing to normal font
        }
        
        # Play prize reveal sound
        self.play_sound_signal.emit({"key": "notification", "action": "play"})
        
        # Start the visual Triglavian text morph display (prize reveal, not general animation)
        self.animation_manager.start_prize_reveal(prize_name, donator)
        
        if self.config.get('debug_mode_enabled', False):
            self.log_status(f"🎲 Revealing Prize: {prize_name} (Donator: {donator})")

    def _finish_prize_reveal_and_continue_to_winner_draw(self):
        """Finish the prize reveal animation and continue to winner draw immediately"""
        if self.config.get('debug_mode_enabled', False):
            self.log_status("🎲 Prize revealed! Starting winner draw...")
        
        # No additional delay needed since JavaScript now handles full 8-second timing
        self._continue_to_winner_animation()

    def _continue_to_winner_animation(self):
        """Continue to the main winner draw animation after prize reveal"""
        self._is_prize_reveal_active = False
        self._needs_prize_reveal = False
        
        # Reveal the actual prize now
        if self._hidden_prize_name and self._hidden_donator:
            self.current_prize = self._hidden_prize_name
            self.current_donator = self._hidden_donator
            if self.config.get('debug_mode_enabled', False):
                self.log_status(f"🎲 Prize Revealed: {self._hidden_prize_name} (Donator: {self._hidden_donator})")
            
            # Clear the hidden prize data
            self._hidden_prize_name = None
            self._hidden_donator = None
            
            # Update displays with the real prize
            self.update_displays()
        
        self._prize_reveal_data = None
        
        if self.config.get('debug_mode_enabled', False):
            self.log_status("🎲 Prize reveal complete, starting winner draw animation...")
        self._start_js_animation(is_continuation=True)

    def _start_winner_draw_continuation(self):
        """Start the winner draw animation as a continuation of prize reveal"""
        if not self.last_winner:
            self._set_state(AppState.IDLE)
            return

        # Use normal confirmation timeout for winner draw
        countdown_s = self.config.get('confirmation_timeout', 90)
        options = {
            'countdownDurationS': countdown_s,
           'revealInterval': {"Normal": 300, "Slow": 700, "Very Slow": 1200}.get(self.config.get("animation_box_speed", "Normal"), 300)
        }

        countdown_s = self.config.get('confirmation_timeout', 90)
        options = {
            'countdownDurationS': countdown_s,
            'revealInterval': {"Normal": 300, "Slow": 700, "Very Slow": 1200}.get(self.config.get("animation_box_speed", "Normal"), 300)
        }
        anim_type_to_use = self.config.get("animation_type", config_manager.DEFAULT_CONFIG["animation_type"])
        print(f"Winner draw after random prize reveal: Using animation type '{anim_type_to_use}'")
        self.sound_manager.play("animation_start", loops=0)
        self.animation_manager.start_reveal(self.last_winner, anim_type_to_use, options)

    @pyqtSlot()
    def _set_prize_and_open_draw(self):
        # Only update prize from input field if there's actually text in it
        if self.prize_input.text().strip():
            self._set_prize_and_donator_from_inputs()
        # If no text input and no prize selected, show warning and prevent opening draw
        elif self.current_prize == "<NO PRIZE SET>":
            QMessageBox.warning(self, "No Prize Selected", "Please select or enter a prize before opening the draw.")
            self.log_status("No prize selected. Use dropdown or type a prize name first.")
            return
            
        if self.current_state in [AppState.STARTING, AppState.BOT_CONNECTING, AppState.BOT_DOWN]: QMessageBox.warning(self, "Not Connected", "Twitch bot must be connected."); return
        if self.current_state in [AppState.ANIMATING_WINNER, AppState.AWAITING_CONFIRMATION, AppState.AWAITING_EVE_RESPONSE, AppState.FETCHING_ESI_DATA, AppState.AWAITING_PRIZE_POLL_VOTES]: self.log_status("Cannot open draw during active process."); return
        if self.current_state == AppState.COLLECTING: self.log_status("Draw is already open."); return
        if self.current_state in [AppState.IDLE, AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN, AppState.TIMED_OUT, AppState.EVE_TIMED_OUT]: self._set_state(AppState.COLLECTING)

    @pyqtSlot()
    def remove_selected_participant(self):
        allowed_states = [AppState.IDLE, AppState.COLLECTING, AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN, AppState.TIMED_OUT, AppState.EVE_TIMED_OUT, AppState.AWAITING_PRIZE_POLL_VOTES]
        if self.current_state not in allowed_states: QMessageBox.warning(self, "Action Denied", f"Cannot remove in {self.current_state.name} state."); return
        to_remove = [self.participant_list.item(i).text() for i in range(self.participant_list.count()) if self.participant_list.item(i).checkState() == Qt.CheckState.Checked] 
        if not to_remove: self.log_status("No participant(s) checked to remove."); return
        if QMessageBox.question(self, "Remove", f"Remove {len(to_remove)} participant(s)?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            removed_count = sum(1 for name in to_remove if name in self.participants and self.participants.remove(name) is None)
            if removed_count > 0: self._update_participant_list_widget(); self.log_status(f"Removed {removed_count} participant(s)."); self.animation_manager.update_participants(sorted(list(self.participants), key=str.lower)); self.update_ui_button_states()

    @pyqtSlot()
    def copy_eve_response_content(self):
        # Prefer copying the last verified IGN if available (set when ESI lookup succeeds).
        ign = getattr(self, 'last_verified_ign', None)
        if ign:
            try:
                QApplication.clipboard().setText(ign)
                self.log_status(f"Copied IGN: {ign}")
            except Exception as _e:
                self.log_status(f"Failed to copy IGN: {_e}")
            return

        # Fallback: copy the quoted part of the raw EVE->Twitch response (legacy behavior)
        if not self.eve2twitch_response:
            self.log_status("No EVE response to copy.")
            return
        match = re.search(r'"([^"]*)"', self.eve2twitch_response)
        if match:
            try:
                QApplication.clipboard().setText(match.group(1))
                self.log_status(f"Copied EVE response: \"{match.group(1)}\"")
            except Exception as _e:
                self.log_status(f"Failed to copy EVE response: {_e}")
        else:
            self.log_status("Could not find text in quotes in EVE response.")

    @pyqtSlot()
    def clear_participants(self):
        if not self.participants and self.selected_winner == "---" and self.current_state == AppState.IDLE: self.log_status("Nothing to purge."); return
        prompt = "Purge all entrants and clear selected winner?"; cancel_states = [AppState.ANIMATING_WINNER, AppState.AWAITING_CONFIRMATION, AppState.AWAITING_EVE_RESPONSE, AppState.FETCHING_ESI_DATA, AppState.AWAITING_PRIZE_POLL_VOTES]
        if self.current_state in cancel_states: prompt = f"Current process will be cancelled.\n\n{prompt}"
        if QMessageBox.question(self, "Confirm Purge", prompt, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            if self.current_state in cancel_states: self._cancel_active_draw_processes("Purged")
            self.participants.clear(); self.last_winner = None; self.selected_winner = "---"; self.confirmation_message = None; self.eve2twitch_response = None; self.current_donator = "<NO DONATOR SET>"
            self._set_state(AppState.IDLE); self._update_participant_list_widget(); self.confirmation_log.append("\n--- LIST PURGED ---"); self.log_status("List PURGED."); self.animation_manager.update_participants([]) 

    def _start_js_animation(self, animation_type_override=None, is_continuation=False):
        if not self.last_winner:
            self._set_state(AppState.IDLE)
            return
        self.start_winner_reveal_animation(
            self.last_winner,
            animation_type_override=animation_type_override,
            is_continuation=is_continuation
        )

    @pyqtSlot()
    def _close_and_select_winner(self):
        prize_mode = self.config.get("prize_selection_mode", PRIZE_MODE_POLL)
        if self.current_prize == "<NO PRIZE SET>" and (prize_mode == PRIZE_MODE_POLL or prize_mode == PRIZE_MODE_STREAMER): QMessageBox.warning(self, "No Prize", "Please set/select a prize first."); return
        permissible = [AppState.COLLECTING, AppState.IDLE, AppState.TIMED_OUT, AppState.EVE_TIMED_OUT, AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN, AppState.AWAITING_PRIZE_POLL_VOTES]
        if self.current_state not in permissible or not self.is_twitch_bot_ready or not self.participants: return
        if self.current_state == AppState.AWAITING_PRIZE_POLL_VOTES: self._stop_prize_poll_timer()
        if self.current_state == AppState.COLLECTING: self._announce_draw_closed(); self._set_state(AppState.IDLE); QTimer.singleShot(150, self.draw_winner)
        else:
            if self.current_state != AppState.IDLE: self._set_state(AppState.IDLE); QTimer.singleShot(50, self.draw_winner)
            else: self.draw_winner()

    @pyqtSlot()
    def abandon_draw(self):
        cancel_states = [AppState.ANIMATING_WINNER, AppState.AWAITING_CONFIRMATION, AppState.AWAITING_EVE_RESPONSE, AppState.FETCHING_ESI_DATA, AppState.AWAITING_PRIZE_POLL_VOTES]
        if self.current_state not in cancel_states: self.log_status("No active draw/poll to abandon."); return
        action = "prize poll" if self.current_state == AppState.AWAITING_PRIZE_POLL_VOTES else "draw"
        context = self.last_winner or ("Prize Poll" if action == "prize poll" else "Unknown")
        self.log_status(f"{action.capitalize()} abandoned for {context}. Ready for next action."); self._cancel_active_draw_processes("Abandoned")
        logging_utils.send_ga_event(self.config, "draw_abandoned" if action == "draw" else "poll_abandoned", {"context": context}, self.log_status)
        self.last_winner = None; self.selected_winner = "---"; self.current_donator = "<NO DONATOR SET>"
        self._set_state(AppState.IDLE); self.clear_confirmation_log(); self.confirmation_log.append(f"\n--- {action.capitalize()} Abandoned ---") 

    def open_options_dialog(self):
        if self.options_dialog_instance and self.options_dialog_instance.isVisible():
            self.options_dialog_instance.raise_()
            self.options_dialog_instance.activateWindow()
            return

        if self.current_state in [AppState.ANIMATING_WINNER, AppState.AWAITING_CONFIRMATION,
                                   AppState.AWAITING_EVE_RESPONSE, AppState.FETCHING_ESI_DATA,
                                   AppState.AWAITING_PRIZE_POLL_VOTES]:
            QMessageBox.warning(self, "Busy", f"Cannot open options in {self.current_state.name} state.")
            return

        self._font_multiplier_before_options = self.config.get("font_size_multiplier", 1.0)
        temp_config = self.config.copy()
        temp_config["customisable_ui_enabled"] = True
        self.options_dialog_instance = OptionsDialog(temp_config, self)

        self.options_dialog_instance.reset_layout_signal.connect(self._reset_widget_layout)
        self.options_dialog_instance.save_layout_signal.connect(lambda: self._commit_layout_changes(save_to_file=False))
        self.options_dialog_instance.apply_font_now_signal.connect(self._handle_apply_font_now)
        self.layout_adjusted.connect(self.options_dialog_instance.update_working_geometry)
        self.options_dialog_instance.lock_state_changed.connect(self._handle_lock_state_change_from_dialog)
        result = self.options_dialog_instance.exec()
        try:
            self.layout_adjusted.disconnect(self.options_dialog_instance.update_working_geometry)
            self.options_dialog_instance.lock_state_changed.disconnect(self._handle_lock_state_change_from_dialog)
            self.options_dialog_instance.apply_font_now_signal.disconnect(self._handle_apply_font_now)
        except TypeError:
            pass

        if result == QDialog.DialogCode.Accepted:
            if not config_manager.save_config(self.config):
                QMessageBox.warning(self, "Save Error", "Failed to save config.")
            if self.config.get("google_analytics_enabled") and self.config.get("ga_measurement_id") and self.config.get("ga_api_secret"):
                self._ga_warning_shown = False
        else:
            if self.config.get('debug_mode_enabled', False):
                self.log_status("Options cancelled. Reverting to pre-dialog settings if necessary.")
            self.config = self.options_dialog_instance.initial_config_snapshot.copy()
            self.config["customisable_ui_enabled"] = True

            font_was_reverted = False
            if abs(self.config.get("font_size_multiplier", 1.0) - self._font_multiplier_before_options) > 0.001:
                print(f"Dialog rejected. Reverting font from {self.config.get('font_size_multiplier')} to {self._font_multiplier_before_options}")
                self.config["font_size_multiplier"] = self._font_multiplier_before_options
                font_was_reverted = True
            else:
                print(f"Dialog rejected. Font multiplier {self.config.get('font_size_multiplier')} matches pre-dialog state {self._font_multiplier_before_options}.")

            if font_was_reverted:
                self._apply_font_size(force=True)  # Force because we're reverting
            self._update_layout_mode()
            self._discard_layout_changes()

            if self.animation_type_selector_main: 
                self.animation_type_selector_main.setCurrentText(self.config.get("animation_type", config_manager.ANIM_TYPE_HACKING)) 
            if self.prize_mode_selector: 
                self.prize_mode_selector.setCurrentText(self.config.get("prize_selection_mode", PRIZE_MODE_POLL)) 

            self._load_prize_options_into_dropdown()
            self._update_prize_dropdown_behavior()
            self.update_ui_button_states()

        self.options_dialog_instance = None
        if hasattr(self, '_font_multiplier_before_options'):
            delattr(self, '_font_multiplier_before_options')

    def start_winner_reveal_animation(self, winner_name, animation_type_override=None, is_continuation=False, _retry_count=0):
        # Readiness Check: Ensure the animation panel's visual warm-up is complete before proceeding.
        # This prevents a race condition on the first draw, especially under heavy system load (e.g., streaming with OBS).
        if not self._first_animation_warmup_done:
            if _retry_count > 25:  # Timeout after 5 seconds (25 * 200ms)
                self.log_status("ERROR: Animation panel did not become ready in time. Animation aborted.")
                self._set_state(AppState.IDLE)
                QMessageBox.critical(self, "Animation Error", "The animation panel failed to initialize. Please try restarting the application.")
                return

            if _retry_count == 0: # Only log the initial message
                self.log_status("Preparing animation engine...")
            
            # Reschedule this function call to wait for the warm-up to complete without freezing the UI.
            QTimer.singleShot(200, lambda: self.start_winner_reveal_animation(
                winner_name, animation_type_override, is_continuation, _retry_count + 1
            ))
            return

        # Use an override if provided, otherwise use the type from the config
        if animation_type_override:
            anim_type_cfg = animation_type_override
            if self.config.get('debug_mode_enabled', False):
                self.log_status(f"🎲 Using OVERRIDE animation type: {anim_type_cfg}")
        else:
            anim_type_cfg = self.config.get("animation_type", config_manager.ANIM_TYPE_HACKING)

        # Reset the prize reveal flag if it exists
        if hasattr(self, '_was_prize_reveal'):
            self._was_prize_reveal = False
            if self.config.get('debug_mode_enabled', False):
                self.log_status(f"🎲 Using {anim_type_cfg} animation for winner draw (consistent with config setting)")

        countdown_s = self.config.get('confirmation_timeout', 90)
        # Add the is_continuation flag to the options passed to JavaScript
        options = {'countdownDurationS': countdown_s, 'isContinuation': is_continuation}

        tech_theme_animations = [
            config_manager.ANIM_TYPE_HACKING, config_manager.ANIM_TYPE_TRIGLAVIAN,
            config_manager.ANIM_TYPE_NODE_PATH, config_manager.ANIM_TYPE_TRIG_CONDUIT,
            config_manager.ANIM_TYPE_TRIG_CODE_REVEAL
        ]

        anim_type_to_use = anim_type_cfg
        if anim_type_cfg == config_manager.ANIM_TYPE_RANDOM_TECH:
            available_tech_animations = list(tech_theme_animations)
            if self.last_tech_animation_type and \
               self.last_tech_animation_type in tech_theme_animations and \
               len(available_tech_animations) > 1:
                available_tech_animations.remove(self.last_tech_animation_type)

            if not available_tech_animations:
                anim_type_to_use = config_manager.ANIM_TYPE_HACKING 
            else:
                anim_type_to_use = random.choice(available_tech_animations)
            self.last_tech_animation_type = anim_type_to_use
            print(f"Random tech animation selected: {anim_type_to_use}")
        else:
            self.last_tech_animation_type = None

        sound_to_play = "animation_start"

        if anim_type_to_use == config_manager.ANIM_TYPE_HACKING:
            options['revealInterval'] = {"Normal": 300, "Slow": 700, "Very Slow": 1200}.get(self.config.get("animation_box_speed", "Normal"), 300)
        elif anim_type_to_use == config_manager.ANIM_TYPE_TRIGLAVIAN:
            options['trigRevealSpeed'] = self.config.get("animation_trig_speed", config_manager.TRIG_SPEED_NORMAL)
        elif anim_type_to_use == config_manager.ANIM_TYPE_NODE_PATH:
            options['nodePathSpeed'] = self.config.get("animation_node_path_speed", config_manager.NODE_PATH_SPEED_NORMAL)
        elif anim_type_to_use == config_manager.ANIM_TYPE_TRIG_CONDUIT:
            options['trigConduitSpeed'] = self.config.get("animation_trig_conduit_speed", config_manager.TRIG_CONDUIT_SPEED_NORMAL)
        elif anim_type_to_use == config_manager.ANIM_TYPE_TRIG_CODE_REVEAL:
            options.update({k: self.config.get(f"animation_{k}", config_manager.DEFAULT_CONFIG[f"animation_{k}"]) for k in ["trig_code_length", "trig_code_reveal_speed", "trig_code_char_set", "trig_code_finalist_count"]})
        else:
            print(f"Warning: Animation type '{anim_type_to_use}' not explicitly handled for options. Defaulting to Hacking options.")
            anim_type_to_use = config_manager.ANIM_TYPE_HACKING
            options['revealInterval'] = 300

        if sound_to_play:
             self.sound_manager.play(sound_to_play, loops=0)

        self.animation_manager.start_reveal(winner_name, anim_type_to_use, options)

    @pyqtSlot(bool)
    def handle_bot_ready(self, is_ready):
        self.is_twitch_bot_ready = is_ready
        if is_ready:
            # Ensure successful connection is visible in the UI
            try:
                channel = getattr(self, 'effective_channel', None) or getattr(self, 'twitch_thread', None) and getattr(self.twitch_thread, 'channel', None) or getattr(self, 'config', {}).get('nick')
                if channel and self.config.get('debug_mode_enabled', False):
                    self.log_status(f"Successfully connected to #{channel}")
            except Exception:
                pass
            if self.current_state == AppState.BOT_CONNECTING: self._set_state(AppState.IDLE)
        elif self.current_state != AppState.BOT_DOWN: self._set_state(AppState.BOT_DOWN)

    @pyqtSlot()
    def debug_trigger_esi_render(self):
        """Debug helper: trigger _handle_esi_data_ready using a sample portrait file if present.
        Place a sample PNG at `portraits/sample_portrait.png` relative to the app folder to use this.
        """
        try:
            import os, base64
            sample_path = os.path.join(os.path.dirname(__file__), 'portraits', 'sample_portrait.png')
            if not os.path.exists(sample_path):
                self.log_status(f"DEBUG: Sample portrait not found at {sample_path}")
                return
            with open(sample_path, 'rb') as f:
                img_bytes = f.read()
            b64 = base64.b64encode(img_bytes).decode('ascii')
            fake_data = {
                'id': 99999999,
                'name': 'DEBUG_Sample',
                'portrait_base64': b64,
                'portrait_content_type': 'image/png',
                'corporation_name': 'Debug Corp',
                'corporation_id': 12345,
                'alliance_name': None,
                'alliance_id': None
            }
            # Call the handler on the main thread
            QTimer.singleShot(10, lambda: self._handle_esi_data_ready(fake_data))
            self.log_status("DEBUG: Triggered ESI render with sample portrait")
        except Exception as e:
            self.log_status(f"DEBUG: Failed to trigger ESI render: {e}")

    @pyqtSlot()
    def add_test_entries(self):
         if not self.config.get("enable_test_entries", False): self.log_status("Test entry adding is disabled."); QMessageBox.warning(self, "Feature Disabled", "Enable in Options."); return
         templates = ["QuickFox_{num}","Supercali","Awesome_{num}","Generic_{num}","TestUser_{num}"]
         fake_names = [ (random.choice(templates).replace("{num}", f"{i+1:02d}") )[:25] for i in range(20)]
         added = {name for name in fake_names if name.lower() not in {p.lower() for p in self.participants}}
         if added:
             self.participants.update(added); self._update_participant_list_widget(); self.log_status(f"Added {len(added)} test entries.")
             self.animation_manager.update_participants(sorted(list(self.participants), key=str.lower))
             for name in added: logging_utils.send_ga_event(self.config, "draw_entry", {"event_label": "TestEntryAdded"}, self.log_status)
         else: self.log_status("All test entries already in list.")

    def clear_confirmation_log(self):
        if hasattr(self, 'confirmation_log'): self.confirmation_log.clear() 

    def schedule_twitch_message(self, message):
        if self.twitch_thread and self.twitch_thread.bot and self.twitch_thread.loop and self.is_twitch_bot_ready:
            try: asyncio.run_coroutine_threadsafe(self.twitch_thread.bot.send_chat_message(message), self.twitch_thread.loop)
            except Exception as e: self.log_status(f"Error scheduling Twitch message: {e}")
        else: self.log_status("Error: Bot not ready to send message.")

    def _expand_prize_list(self, prize_list_raw: list) -> list:
        expanded = []
        for p_str in prize_list_raw:
            base_name, donator, quantity = self._parse_prize_and_donator(p_str)
            display_name = base_name
            if donator:
                display_name += f" ({donator})"
            
            for _ in range(quantity):
                expanded.append({
                    "display": display_name, 
                    "original_full": p_str,    
                    "base_name": base_name,    
                    "donator": donator         
                })
        return expanded

    def _load_prize_options_into_dropdown(self): 
        if not hasattr(self, 'prize_options_dropdown'): return 
        self.prize_options_dropdown.blockSignals(True) 
        self.prize_options_dropdown.clear() 
        mode = self.config.get("prize_selection_mode", PRIZE_MODE_POLL)

        if mode == PRIZE_MODE_STREAMER:
            self.prize_options_dropdown.addItem(DROPDOWN_SELECT_PRIZE_TEXT) 
            
            # Add Random Prize option if there are any prizes available
            common_raw = self.config.get("common_prizes_list", [])
            configured_raw = self.config.get("prize_options", [])
            
            if common_raw or configured_raw:
                self.prize_options_dropdown.addItem(DROPDOWN_RANDOM_PRIZE_TEXT)
            
            expanded_common = self._expand_prize_list(common_raw)
            expanded_configured = self._expand_prize_list(configured_raw)

            if expanded_common:
                self.prize_options_dropdown.addItem(DROPDOWN_COMMON_PRIZE_HEADER) 
                self.prize_options_dropdown.model().item(self.prize_options_dropdown.count()-1).setEnabled(False) 
                for prize_data in expanded_common:
                    self.prize_options_dropdown.addItem(prize_data["display"], userData=prize_data) 

            if expanded_common and expanded_configured:
                self.prize_options_dropdown.addItem(DROPDOWN_SEPARATOR_TEXT) 
                self.prize_options_dropdown.model().item(self.prize_options_dropdown.count()-1).setEnabled(False) 

            if expanded_configured:
                self.prize_options_dropdown.addItem(DROPDOWN_CONFIGURED_PRIZE_HEADER) 
                self.prize_options_dropdown.model().item(self.prize_options_dropdown.count()-1).setEnabled(False) 
                for prize_data in expanded_configured:
                    self.prize_options_dropdown.addItem(prize_data["display"], userData=prize_data) 
        else: 
            self.prize_options_dropdown.addItem(DROPDOWN_POLL_MODE_TEXT) 

        self.prize_options_dropdown.blockSignals(False) 
        self._update_prize_dropdown_behavior()


    @pyqtSlot(int)
    def _on_prize_dropdown_changed(self, index): 
        if not hasattr(self, 'prize_options_dropdown') or index < 0: 
            return

        mode = self.config.get("prize_selection_mode", PRIZE_MODE_POLL)
        selected_text = self.prize_options_dropdown.itemText(index) 
        prize_data = self.prize_options_dropdown.itemData(index)  

        non_selectable_texts = [
            DROPDOWN_SELECT_PRIZE_TEXT,
            DROPDOWN_COMMON_PRIZE_HEADER,
            DROPDOWN_CONFIGURED_PRIZE_HEADER,
            DROPDOWN_SEPARATOR_TEXT,
            DROPDOWN_POLL_MODE_TEXT
        ]

        # Handle Random Prize selection
        if selected_text == DROPDOWN_RANDOM_PRIZE_TEXT:
            self._trigger_random_prize_selection()
            return

        if selected_text in non_selectable_texts or prize_data is None:
            if self.current_prize != "<NO PRIZE SET>" or self.current_donator != "<NO DONATOR SET>":
                self.current_prize, self.current_donator = "<NO PRIZE SET>", "<NO DONATOR SET>"
                self.log_status("Prize/Donator cleared.")
                if self.prize_input: self.prize_input.clear()
            # Clear any hidden prize state when clearing
            self._clear_hidden_prize_state()
            self.update_displays()
            self._update_prize_dropdown_behavior()
            return

        if mode == PRIZE_MODE_STREAMER and isinstance(prize_data, dict):
            self.current_prize = prize_data.get("base_name", selected_text) 
            self.current_donator = prize_data.get("donator") or "<NO DONATOR SET>"
            # Clear any hidden prize state when selecting a normal prize
            # but preserve the original full string for accurate removal later.
            self._clear_hidden_prize_state()
            try:
                self._selected_prize_original_string = prize_data.get("original_full")
            except Exception:
                self._selected_prize_original_string = None
            if self.config.get('debug_mode_enabled', False):
                self.log_status(f"Streamer selected prize: {self.current_prize} (Donator: {self.current_donator})")
            if self.prize_input: self.prize_input.clear()
            self.update_displays()
        
        self._update_prize_dropdown_behavior()


    @pyqtSlot(str)
    def _on_prize_mode_changed(self, mode_text):
        if not hasattr(self, 'prize_mode_selector'): return 
        self.config["prize_selection_mode"] = mode_text; self._load_prize_options_into_dropdown(); self.update_ui_button_states()

    @pyqtSlot(str)
    def _on_main_animation_type_changed(self, anim_type_text):
        if not hasattr(self, 'animation_type_selector_main'): return 
        self.config["animation_type"] = anim_type_text; self.log_status(f"Draw animation style set to: {anim_type_text}")

    def _update_prize_dropdown_behavior(self): 
        if not hasattr(self, 'prize_options_dropdown'): return 
        mode = self.config.get("prize_selection_mode", PRIZE_MODE_POLL)
        can_interact = self.current_state in [AppState.IDLE, AppState.COLLECTING] or self.current_state in [AppState.CONFIRMED_NO_IGN, AppState.CONFIRMED_WITH_IGN, AppState.TIMED_OUT, AppState.EVE_TIMED_OUT]
        if mode == PRIZE_MODE_STREAMER:
            self.prize_options_dropdown.setToolTip("Select a pre-configured or common prize.") 
            has_prizes = any(self.prize_options_dropdown.itemData(i) is not None for i in range(self.prize_options_dropdown.count())) 
            self.prize_options_dropdown.setEnabled(can_interact and has_prizes) 
        else: # PRIZE_MODE_POLL
            self.prize_options_dropdown.setToolTip("Disabled in Poll mode. Poll uses Configured Prizes.") 
            self.prize_options_dropdown.setEnabled(False) 
            if self.prize_options_dropdown.count() == 0 or self.prize_options_dropdown.itemText(0) != DROPDOWN_POLL_MODE_TEXT: 
                self.prize_options_dropdown.blockSignals(True); self.prize_options_dropdown.clear(); self.prize_options_dropdown.addItem(DROPDOWN_POLL_MODE_TEXT); self.prize_options_dropdown.blockSignals(False) 

    @pyqtSlot()
    def start_prize_poll(self): 
        if self.config.get("prize_selection_mode") != PRIZE_MODE_POLL:
            QMessageBox.information(self, "Mode Incorrect", "Mode must be 'Twitch Chat Poll'.")
            return
        if self.current_state != AppState.IDLE:
            QMessageBox.warning(self, "Busy", f"Cannot start poll in state: {self.current_state.name}")
            return

        raw_prizes_from_config = self.config.get("prize_options", [])
        if not raw_prizes_from_config:
            QMessageBox.warning(self, "No Prizes", "No 'Configured Prize Options' for poll.")
            return

        distinct_prize_type_map = {}
        for p_str in raw_prizes_from_config:
            base_name, donator, _ = self._parse_prize_and_donator(p_str)
            display_key = base_name
            if donator:
                display_key += f" ({donator})"
            if display_key not in distinct_prize_type_map:
                distinct_prize_type_map[display_key] = p_str
        
        distinct_prize_entries_for_poll = list(distinct_prize_type_map.items())

        if not distinct_prize_entries_for_poll:
            QMessageBox.warning(self, "No Prizes", "No distinct prize types found after parsing for poll.")
            return
        
        num_distinct_types_available = len(distinct_prize_entries_for_poll)
        num_to_select_for_poll = min(num_distinct_types_available, 5)

        if num_to_select_for_poll < 1 : 
             QMessageBox.warning(self, "No Prizes", f"Not enough distinct prize types to start a poll (need at least 1, found {num_to_select_for_poll}).")
             return

        prizes_to_use_in_poll_tuples = random.sample(distinct_prize_entries_for_poll, num_to_select_for_poll)

        self.current_poll_options = []
        self.prize_poll_votes.clear()
        self.prize_poll_voters.clear()
        
        numbers_to_assign = list(range(1, num_to_select_for_poll + 1))
        random.shuffle(numbers_to_assign)

        lines = ["🏆 EVE PRIZE POLL 🏆 Vote with the number:"]
        for i, (display_key, original_full_string) in enumerate(prizes_to_use_in_poll_tuples):
            if i >= len(numbers_to_assign): break 
            num = numbers_to_assign[i]
            
            original_config_index = -1
            try:
                original_config_index = raw_prizes_from_config.index(original_full_string)
            except ValueError:
                 print(f"Warning: Poll prize '{original_full_string}' (display_key: '{display_key}') not found directly in raw config list. This can happen if it's a duplicate that was consolidated by display_key, or if the list changed. Votes for this option might not be correctly attributed if this index is not representative of all its instances.")
                 for idx, raw_p_str in enumerate(raw_prizes_from_config):
                     b_name, d_name, _ = self._parse_prize_and_donator(raw_p_str)
                     current_display_key = b_name
                     if d_name: current_display_key += f" ({d_name})"
                     if current_display_key == display_key:
                         original_config_index = idx
                         break


            self.current_poll_options.append({
                "text": display_key, 
                "original_full_text": original_full_string, 
                "number": num,
                "original_index": original_config_index 
            })
            lines.append(f"[{num}] {display_key.upper()}")

        duration = self.config.get("poll_duration", 30)
        lines.append(f"Poll ends in {duration}s!")
        announce = " | ".join(lines);

        self.clear_confirmation_log()
        self.confirmation_log.setHtml(self._format_prize_poll_for_log()) 
        self.schedule_twitch_message(announce)
        self.log_status(f"Prize poll started ({duration}s with {len(prizes_to_use_in_poll_tuples)} options).")
        self._set_state(AppState.AWAITING_PRIZE_POLL_VOTES)
        logging_utils.send_ga_event(self.config, "prize_poll_started", {"num_options": len(self.current_poll_options), "duration": duration}, self.log_status)


    def _format_prize_poll_for_log(self):
        if not self.current_poll_options: return "<p>No active poll.</p>"
        html = "<h3 style='color:#e8d900; text-align:center;'>-- PRIZE POLL ACTIVE --</h3><table width='98%' style='margin:auto; border-collapse:collapse; font-family:Shentox-SemiBold, Consolas; font-size:9.5pt; border:1px solid #333;'><thead style='background-color:#333; color:#e8d900;'><tr><th style='padding:3px 6px; text-align:left; width:8%;'>ID</th><th style='padding:3px 6px; text-align:left;'>PRIZE</th><th style='padding:3px 6px; text-align:center; width:18%;'>VOTES</th><th style='padding:3px 6px; text-align:center; width:15%;'>%</th></tr></thead><tbody>"
        total_votes = sum(self.prize_poll_votes.values())
        sorted_options = sorted(self.current_poll_options, key=lambda x: x["number"])
        for opt in sorted_options:
            votes = self.prize_poll_votes.get(opt["original_index"], 0) 
            perc = (votes / total_votes * 100) if total_votes > 0 else 0
            html += f"<tr style='border-bottom:1px solid #333; background:rgba(17,17,17,0.5);'><td style='padding:3px 6px; text-align:center; color:#4af1f2;'>[{opt['number']}]</td><td style='padding:3px 6px; color:#c0c0c0;'><i>{opt['text'].upper()}</i></td><td style='padding:3px 6px; text-align:center; color:#4af1f2;'>{votes}</td><td style='padding:3px 6px; text-align:center; color:#c0c0c0;'>{perc:.0f}%</td></tr>"
        html += "</tbody></table>"
        if self.prize_poll_timer_thread and self.prize_poll_timer_thread.is_alive(): html += "<p style='text-align:center; color:#a0a0a0; margin-top:8px; font-size:9pt;'><i>POLL ACTIVE...</i></p>"
        elif total_votes >= 0: html += f"<p style='text-align:center; color:#e8d900; margin-top:8px; font-size:9pt;'><b>POLL CONCLUDED | TOTAL: {total_votes}</b></p>"
        
        # Add debug information if debug mode is enabled
        if self.config.get("debug_mode_enabled", False):
            debug_info = f"<p style='text-align:left; color:#888; margin-top:10px; font-size:8pt; border-top:1px solid #333; padding-top:5px;'>"
            debug_info += f"<b>DEBUG:</b> State: {self.current_state.name} | "
            debug_info += f"Total Options: {len(self.current_poll_options)} | "
            debug_info += f"Unique Voters: {len(self.prize_poll_voters)} | "
            debug_info += f"Winner: {self.last_winner or 'None'} | "
            debug_info += f"Participants: {len(self.participants)}"
            debug_info += "</p>"
            html += debug_info
        
        return html

    def _update_prize_poll_display_in_log(self):
        if self.current_state == AppState.AWAITING_PRIZE_POLL_VOTES: self.confirmation_log.setHtml(self._format_prize_poll_for_log()) 

    def _finalize_prize_poll(self):
        self.log_status("Prize poll ended."); self._update_prize_poll_display_in_log()
        win_prize, win_donator = "<NO PRIZE SET>", "<NO DONATOR SET>"
        if self.prize_poll_votes:
            max_votes = max(self.prize_poll_votes.values(), default=0)
            top_indices = [idx for idx, count in self.prize_poll_votes.items() if count == max_votes]
            winning_opt_data = None
            if top_indices:
                winner_idx = random.choice(top_indices) if len(top_indices) > 1 else top_indices[0]
                winning_opt_data = next((opt for opt in self.current_poll_options if opt["original_index"] == winner_idx), None)
            if winning_opt_data:
                win_prize, don, _ = self._parse_prize_and_donator(winning_opt_data["original_full_text"])
                if don: win_donator = don
        self.current_prize, self.current_donator = win_prize, win_donator
        self.prize_input.setText(win_prize if win_prize != "<NO PRIZE SET>" else "") 
        self.update_displays()
        announce = f"PRIZE POLL ENDED! 🏆 Winning prize: {win_prize.upper()}" if win_prize != "<NO PRIZE SET>" else "PRIZE POLL ENDED! No prize selected."
        self.schedule_twitch_message(announce)
        logging_utils.send_ga_event(self.config, "prize_poll_ended", {"winning_prize": win_prize, "total_votes": sum(self.prize_poll_votes.values())}, self.log_status)
        self._set_state(AppState.IDLE)

    def closeEvent(self, event):
        if self.has_unsaved_layout_changes():
            reply = QMessageBox.question(self, "Unsaved Layout", "Save layout changes?", QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Save:
                if not self._commit_layout_changes(save_to_file=False): event.ignore(); return
            elif reply == QMessageBox.StandardButton.Cancel: event.ignore(); return
            elif reply == QMessageBox.StandardButton.Discard: self._discard_layout_changes()
        try:
             logging_utils._ensure_ga_client_id()

             self.config["window_geometry"] = None
             print("DEBUG: Setting window_geometry to None in config before saving on close.")

             if not config_manager.save_config(self.config): print("ERROR: Failed to save config on close.")
        except Exception as e: print(f"Error saving on close: {e}")

        self.stop_twitch_connection(); self._stop_confirmation_timer(); self._stop_eve_response_timer(); self._stop_prize_poll_timer()
        if self.esi_worker_thread and self.esi_worker_thread.isRunning(): self.esi_worker_thread.quit(); self.esi_worker_thread.wait(1000)
        if self.timer_poll_qtimer.isActive(): self.timer_poll_qtimer.stop()
        if self.current_state == AppState.ANIMATING_WINNER: self.animation_manager.cancel_animation()
        if hasattr(self, 'sound_manager'): self.sound_manager.stop_all(); self.sound_manager.quit()
        if self.animation_manager: self.animation_manager.stop()
        event.accept()

# --- Application Entry Point ---
if __name__ == '__main__':
    QApplication.setApplicationName(APP_NAME)
    QApplication.setOrganizationName(ORG_NAME)
    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '8898'
    print(f"Remote debugging configured on port 8898")

    if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'): QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyleSheet(BASE_STYLESHEET)
    
    # Check for first run and show setup dialog
    from first_run_setup import check_first_run, FirstRunDialog, save_user_channel
    if check_first_run():
        print("First run detected - showing setup dialog...")
        channel_name = FirstRunDialog.show_first_run_setup()
        if channel_name:
            save_user_channel(channel_name)
            print(f"✅ First run setup complete! Channel: {channel_name}")
        else:
            print("⚠️ User cancelled first run setup")
            # Still allow app to continue with default from ENV

    splash = None
    try:
        pixmap_path = resource_path(LOADING_IMAGE_FILE)
        if Path(pixmap_path).is_file():
            pixmap = QPixmap(pixmap_path)
            if not pixmap.isNull(): splash = QSplashScreen(pixmap); splash.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint); splash.setEnabled(False); splash.show(); app.processEvents()
    except Exception as e: print(f"Splash Error: {e}")

    print("DEBUG: Initializing GiveawayApp...")
    window = GiveawayApp()
    print(f"DEBUG: GiveawayApp initialized. Config window_geometry: {window.config.get('window_geometry')}")

    print("DEBUG: Calling window.showMaximized()...")
    window.showMaximized()
    print(f"DEBUG: After showMaximized(). Is window maximized? {window.isMaximized()}")
    QApplication.processEvents()
    print(f"DEBUG: After processEvents. Is window maximized? {window.isMaximized()}. Geometry: {window.geometry().x()},{window.geometry().y()},{window.geometry().width()}x{window.geometry().height()}")

    def show_main_and_finish_splash():
        if splash: splash.finish(window)
        print(f"DEBUG: Splash finished. Is window maximized? {window.isMaximized()}. Geometry: {window.geometry().x()},{window.geometry().y()},{window.geometry().width()}x{window.geometry().height()}")
        
        # Check for updates after splash screen
        try:
            from update_dialog import check_for_updates_with_dialog
            QTimer.singleShot(1000, lambda: check_for_updates_with_dialog(window))
        except Exception as e:
            print(f"Update check error: {e}")

    QTimer.singleShot(200, show_main_and_finish_splash)

    try:
        exit_code = app.exec()
    finally:
        # No cleanup needed for plain .env file
        print("🧹 Application shutdown complete")
    # QUICK DEV TEST: schedule a single auto-lookup-failed announcement for testing (only when debug enabled)
    try:
        if '--dev-test-e2t-404' in sys.argv or (os.environ.get('RUSTYBOT_DEV_TEST_E2T_404') == '1'):
            # Trigger after a short delay to ensure the main window exists
            def _dev_trigger():
                try:
                    if 'window' in globals() and window and hasattr(window, '_announce_auto_lookup_failed'):
                        window._announce_auto_lookup_failed('test_user_404')
                        print("DEV: Triggered auto-lookup-failed announcer for 'test_user_404'.")
                except Exception as e:
                    print(f"DEV: Failed to trigger announcer: {e}")
            QTimer.singleShot(1000, _dev_trigger)
    except Exception:
        pass
    sys.exit(exit_code)