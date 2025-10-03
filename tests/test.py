# test_connection.py (Corrected Version)
import os
import asyncio
from dotenv import load_dotenv
from twitchio.ext import commands

print("--- Starting Minimal Connection Test (v2) ---")
load_dotenv()

# Load ALL required credentials from the .env file
token = os.getenv("TWITCH_TOKEN")
nick = os.getenv("TWITCH_NICK")
channel = os.getenv("TWITCH_CHANNEL")
client_id = os.getenv("TWITCH_CLIENT_ID")      # <<< ADDED
client_secret = os.getenv("TWITCH_CLIENT_SECRET")  # <<< ADDED
bot_id = os.getenv("TWITCH_BOT_ID")            # <<< ADDED

print(f"Attempting to connect as '{nick}' to channel '{channel}'...")
if not all([token, nick, channel, client_id, client_secret, bot_id]):
    print("\n[CRITICAL] One or more required variables are missing from your .env file. Please check it.")
    exit()

class TestBot(commands.Bot):
    async def event_ready(self):
        print("\n" + "="*50)
        print("  SUCCESS! Connection to Twitch chat was successful.")
        print(f"  Logged in as: {self.nick}")
        print("="*50 + "\n")
        # You can uncomment the line below to send a test message
        # await self.get_channel(channel).send("Test connection successful!")
        await self.close()

    async def event_authentication_failed(self, token: str):
        print("\n" + "!"*50)
        print("  FAILURE! Authentication failed with the current credentials.")
        print("  This confirms the issue persists even after a full reset.")
        print("  Please double-check every value in your .env file against your Twitch Dev Console.")
        print("!"*50 + "\n")
        await self.close()

# <<< ADDED >>> Pass all required arguments to the Bot constructor
bot = TestBot(
    token=token,
    client_id=client_id,
    client_secret=client_secret,
    nick=nick,
    bot_id=bot_id,
    prefix='!',
    initial_channels=[channel]
)

try:
    # twitchio manages its own event loop when using start()
    bot.run()
except Exception as e:
    print(f"\n[CRITICAL] An unexpected error occurred: {e}")