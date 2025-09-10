"""
FFmpeg Downloader and Bundler for PyInstaller

This script downloads FFmpeg binaries for Windows and sets up PyInstaller
to bundle them with the video compressor executable.
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path
import shutil
import subprocess


def download_ffmpeg_windows():
    """Download FFmpeg binaries for Windows."""
    ffmpeg_dir = Path("ffmpeg_bundle")
    ffmpeg_dir.mkdir(exist_ok=True)
    
    # FFmpeg release URL (Windows essentials build)
    # Using a reliable third-party build since official releases are large
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    print("Downloading FFmpeg (this may take a few minutes)...")
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    
    try:
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print("Download complete. Extracting...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Find the extracted folder (usually has version number)
        extracted_folders = [f for f in ffmpeg_dir.iterdir() if f.is_dir()]
        if extracted_folders:
            ffmpeg_folder = extracted_folders[0]
            ffmpeg_exe = ffmpeg_folder / "bin" / "ffmpeg.exe"
            
            if ffmpeg_exe.exists():
                # Copy to bundle directory
                bundle_ffmpeg = ffmpeg_dir / "ffmpeg.exe"
                shutil.copy2(ffmpeg_exe, bundle_ffmpeg)
                print(f"FFmpeg extracted to: {bundle_ffmpeg}")
                
                # Cleanup
                zip_path.unlink()
                shutil.rmtree(ffmpeg_folder)
                
                return bundle_ffmpeg
            else:
                print("Error: ffmpeg.exe not found in extracted files")
                return None
        else:
            print("Error: No folders found in extracted zip")
            return None
            
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return None


def build_video_compressor_with_ffmpeg():
    """Build video compressor with bundled FFmpeg."""
    # Download FFmpeg if not present
    ffmpeg_bundle_dir = Path("ffmpeg_bundle")
    ffmpeg_exe = ffmpeg_bundle_dir / "ffmpeg.exe"
    
    if not ffmpeg_exe.exists():
        print("FFmpeg not found, downloading...")
        downloaded_ffmpeg = download_ffmpeg_windows()
        if not downloaded_ffmpeg:
            print("Failed to download FFmpeg. Aborting.")
            return False
        ffmpeg_exe = downloaded_ffmpeg
    
    # Build with PyInstaller, including FFmpeg
    print("Building video compressor with bundled FFmpeg...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name", "video_compressor",
        "--add-binary", f"{ffmpeg_exe};.",  # Bundle FFmpeg in root of exe
        "--strip",
        "--icon", "NONE",
        "--paths", "src",
        "scripts/video_compressor.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("Build successful! Check dist/video_compressor.exe")
        print("This EXE now includes FFmpeg and requires no separate installation.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "download-only":
        download_ffmpeg_windows()
    else:
        build_video_compressor_with_ffmpeg()
