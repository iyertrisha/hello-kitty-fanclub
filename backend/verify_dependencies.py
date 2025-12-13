"""
Dependency Verification Script

This script verifies that all required Python packages are installed and can be imported.
Run this to check if dependencies are properly installed before starting the backend.

Usage:
    python verify_dependencies.py
"""
import sys
import importlib

# Fix for UnicodeEncodeError on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Critical packages that must be installed for the backend to work
CRITICAL_PACKAGES = {
    'flask': 'Flask',
    'flask_cors': 'Flask-CORS',
    'flask_session': 'Flask-Session',
    'mongoengine': 'mongoengine',
    'pymongo': 'pymongo',
    'dotenv': 'python-dotenv',
}

# Important packages (backend may work without some of these)
IMPORTANT_PACKAGES = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'sklearn': 'scikit-learn',
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'requests': 'requests',
    'web3': 'web3',
    'twilio': 'twilio',
    'sendgrid': 'sendgrid',
}

def check_package(package_name, display_name):
    """Check if a package can be imported"""
    try:
        importlib.import_module(package_name)
        return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

def get_package_version(package_name):
    """Get the version of an installed package"""
    try:
        module = importlib.import_module(package_name)
        if hasattr(module, '__version__'):
            return module.__version__
        return "installed (version unknown)"
    except:
        return None

def verify_dependencies():
    """Verify all dependencies are installed"""
    print("Verifying backend dependencies...")
    print("=" * 60)
    print()
    
    critical_failed = []
    important_failed = []
    
    # Check critical packages
    print("Critical Packages (required for backend to start):")
    print("-" * 60)
    for package_name, display_name in CRITICAL_PACKAGES.items():
        is_installed, error = check_package(package_name, display_name)
        if is_installed:
            version = get_package_version(package_name)
            print(f"  ✅ {display_name:20s} - {version}")
        else:
            print(f"  ❌ {display_name:20s} - MISSING")
            print(f"      Error: {error}")
            critical_failed.append(display_name)
    print()
    
    # Check important packages
    print("Important Packages (may be needed for specific features):")
    print("-" * 60)
    for package_name, display_name in IMPORTANT_PACKAGES.items():
        is_installed, error = check_package(package_name, display_name)
        if is_installed:
            version = get_package_version(package_name)
            print(f"  ✅ {display_name:20s} - {version}")
        else:
            print(f"  ⚠️  {display_name:20s} - MISSING (optional)")
            important_failed.append(display_name)
    print()
    
    # Summary
    print("=" * 60)
    if critical_failed:
        print("❌ VERIFICATION FAILED")
        print(f"   Missing critical packages: {', '.join(critical_failed)}")
        print()
        print("To install missing packages:")
        print("  1. Activate your virtual environment:")
        print("     PowerShell: .\\venv\\Scripts\\Activate.ps1")
        print("  2. Install dependencies:")
        print("     pip install -r requirements.txt")
        print("  3. Or install specific packages:")
        for pkg in critical_failed:
            print(f"     pip install {pkg}")
        return False
    elif important_failed:
        print("⚠️  VERIFICATION PASSED (with warnings)")
        print(f"   Missing optional packages: {', '.join(important_failed)}")
        print("   Backend should work, but some features may be unavailable.")
        return True
    else:
        print("✅ VERIFICATION PASSED")
        print("   All packages are installed and can be imported.")
        return True

if __name__ == '__main__':
    success = verify_dependencies()
    sys.exit(0 if success else 1)

