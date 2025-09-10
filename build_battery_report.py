"""
Build script for the battery health report tool.

This script creates a standalone EXE of the battery report generator
that can be dropped into any folder to generate battery health reports.
"""

import subprocess
import sys
from pathlib import Path

def build_battery_report():
    """Build the battery report tool as a standalone EXE."""
    
    script_path = Path("scripts/battery_report.py")
    
    if not script_path.exists():
        print(f"Error: {script_path} not found!")
        return False
    
    print("Building battery report EXE...")
    
    # PyInstaller command
    cmd = [
        "C:/Users/slode/Python/.venv/Scripts/pyinstaller.exe",
        "--onefile",
        "--console",
        "--name", "battery_report",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        str(script_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"EXE created: dist/battery_report.exe")
        print("\nTo use:")
        print("1. Copy battery_report.exe to any folder")
        print("2. Right-click and 'Run as administrator' for full report")
        print("3. Or double-click for basic report")
        print("4. Report will be generated and opened in your browser")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_battery_report()
    if not success:
        sys.exit(1)
