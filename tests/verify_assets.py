"""
Asset Path Verification Script
Verifies all asset files are in correct locations after migration
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from animation_manager import (
        resource_path,
        ANIMATION_HTML_FILE,
        ANIMATION_JS_FILE,
        ANIMATION_CSS_FILE,
        NETWORK_JS_FILE,
        BG_LISTS_JS_FILE,
        ANIMATION_QWEBCHANNEL_FILE
    )
    
    print("=" * 60)
    print("ASSET PATH VERIFICATION")
    print("=" * 60)
    
    assets = [
        (ANIMATION_HTML_FILE, "Animation HTML"),
        (ANIMATION_JS_FILE, "Main JavaScript"),
        (ANIMATION_CSS_FILE, "Stylesheet"),
        (NETWORK_JS_FILE, "Network Animation"),
        (BG_LISTS_JS_FILE, "Background Lists"),
        (ANIMATION_QWEBCHANNEL_FILE, "WebChannel"),
    ]
    
    all_found = True
    for file_path, name in assets:
        full_path = Path(resource_path(file_path))
        exists = full_path.exists()
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"{status:12} | {name:20} | {file_path}")
        all_found = all_found and exists
    
    print("=" * 60)
    if all_found:
        print("✅ SUCCESS: All asset files found!")
        sys.exit(0)
    else:
        print("❌ ERROR: Some asset files are missing!")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
