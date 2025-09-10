"""
Build script for the duplicate file finder tool.

This script creates a standalone EXE of the duplicate finder tool
that can be dropped into any folder to scan for duplicates.
"""

import subprocess
import sys
from pathlib import Path

def build_find_duplicates():
    """Build the duplicate finder as a standalone EXE."""
    
    script_path = Path("scripts/find_duplicates.py")
    
    if not script_path.exists():
        print(f"Error: {script_path} not found!")
        return False
    
    print("Building duplicate finder EXE...")
    
    # PyInstaller command
    cmd = [
        "C:/Users/slode/Python/.venv/Scripts/pyinstaller.exe",
        "--onefile",
        "--console",
        "--name", "find_duplicates",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        str(script_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"EXE created: dist/find_duplicates.exe")
        print("\nTo use:")
        print("1. Copy find_duplicates.exe to any folder")
        print("2. Double-click the EXE to scan for duplicates")
        print("3. Choose whether to report only or move duplicates")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_find_duplicates()
    if not success:
        sys.exit(1)
