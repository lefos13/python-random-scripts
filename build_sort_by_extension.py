"""
Build script for the file sorter by extension tool.

This script creates a standalone EXE of the file sorter tool
that can be dropped into any folder to organize files by extension.
"""

import subprocess
import sys
from pathlib import Path

def build_sort_by_extension():
    """Build the file sorter as a standalone EXE."""
    
    script_path = Path("scripts/sort_by_extension.py")
    
    if not script_path.exists():
        print(f"Error: {script_path} not found!")
        return False
    
    print("Building file sorter by extension EXE...")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name", "sort_by_extension",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        str(script_path)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print("EXE created: dist/sort_by_extension.exe")
        print("\nTo use:")
        print("1. Copy sort_by_extension.exe to any folder")
        print("2. Double-click the EXE to sort files by extension")
        print("3. Files will be organized into 'sorted_files/' subfolders")
        print("4. Original files are preserved in their current locations")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_sort_by_extension()
    if not success:
        sys.exit(1)
