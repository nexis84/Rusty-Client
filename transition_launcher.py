"""
Transitional Launcher for v1.4.9 → v1.5.0 Migration
This simple script helps v1.4.9 users transition to the new Launcher-based system
"""
import os
import sys
import subprocess
from pathlib import Path

def find_launcher():
    """Find Launcher.exe in the current directory"""
    current_dir = Path(__file__).parent if hasattr(__file__, '__file__') else Path.cwd()
    
    # Check common locations
    possible_paths = [
        current_dir / "Launcher.exe",
        Path(sys.executable).parent / "Launcher.exe",
        current_dir.parent / "Launcher.exe",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def main():
    print("="*60)
    print("  RustyBot v1.5.0+ Transitional Launcher")
    print("="*60)
    print()
    
    # Find Launcher.exe
    launcher_path = find_launcher()
    
    if launcher_path:
        print(f"✓ Found Launcher.exe at: {launcher_path}")
        print()
        print("🎉 IMPORTANT: RustyBot now uses a Launcher!")
        print()
        print("What's changed:")
        print("  • Run 'Launcher.exe' instead of 'Main.exe'")
        print("  • Updates are now automatic and seamless")
        print("  • No more installer crashes!")
        print()
        print("Please update your shortcuts to point to Launcher.exe")
        print()
        print("Launching Launcher.exe now...")
        print()
        
        # Launch Launcher.exe
        try:
            subprocess.Popen([str(launcher_path)], cwd=str(launcher_path.parent))
            print("✓ Launcher started successfully!")
            print()
            input("Press Enter to close this window...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Failed to launch Launcher.exe: {e}")
            print()
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        print("❌ ERROR: Launcher.exe not found!")
        print()
        print("This appears to be an incomplete installation.")
        print()
        print("Please:")
        print("  1. Re-download RustyBot_v1.5.0_WithLauncher.zip")
        print("  2. Extract the complete contents")
        print("  3. Run Launcher.exe")
        print()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
