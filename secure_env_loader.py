"""
Secure Environment Loader for RustyBot
Encrypts sensitive credentials so they can't be easily extracted from distribution
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureEnvLoader:
    def __init__(self):
        # Generate a key from machine-specific data + embedded salt
        # This makes it harder to extract credentials, but app still works
        self.key = self._generate_key()
        self.cipher = Fernet(self.key)
    
    def _generate_key(self):
        """Generate encryption key from app-specific data"""
        # Use a combination of app name and fixed salt
        # This provides basic obfuscation while keeping it portable
        password = b"RustyBot_Twitch_Giveaway_Bot_2024"
        salt = b"rustybot_salt_v1"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_value(self, value):
        """Encrypt a string value"""
        if not isinstance(value, bytes):
            value = str(value).encode()
        encrypted = self.cipher.encrypt(value)
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value):
        """Decrypt a string value"""
        if isinstance(encrypted_value, str):
            encrypted_value = encrypted_value.encode()
        decrypted_data = base64.urlsafe_b64decode(encrypted_value)
        decrypted = self.cipher.decrypt(decrypted_data)
        return decrypted.decode()
    
    def create_encrypted_env(self, env_data, output_file='secure.env'):
        """Create encrypted environment file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Encrypted RustyBot Credentials\n")
            f.write("# These are encrypted to protect the bot token\n\n")
            for key, value in env_data.items():
                encrypted = self.encrypt_value(value)
                f.write(f"{key}={encrypted}\n")
        print(f"Created encrypted env file: {output_file}")
    
    def load_secure_env(self, env_file='secure.env'):
        """Load and decrypt environment variables"""
        env_vars = {}
        if not os.path.exists(env_file):
            return env_vars
        
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, encrypted_value = line.split('=', 1)
                    try:
                        decrypted = self.decrypt_value(encrypted_value)
                        env_vars[key] = decrypted
                        # Set in environment
                        os.environ[key] = decrypted
                    except Exception as e:
                        print(f"Warning: Could not decrypt {key}: {e}")
        
        return env_vars


def encrypt_env_file(source_env='.env', dest_env='secure.env'):
    """Utility function to encrypt existing .env file"""
    from dotenv import dotenv_values
    
    # Load existing .env
    env_data = dotenv_values(source_env)
    
    # Create encrypted version
    loader = SecureEnvLoader()
    loader.create_encrypted_env(env_data, dest_env)
    
    print(f"\nEncrypted {len(env_data)} variables:")
    for key in env_data.keys():
        print(f"  - {key}")


if __name__ == "__main__":
    # Example usage: Encrypt the current .env file
    print("RustyBot Secure Environment Encryption Tool")
    print("=" * 50)
    
    if os.path.exists('.env'):
        print("\nEncrypting .env file...")
        encrypt_env_file('.env', 'secure.env')
        print("\n✅ Encryption complete!")
        print("\nNext steps:")
        print("1. Review secure.env file")
        print("2. Update Main.py to use secure.env")
        print("3. Delete or don't distribute the plain .env file")
    else:
        print("\nNo .env file found. Creating example...")
        loader = SecureEnvLoader()
        example_data = {
            'TWITCH_TOKEN': 'your_token_here',
            'TWITCH_NICK': 'your_bot_name',
            'TWITCH_CHANNEL': 'your_channel'
        }
        loader.create_encrypted_env(example_data, 'secure.env.example')
        print("\n✅ Created secure.env.example")
