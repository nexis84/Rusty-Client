"""
Dependency Checker for RustyBot
Verifies all required packages are installed with correct versions
"""
import sys
from importlib.metadata import version, PackageNotFoundError

# Define required packages with their expected versions
REQUIRED_PACKAGES = {
    "PyQt6": "6.9.1",
    "PyQt6-WebEngine": "6.9.0",
    "pygame": "2.6.1",
    "twitchio": "3.1.0",
    "python-twitch-irc": "1.1.0",
    "python-dotenv": "1.0.0",
    "requests": "2.32.4",
}

OPTIONAL_PACKAGES = {
    "pygame": "2.6.1",
    "python-twitch-irc": "1.1.0",
}

def check_package(name, expected_version, optional=False):
    """Check if a package is installed and version matches"""
    try:
        installed_version = version(name)
        matches = installed_version == expected_version
        
        if matches:
            status = "✓ OK"
            color = "green"
        else:
            status = f"⚠ Version mismatch (installed: {installed_version})"
            color = "yellow"
        
        opt_marker = " [OPTIONAL]" if optional else ""
        print(f"{status:30} | {name:25} | Expected: {expected_version}{opt_marker}")
        return matches or optional  # Optional packages don't cause failure
        
    except PackageNotFoundError:
        if optional:
            print(f"⚠ Not installed (optional) | {name:25} | Expected: {expected_version}")
            return True  # Optional package missing is OK
        else:
            print(f"✗ NOT INSTALLED            | {name:25} | Expected: {expected_version}")
            return False

def main():
    print("=" * 80)
    print("DEPENDENCY VERIFICATION - RustyBot v1.38")
    print("=" * 80)
    print()
    
    all_ok = True
    
    # Check required packages
    print("Required Packages:")
    print("-" * 80)
    for package, expected_ver in REQUIRED_PACKAGES.items():
        if package not in OPTIONAL_PACKAGES:
            result = check_package(package, expected_ver, optional=False)
            all_ok = all_ok and result
    
    print()
    print("Optional Packages:")
    print("-" * 80)
    for package, expected_ver in OPTIONAL_PACKAGES.items():
        check_package(package, expected_ver, optional=True)
    
    print()
    print("=" * 80)
    
    if all_ok:
        print("✅ SUCCESS: All required dependencies are installed correctly!")
        print()
        print("You can now run: python Main.py")
        return 0
    else:
        print("❌ ERROR: Some required dependencies are missing or wrong version!")
        print()
        print("To install/update dependencies, run:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
