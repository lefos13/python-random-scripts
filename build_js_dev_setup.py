"""
Build script for the JavaScript development environment setup tool.

This script creates a standalone EXE of the JS dev setup tool
that can be run on any clean Windows PC to install all necessary development tools.
"""

import subprocess
import sys
from pathlib import Path

def build_js_dev_setup():
    """Build the JavaScript development setup tool as a standalone EXE."""
    
    script_path = Path("scripts/js_dev_setup.py")
    
    if not script_path.exists():
        print(f"Error: {script_path} not found!")
        return False
    
    print("Building JavaScript development setup EXE...")
    
    # PyInstaller command
    cmd = [
        "C:/Users/slode/Python/.venv/Scripts/pyinstaller.exe",
        "--onefile",
        "--console",
        "--name", "js_dev_setup",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        str(script_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"EXE created: dist/js_dev_setup.exe")
        print("\nTo use:")
        print("1. Copy js_dev_setup.exe to any Windows PC")
        print("2. Right-click and 'Run as administrator' (REQUIRED)")
        print("3. The tool will install NVM, Node.js, Git, VS Code, Chrome, and Windows Terminal")
        print("4. VS Code will be configured with recommended settings and extensions")
        print("\nIMPORTANT: Administrator privileges are required for software installation!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_js_dev_setup()
    if not success:
        sys.exit(1)
