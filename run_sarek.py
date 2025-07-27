#!/usr/bin/env python3
"""
Standalone runner for Sarek - handles missing dependencies gracefully
"""

import sys
import os
import subprocess
from pathlib import Path

sarek_dir = Path(__file__).parent / "sarek"
sys.path.insert(0, str(sarek_dir.parent))


def check_and_install_dependencies():
    """Check for dependencies and try to install them"""
    dependencies = {
        'requests': 'python3-requests',
        'rich': 'python3-rich',
        'git': 'python3-git',
        'psutil': 'python3-psutil'
    }

    missing = []

    for module, apt_package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module} is available")
        except ImportError:
            missing.append((module, apt_package))
            print(f"❌ {module} is missing")

    if missing:
        print(f"\n🔧 Missing dependencies detected!")
        print("You can install them with:")
        print("sudo apt update")
        apt_cmd = "sudo apt install " + " ".join([pkg for _, pkg in missing])
        print(apt_cmd)
        print()

        response = input("Continue anyway? Some features may not work (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

    return len(missing) == 0


def main():
    """Main entry point"""
    print("🖖 Starting Sarek AI Assistant...")

    all_deps_available = check_and_install_dependencies()

    if not all_deps_available:
        print("⚠️  Running with limited functionality due to missing dependencies")

    try:
        from sarek.main import main as sarek_main
        sarek_main()
    except ImportError as e:
        print(f"❌ Failed to import Sarek: {e}")
        print("Make sure you're running from the correct directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running Sarek: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()