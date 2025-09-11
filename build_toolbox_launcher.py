"""Build script for the unified toolbox launcher.

Creates a single GUI EXE that exposes buttons for each standalone tool.
The EXE attempts to import and run modules internally when possible; otherwise
it will invoke an external Python interpreter for each tool script.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
import sys

LAUNCHER_SCRIPT = "scripts/toolbox_launcher.py"
BUILD_DIR = "build/toolbox_launcher"
DIST_DIR = "dist"
EXE_NAME = "toolbox_launcher.exe"


def build():
    script_path = Path(LAUNCHER_SCRIPT)
    if not script_path.exists():
        print(f"❌ Launcher script not found: {script_path}")
        return 1

    Path(DIST_DIR).mkdir(exist_ok=True)

    print("🔨 Building unified toolbox launcher...")
    print(f"📄 Source: {script_path}")

    pyinstaller_path = Path.cwd() / ".venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_path.exists():
        pyinstaller_path = Path("pyinstaller")

    cmd = [
        str(pyinstaller_path),
        "--onefile",
        "--windowed",
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={BUILD_DIR}",
        f"--name={EXE_NAME[:-4]}",
        # Hidden imports to ensure scripts package modules are bundled
        "--hidden-import=scripts.nef_to_jpg",
        "--hidden-import=scripts.organize_photos",
        "--hidden-import=scripts.video_compressor",
        "--hidden-import=scripts.find_duplicates",
        "--hidden-import=scripts.battery_report",
        "--hidden-import=scripts.sort_by_extension",
        "--hidden-import=scripts.sort_by_type",
        "--hidden-import=scripts.example_tool",
        LAUNCHER_SCRIPT,
    ]

    print("⚙️  Running PyInstaller...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ Build failed")
        if e.stderr:
            print(e.stderr)
        return 1

    exe_path = Path(DIST_DIR) / EXE_NAME
    if not exe_path.exists():
        print("❌ Build finished but EXE not found.")
        return 1

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✅ Build complete -> {exe_path} ({size_mb:.1f} MB)")
    print("💡 Run it: .\\dist\\toolbox_launcher.exe")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
