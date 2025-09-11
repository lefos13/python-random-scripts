"""
Build script for sort_by_type.py

Creates an EXE file from the sort_by_type.py script using PyInstaller.
The resulting EXE is completely standalone and can be dropped into any directory.
"""

import subprocess
import sys
from pathlib import Path
import shutil

def main():
    # Paths
    script_file = "scripts/sort_by_type.py"
    build_dir = "build/sort_by_type"
    dist_dir = "dist"
    exe_name = "sort_by_type.exe"
    
    # Check if script exists
    if not Path(script_file).exists():
        print(f"❌ Error: {script_file} not found")
        return 1
    
    # Create dist directory
    Path(dist_dir).mkdir(exist_ok=True)
    
    print("🔨 Building sort_by_type.exe...")
    print(f"📄 Source: {script_file}")
    print(f"📁 Build dir: {build_dir}")
    print(f"📦 Output: {dist_dir}/{exe_name}")
    
    # PyInstaller command - use full path to avoid PATH issues
    pyinstaller_path = Path.cwd() / ".venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_path.exists():
        pyinstaller_path = "pyinstaller"  # Fallback to PATH
    
    cmd = [
        str(pyinstaller_path),
        "--onefile",
        "--console",
        "--clean",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        f"--specpath={build_dir}",
        f"--name={exe_name[:-4]}",  # Remove .exe extension for name
        script_file
    ]
    
    try:
        # Run PyInstaller
        print("\n⚙️  Running PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.stdout:
            print("📝 PyInstaller output:")
            print(result.stdout)
        
        # Check if EXE was created
        exe_path = Path(dist_dir) / exe_name
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Build successful!")
            print(f"📦 Created: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            print(f"\n💡 The EXE can be dropped into any folder to sort files by type.")
            print(f"   It will create a 'sorted_by_type' subfolder with organized file categories.")
        else:
            print("❌ Error: EXE file was not created")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stderr:
            print("Error details:")
            print(e.stderr)
        return 1
    
    except FileNotFoundError:
        print("❌ Error: PyInstaller not found. Install with: pip install pyinstaller")
        return 1
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())