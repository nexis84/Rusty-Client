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
    from pathlib import Path
    from dotenv import load_dotenv
    import json
    from enum import Enum, auto
    from datetime import datetime
    import uuid
    from collections import Counter
    
    # --- Project Imports ---
    import config_manager
    import requests
    import base64
    
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
        VALID_DRAW_SPEEDS
    )
    
    # --- PyQt6 Imports Continued ---
    from PyQt6.QtCore import (
        QObject, pyqtSignal, QTimer, QSettings, Qt,
        QPoint, QSize, QUrl, QThread, QStandardPaths
    )
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
        QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox,
        QGroupBox, QHBoxLayout, QListWidget, QListWidgetItem,
        QLabel, QSpinBox, QFileDialog, QSplashScreen,
        QMenuBar, QMenu, QToolBar, QStatusBar,
        QMessageBox, QDoubleSpinBox
    )
    from PyQt6.QtGui import QPixmap, QMovie, QDesktopServices, QIcon, QFont, QFontDatabase, QColor
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    
    # --- Twitch Imports ---
    import twitchio
    from twitchio.ext import commands
    
    # The 'Message' class is now part of the commands extension's Context.
    # We no longer need to import it directly from twitchio
    # The `ctx` object in event handlers provides access to the message.
    
    
    # --- Bot Class and Main Application ---
    
    class TwitchBot(commands.Bot):
        # This is where your Twitch bot's logic will be
        def __init__(self, token, prefix, initial_channels, main_app_instance):
            self.main_app = main_app_instance
            super().__init__(token=token, prefix=prefix, initial_channels=initial_channels)
    
        async def event_ready(self):
            print(f'Bot is logged in as {self.nick}')
            print(f'User ID: {self.user_id}')
            # You can now send a message to a channel here if you want, for example:
            # await self.connected_channels[0].send("RustyBot is now online!")
    
        async def event_message(self, ctx):
            # This is the event handler for incoming messages.
            # `ctx` is a Context object, which contains the message.
            if ctx.author.name.lower() == self.nick.lower():
                # Ignore messages from the bot itself to prevent loops
                return
            
            message_text = ctx.content
            username = ctx.author.name
            
            print(f'Received message from {username}: {message_text}')
    
            # Now you can send the message to the main application
            self.main_app.bot_signal.emit(f"{username}: {message_text}")
    
            # Process commands if any
            await self.handle_commands(ctx)
    
        @commands.command()
        async def hello(self, ctx: commands.Context):
            await ctx.send(f'Hello {ctx.author.name}!')
    
    
    # A signal class to pass data from the bot thread to the main thread
    class BotSignal(QObject):
        message_received = pyqtSignal(str)
    
    
    class GiveawayApp(QMainWindow):
        # ... (The rest of your existing code for GiveawayApp) ...
    
    