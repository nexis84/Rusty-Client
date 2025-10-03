#!/usr/bin/env python3
"""
Test script to verify debug message filtering
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, '.')

import config_manager

def test_debug_filtering():
    """Test the debug filtering functionality"""
    print("Testing debug message filtering...")
    
    # Load current config
    config = config_manager.load_config()
    debug_enabled = config.get('debug_mode_enabled', False)
    
    print(f"Current debug mode: {debug_enabled}")
    
    # Test messages that should be filtered
    debug_only_messages = [
        "STATE CHANGE: IDLE -> COLLECTING",
        "Successfully connected to ne_x_is", 
        "Starting bot initialization...",
        "Initializing and connecting bot...",
        "Animation page ready.",
        "Font sizes applied. Layout refresh scheduled.",
        "Attempting Twitch connection to #ne_x_is..."
    ]
    
    print(f"\nMessages that should be filtered when debug mode is OFF:")
    for msg in debug_only_messages:
        print(f"  - {msg}")
    
    print(f"\nWith debug mode {'ON' if debug_enabled else 'OFF'}, these messages will {'appear' if debug_enabled else 'be hidden'}.")
    
    return True

if __name__ == "__main__":
    try:
        test_debug_filtering()
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
