"""
Build script for the NEF to JPG converter tool.

This script creates a standalone EXE of the NEF to JPG converter
that can be dropped into any folder to batch convert NEF images to JPG.
"""

import subprocess
import sys
from pathlib import Path

def build_nef_to_jpg():
    """Build the NEF to JPG converter as a standalone EXE."""
    
    script_path = Path("scripts/nef_to_jpg.py")
    
    if not script_path.exists():
        print(f"Error: {script_path} not found!")
        return False
    
    print("Building NEF to JPG converter EXE...")
    
    # PyInstaller command
    cmd = [
        "C:/Projects/My projects/python-random-scripts/.venv/Scripts/pyinstaller.exe",
        "--onefile",
        "--console",
        "--name", "nef_to_jpg",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        str(script_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"EXE created: dist/nef_to_jpg.exe")
        print("\nTo use:")
        print("1. Copy nef_to_jpg.exe to any folder")
        print("2. Double-click the EXE to batch convert NEF images to JPG")
        print("3. Use command-line flags for advanced options (see README)")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_nef_to_jpg()
    if not success:
        sys.exit(1)
