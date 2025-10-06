"""
RustyBot Credential Setup Wizard
This interactive script helps you set up your encrypted credentials
"""
import os
import sys
from secure_env_loader import SecureEnvLoader

def print_header():
    print("\n" + "="*60)
    print("  RustyBot Credential Setup Wizard")
    print("="*60)
    print("\nThis wizard will help you create an encrypted secure.env file")
    print("with your Twitch bot credentials.\n")

def get_input_with_default(prompt, default=""):
    """Get user input with an optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        user_input = input(f"{prompt}: ").strip()
        return user_input

def setup_credentials():
    """Interactive credential setup"""
    print_header()
    
    # Check if secure.env already exists
    if os.path.exists('secure.env'):
        response = input("⚠️  secure.env already exists. Overwrite? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n✅ Setup cancelled. Existing secure.env preserved.")
            return
        print()
    
    print("📋 Required Credentials")
    print("-" * 60)
    print("Get your Twitch credentials from: https://dev.twitch.tv/console/apps\n")
    
    # Collect credentials
    credentials = {}
    
    print("1️⃣  Twitch Bot Token")
    print("   (Token from Twitch - do NOT include 'oauth:' prefix)")
    credentials['TWITCH_TOKEN'] = get_input_with_default("   Enter token")
    
    print("\n2️⃣  Bot Username")
    credentials['TWITCH_NICK'] = get_input_with_default("   Enter bot username")
    
    print("\n3️⃣  Channel to Monitor")
    credentials['TWITCH_CHANNEL'] = get_input_with_default("   Enter channel name")
    
    print("\n4️⃣  Twitch Application Credentials")
    credentials['TWITCH_CLIENT_ID'] = get_input_with_default("   Enter Client ID")
    credentials['TWITCH_CLIENT_SECRET'] = get_input_with_default("   Enter Client Secret")
    credentials['TWITCH_BOT_ID'] = get_input_with_default("   Enter Bot User ID")
    
    print("\n📋 Optional Configuration")
    print("-" * 60)
    
    credentials['EVE2TWITCH_BOT_NAME'] = get_input_with_default(
        "   EVE2Twitch Bot Name", "Eve2Twitch"
    )
    
    credentials['CONFIRMATION_TIMEOUT'] = get_input_with_default(
        "   Winner Confirmation Timeout (seconds)", "90"
    )
    
    credentials['EVE_RESPONSE_TIMEOUT'] = get_input_with_default(
        "   EVE Response Timeout (seconds)", "300"
    )
    
    credentials['ENTRY_METHOD'] = get_input_with_default(
        "   Entry Method (COMMAND/KEYWORD)", "COMMAND"
    )
    
    credentials['JOIN_COMMAND'] = get_input_with_default(
        "   Join Command", "!join"
    )
    
    # Validate required fields
    required = ['TWITCH_TOKEN', 'TWITCH_NICK', 'TWITCH_CHANNEL', 
                'TWITCH_CLIENT_ID', 'TWITCH_CLIENT_SECRET', 'TWITCH_BOT_ID']
    
    missing = [field for field in required if not credentials.get(field)]
    
    if missing:
        print("\n❌ Error: Missing required fields:")
        for field in missing:
            print(f"   - {field}")
        print("\nSetup cancelled.")
        return
    
    # Create encrypted file
    print("\n🔐 Encrypting credentials...")
    loader = SecureEnvLoader()
    loader.create_encrypted_env(credentials, 'secure.env')
    
    print("\n" + "="*60)
    print("  ✅ Setup Complete!")
    print("="*60)
    print("\n📁 Created: secure.env (encrypted)")
    print("\n⚠️  IMPORTANT:")
    print("   • Keep secure.env in the same folder as RustyBot.exe")
    print("   • Do NOT share secure.env - it contains your credentials")
    print("   • You can now delete the plain .env file if it exists")
    print("\n▶️  You can now run RustyBot.exe")
    print()

def decrypt_and_show():
    """Show decrypted values from secure.env (for debugging)"""
    if not os.path.exists('secure.env'):
        print("❌ secure.env not found")
        return
    
    print("\n" + "="*60)
    print("  Current Encrypted Credentials")
    print("="*60)
    
    loader = SecureEnvLoader()
    env_vars = loader.load_secure_env('secure.env')
    
    print("\n📋 Loaded credentials:")
    for key, value in env_vars.items():
        # Mask sensitive values
        if 'TOKEN' in key or 'SECRET' in key:
            masked = value[:4] + '*'*(len(value)-8) + value[-4:] if len(value) > 8 else '***'
            print(f"   {key}: {masked}")
        else:
            print(f"   {key}: {value}")
    print()

if __name__ == "__main__":
    try:
        while True:
            print("\n" + "="*60)
            print("  RustyBot Credential Manager")
            print("="*60)
            print("\nOptions:")
            print("  1. Setup new credentials (create/overwrite secure.env)")
            print("  2. View current credentials (masked)")
            print("  3. Exit")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                setup_credentials()
            elif choice == '2':
                decrypt_and_show()
            elif choice == '3':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid option. Please choose 1-3.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to exit...")
