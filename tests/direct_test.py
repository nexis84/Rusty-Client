import sys
import asyncio
from twitchio.client import Client

print("--- Direct Credential Test ---")

# Check if we have the right number of arguments
if len(sys.argv) != 4:
    print("\n[ERROR] Incorrect usage!")
    print('Please run like this: python direct_test.py "oauth:your_token" "your_client_id" "your_client_secret"')
    sys.exit(1)

# Get credentials directly from the command line
token = sys.argv[1]
client_id = sys.argv[2]
client_secret = sys.argv[3]
channel_name = "ne_x_is" # Hardcoded for this test
nick = "The_rusty_Bot"

# Print the credentials to verify they were passed correctly
print(f"Using Token: {token[:12]}...")
print(f"Using Client ID: {client_id}")
print(f"Using Client Secret: {'*' * len(client_secret)}")

class TestBot(Client):
    async def event_ready(self):
        print(f"\n[SUCCESS] Connected to Twitch as {self.nick}!")
        await self.join_channels([channel_name])

    async def event_join(self, channel, user):
        if user.name.lower() == self.nick.lower():
            print(f"[SUCCESS] Successfully joined channel #{channel.name}")
            await channel.send("🤖 Direct credential test successful! The problem is with the .env file.")
            await self.close()

    async def event_error(self, error: Exception, data: str = None):
        print(f"\n[ERROR] Authentication Failed: {error}")
        print("This confirms the issue is with the token/secret generation process itself.")
        await self.close()

async def main():
    bot = TestBot(
        token=token,
        client_id=client_id,
        client_secret=client_secret
    )
    try:
        await bot.start()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())