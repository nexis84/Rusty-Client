# raw_irc_test.py
import socket
import os
from dotenv import load_dotenv

print("--- Starting Raw IRC Connection Test ---")
load_dotenv()

# --- Credentials ---
# Ensure your .env file is correct before running this!
TOKEN = os.getenv("TWITCH_TOKEN")
NICK = os.getenv("TWITCH_NICK").lower() # IRC nicks should be lowercase
CHANNEL = os.getenv("TWITCH_CHANNEL").lower()

# --- Twitch IRC Server Details ---
HOST = "irc.chat.twitch.tv"
PORT = 6667

# --- Create and connect the socket ---
s = None
try:
    print(f"Connecting to {HOST}:{PORT}...")
    s = socket.socket()
    s.connect((HOST, PORT))
    print("Socket connected. Authenticating...")

    # --- Send authentication details to Twitch ---
    # These messages must be encoded to bytes and end with \r\n
    s.send(f"PASS {TOKEN}\r\n".encode('utf-8'))
    s.send(f"NICK {NICK}\r\n".encode('utf-8'))
    s.send(f"JOIN #{CHANNEL}\r\n".encode('utf-8'))
    print(f"Sent PASS, NICK, and JOIN commands for '{NICK}' in '#{CHANNEL}'.")
    print("--- Now listening for a response from Twitch... ---")

    # --- Listen for the server's response ---
    while True:
        response = s.recv(2048).decode('utf-8')

        # If we don't get a response, the connection was likely closed.
        if not response:
            print("\n[FAILURE] Connection closed by Twitch. Authentication likely failed.")
            break

        # Twitch will send PING messages; we must reply with PONG or be disconnected.
        if response.startswith("PING"):
            s.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
            print("> Received PING, sent PONG.")
            continue

        # Print any useful messages from the server
        for line in response.splitlines():
            print(f"> {line}")
            # The official "Welcome" message means we are successfully connected.
            if "Welcome, GLHF!" in line:
                print("\n" + "="*50)
                print("  SUCCESS! Raw IRC connection was successful.")
                print("  Your credentials and account settings are correct.")
                print("="*50 + "\n")
                s.send(f"PRIVMSG #{CHANNEL} :Raw IRC connection test successful!\r\n".encode('utf-8'))
                break
            # The official "Login failed" message.
            if "Login authentication failed" in line:
                print("\n" + "!"*50)
                print("  FAILURE! Raw IRC connection failed.")
                print("  Twitch explicitly rejected your credentials.")
                print("!"*50 + "\n")
                break
        
        # If we got a success or fail message, stop listening.
        if "Welcome, GLHF!" in response or "Login authentication failed" in response:
            break

except Exception as e:
    print(f"\n[CRITICAL ERROR] An error occurred during the connection attempt: {e}")
    traceback.print_exc()

finally:
    if s:
        print("--- Closing socket. ---")
        s.close()