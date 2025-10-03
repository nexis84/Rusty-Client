# -*- coding: utf-8 -*-
"""
IRC Fallback Client for Twitch Chat
Provides a fallback IRC connection when TwitchIO EventSub is not working
"""

import socket
import threading
import time
import re
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtCore import QThread


class TwitchIRCClient(QObject):
    """IRC fallback client for Twitch chat."""
    
    message_received = pyqtSignal(str, str)  # username, message
    connection_status = pyqtSignal(bool)     # connected status
    
    def __init__(self, oauth_token, bot_nick, channel_name, message_callback=None):
        super().__init__()
        self.oauth_token = oauth_token
        self.bot_nick = bot_nick
        self.channel_name = channel_name
        self.message_callback = message_callback
        
        self.socket = None
        self.connected = False
        self.running = False
        self.thread = None
        
        # IRC server details
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        
    def connect(self):
        """Connect to Twitch IRC server."""
        try:
            print(f"🔌 IRC: Connecting to {self.server}:{self.port}")
            
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            
            # Connect to server
            self.socket.connect((self.server, self.port))
            
            # Authenticate
            self.socket.send(f"PASS oauth:{self.oauth_token}\r\n".encode())
            self.socket.send(f"NICK {self.bot_nick}\r\n".encode())
            
            # Join channel
            self.socket.send(f"JOIN #{self.channel_name}\r\n".encode())
            
            # Start listening thread
            self.running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            
            print(f"✅ IRC: Connected to #{self.channel_name}")
            self.connected = True
            self.connection_status.emit(True)
            
            return True
            
        except Exception as e:
            print(f"❌ IRC: Connection failed: {e}")
            self.connected = False
            self.connection_status.emit(False)
            return False
    
    def disconnect(self):
        """Disconnect from IRC server."""
        print("🔌 IRC: Disconnecting...")
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.connection_status.emit(False)
        print("✅ IRC: Disconnected")
    
    def _listen_loop(self):
        """Main listening loop for IRC messages."""
        buffer = ""
        
        try:
            while self.running and self.socket:
                try:
                    # Receive data
                    data = self.socket.recv(2048).decode('utf-8', errors='ignore')
                    if not data:
                        break
                    
                    buffer += data
                    
                    # Process complete lines
                    while '\r\n' in buffer:
                        line, buffer = buffer.split('\r\n', 1)
                        self._process_irc_line(line)
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ IRC: Error in listen loop: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ IRC: Fatal error in listen loop: {e}")
        finally:
            self.running = False
            self.connected = False
            self.connection_status.emit(False)
    
    def _process_irc_line(self, line):
        """Process a single IRC line."""
        try:
            if not line.strip():
                return
            
            # Handle PING messages to stay connected
            if line.startswith('PING'):
                pong_response = line.replace('PING', 'PONG')
                self.socket.send(f"{pong_response}\r\n".encode())
                return
            
            # Parse PRIVMSG (chat messages)
            # Format: :username!username@username.tmi.twitch.tv PRIVMSG #channel :message
            privmsg_match = re.match(r':(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #(\w+) :(.+)', line)
            if privmsg_match:
                username = privmsg_match.group(1)
                channel = privmsg_match.group(2)
                message = privmsg_match.group(3)
                
                # Ignore messages from self
                if username.lower() == self.bot_nick.lower():
                    return
                
                print(f"📨 IRC: {username}: {message}")
                
                # Emit signal
                self.message_received.emit(username, message)
                
                # Call direct callback if provided
                if self.message_callback:
                    try:
                        self.message_callback(username, message)
                    except Exception as e:
                        print(f"❌ IRC: Error in message callback: {e}")
                
        except Exception as e:
            print(f"❌ IRC: Error processing line '{line}': {e}")
    
    def send_message(self, message):
        """Send a message to the channel."""
        try:
            if self.connected and self.socket:
                irc_message = f"PRIVMSG #{self.channel_name} :{message}\r\n"
                self.socket.send(irc_message.encode())
                print(f"✅ IRC: Sent message: {message}")
                return True
            else:
                print("❌ IRC: Cannot send message - not connected")
                return False
        except Exception as e:
            print(f"❌ IRC: Error sending message: {e}")
            return False


class TwitchIRCThread(QThread):
    """Thread wrapper for IRC client."""
    
    message_received = pyqtSignal(str, str)
    connection_status = pyqtSignal(bool)
    
    def __init__(self, oauth_token, bot_nick, channel_name):
        super().__init__()
        self.oauth_token = oauth_token
        self.bot_nick = bot_nick
        self.channel_name = channel_name
        self.irc_client = None
        
    def run(self):
        """Run IRC client in thread."""
        try:
            # Create IRC client
            self.irc_client = TwitchIRCClient(
                oauth_token=self.oauth_token,
                bot_nick=self.bot_nick,
                channel_name=self.channel_name
            )
            
            # Connect signals
            self.irc_client.message_received.connect(self.message_received)
            self.irc_client.connection_status.connect(self.connection_status)
            
            # Connect to IRC
            success = self.irc_client.connect()
            if success:
                # Keep thread alive while connected
                while self.irc_client.running:
                    self.msleep(100)
            
        except Exception as e:
            print(f"❌ IRC Thread: Error: {e}")
        finally:
            if self.irc_client:
                self.irc_client.disconnect()
    
    def stop(self):
        """Stop IRC client."""
        if self.irc_client:
            self.irc_client.disconnect()
        self.quit()
        self.wait()
