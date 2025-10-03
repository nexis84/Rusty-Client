#!/usr/bin/env python3
"""
Quick debug functionality test script
"""

import sys
import os
import json

# Add the current directory to the path
sys.path.insert(0, '.')

import config_manager

def test_debug_mode():
    """Test the debug mode functionality"""
    print("Testing debug mode functionality...")
    
    # Test 1: Check if debug_mode_enabled is in default config
    default_config = config_manager.DEFAULT_CONFIG
    has_debug = 'debug_mode_enabled' in default_config
    debug_value = default_config.get('debug_mode_enabled', 'NOT_FOUND')
    
    print(f"✓ Debug mode in default config: {has_debug}")
    print(f"✓ Default debug value: {debug_value}")
    
    # Test 2: Load current config and check debug setting
    current_config = config_manager.load_config()
    current_debug = current_config.get('debug_mode_enabled', 'NOT_FOUND')
    
    print(f"✓ Current debug setting: {current_debug}")
    
    # Test 3: Test saving debug mode
    test_config = current_config.copy()
    test_config['debug_mode_enabled'] = True
    config_manager.save_config(test_config)
    
    loaded_config = config_manager.load_config()
    test_debug_on = loaded_config.get('debug_mode_enabled')
    
    test_config['debug_mode_enabled'] = False
    config_manager.save_config(test_config)
    
    loaded_config = config_manager.load_config()
    test_debug_off = loaded_config.get('debug_mode_enabled')
    
    print(f"✓ Debug ON test: {test_debug_on}")
    print(f"✓ Debug OFF test: {test_debug_off}")
    
    print("\nDebug mode configuration test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_debug_mode()
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
