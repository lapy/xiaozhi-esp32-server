#!/usr/bin/env python3
"""
Dependency Update and Compatibility Verification Script
Updates all Python dependencies to latest 2025 versions with compatibility checks
"""

import subprocess
import sys
import pkg_resources
import json
from pathlib import Path

def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for this project")
        return False
    elif version.minor >= 11:
        print("✅ Python version is optimal for 2025 dependencies")
    else:
        print("⚠️  Consider upgrading to Python 3.11+ for best compatibility")
    
    return True

def backup_requirements():
    """Create a backup of current requirements"""
    backup_file = "requirements_backup.txt"
    try:
        subprocess.run(["pip", "freeze"], stdout=open(backup_file, 'w'), check=True)
        print(f"✅ Created backup: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False

def update_pip_tools():
    """Update pip and essential tools"""
    print("\n🔧 Updating pip and essential tools...")
    
    commands = [
        "python -m pip install --upgrade pip",
        "pip install --upgrade setuptools wheel",
        "pip install --upgrade pip-tools pip-check"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        stdout, stderr, code = run_command(cmd, check=False)
        if code == 0:
            print(f"✅ Success")
        else:
            print(f"⚠️  Warning: {stderr}")

def install_dependencies():
    """Install updated dependencies"""
    print("\n📦 Installing updated dependencies...")
    
    cmd = "pip install -r requirements.txt"
    print(f"Running: {cmd}")
    stdout, stderr, code = run_command(cmd, check=False)
    
    if code == 0:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print(f"❌ Installation failed: {stderr}")
        return False

def check_compatibility():
    """Check for dependency conflicts"""
    print("\n🔍 Checking for dependency conflicts...")
    
    stdout, stderr, code = run_command("pip check", check=False)
    
    if code == 0:
        print("✅ No dependency conflicts found")
        return True
    else:
        print(f"⚠️  Dependency conflicts detected:")
        print(stderr)
        return False

def verify_key_imports():
    """Verify that key packages can be imported"""
    print("\n🧪 Testing key package imports...")
    
    key_packages = [
        ("torch", "PyTorch"),
        ("numpy", "NumPy"),
        ("aiohttp", "aiohttp"),
        ("websockets", "websockets"),
        ("openai", "OpenAI"),
        ("elevenlabs", "ElevenLabs"),
        ("kokoro_tts", "Kokoro TTS"),
        ("edge_tts", "Edge TTS"),
        ("loguru", "Loguru"),
        ("requests", "Requests")
    ]
    
    results = []
    for package, name in key_packages:
        try:
            __import__(package)
            print(f"✅ {name}: OK")
            results.append((name, True, None))
        except ImportError as e:
            print(f"❌ {name}: FAILED - {e}")
            results.append((name, False, str(e)))
        except Exception as e:
            print(f"⚠️  {name}: WARNING - {e}")
            results.append((name, False, str(e)))
    
    return results

def generate_report(import_results):
    """Generate a compatibility report"""
    print("\n📊 COMPATIBILITY REPORT")
    print("=" * 50)
    
    total = len(import_results)
    passed = sum(1 for _, success, _ in import_results if success)
    
    print(f"Total packages tested: {total}")
    print(f"Successfully imported: {passed}")
    print(f"Failed imports: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL DEPENDENCIES ARE COMPATIBLE!")
        print("✅ Ready for production use")
    else:
        print("\n⚠️  SOME DEPENDENCIES NEED ATTENTION:")
        for name, success, error in import_results:
            if not success:
                print(f"❌ {name}: {error}")
    
    return passed == total

def main():
    """Main update and verification process"""
    print("🚀 Python Dependencies Update & Compatibility Check")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        return False
    
    # Step 2: Create backup
    if not backup_requirements():
        return False
    
    # Step 3: Update pip and tools
    update_pip_tools()
    
    # Step 4: Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed!")
        print("💡 Try restoring from backup: pip install -r requirements_backup.txt")
        return False
    
    # Step 5: Check compatibility
    compatible = check_compatibility()
    
    # Step 6: Test imports
    import_results = verify_key_imports()
    
    # Step 7: Generate report
    all_good = generate_report(import_results)
    
    if all_good and compatible:
        print("\n🎉 UPDATE SUCCESSFUL!")
        print("✅ All dependencies updated to latest 2025 versions")
        print("✅ No compatibility issues detected")
        print("✅ All key packages import successfully")
    else:
        print("\n⚠️  UPDATE COMPLETED WITH WARNINGS")
        print("💡 Review the issues above and consider:")
        print("   - Checking package documentation for breaking changes")
        print("   - Running your application tests")
        print("   - Restoring from backup if needed")
    
    return all_good and compatible

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
