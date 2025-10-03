import os
import asyncio
from dotenv import load_dotenv
from twitchio.ext import commands

load_dotenv()

# Load credentials from .env (replace with your actual values or make sure you load them!)
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_BOT_ID = os.getenv("TWITCH_BOT_ID")
# Create the bot
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            client_id=TWITCH_CLIENT_ID,
            client_secret=TWITCH_CLIENT_SECRET,
            prefix="!",
            initial_channels=[TWITCH_CHANNEL]
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")
        print(f"User id is | {self.user_id}")
        print(f"Channel: {TWITCH_CHANNEL}")


async def main():
    bot = Bot()
    try:
        await bot.start()
    except Exception as e:
        print(f"Error connecting: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())