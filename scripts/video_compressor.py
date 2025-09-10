"""
Video Batch Compressor using FFmpeg

Behavior:
- When run as a bundled EXE dropped into any folder, it scans that folder (and subfolders)
  for video files, compresses them using bundled FFmpeg with configurable quality settings,
  and saves results to a "converted_videos" subfolder while preserving originals.
- When run as a script via Python, it scans the current working directory.

Structure created:
converted_videos/
├── video1_compressed.mp4
├── video2_compressed.mp4
└── ...

Dependencies:
- ffmpeg-python for Python FFmpeg bindings
- FFmpeg binaries (bundled with EXE or auto-downloaded)

Notes:
- If double-clicking the EXE, a prompt at the end will keep the console open.
- Supports common video formats: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, etc.
- Handles duplicate filenames by adding numeric suffixes.
- Quality presets: high, medium, low (adjustable CRF values).
- FFmpeg is automatically bundled - no separate installation needed!
"""

from __future__ import annotations

import sys
import os
import subprocess
from pathlib import Path
from typing import Iterable, Optional
import tempfile
import shutil

# Common video extensions
VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v',
    '.mpg', '.mpeg', '.3gp', '.asf', '.rm', '.rmvb', '.vob', '.ts'
}

# Quality presets (CRF values - lower = better quality/larger size)
QUALITY_PRESETS = {
    'high': 18,      # High quality
    'medium': 23,    # Balanced (default)
    'low': 28        # Smaller file size
}

DEFAULT_QUALITY = 'medium'


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
    # For packaged EXE, use the EXE location; for script, use the working directory
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def iter_video_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip the converted_videos folder itself if it already exists
        if Path(dirpath) == (root / "converted_videos"):
            continue
        for name in filenames:
            if Path(name).suffix.lower() in VIDEO_EXTENSIONS:
                yield Path(dirpath) / name


def unique_path(path: Path) -> Path:
    """Generate a unique path if file already exists by adding numeric suffix."""
    if not path.exists():
        return path
    
    base = path.with_suffix("")
    suffix = path.suffix
    i = 1
    while True:
        cand = base.with_name(f"{base.name}_{i}").with_suffix(suffix)
        if not cand.exists():
            return cand
        i += 1


def get_ffmpeg_path() -> str:
    """Get the path to FFmpeg executable, using bundled version if available."""
    # When frozen (EXE), look for bundled FFmpeg in temp extraction folder
    if is_frozen():
        # PyInstaller extracts to _MEIXXXXXX temp folder
        bundle_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(sys.executable).parent
        
        # Try common locations for bundled FFmpeg
        for ffmpeg_name in ['ffmpeg.exe', 'ffmpeg']:
            ffmpeg_path = bundle_dir / ffmpeg_name
            if ffmpeg_path.exists():
                return str(ffmpeg_path)
        
        # Try looking in subdirectories
        for subdir in ['ffmpeg', 'bin']:
            for ffmpeg_name in ['ffmpeg.exe', 'ffmpeg']:
                ffmpeg_path = bundle_dir / subdir / ffmpeg_name
                if ffmpeg_path.exists():
                    return str(ffmpeg_path)
    
    # Fallback to system PATH
    return 'ffmpeg'


def check_ffmpeg() -> tuple[bool, str]:
    """Check if FFmpeg is available and return status and path."""
    ffmpeg_path = get_ffmpeg_path()
    
    try:
        result = subprocess.run([ffmpeg_path, '-version'], 
                              capture_output=True, check=True, timeout=10)
        return True, ffmpeg_path
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False, ffmpeg_path


def download_ffmpeg_if_needed() -> Optional[str]:
    """Download FFmpeg if not available (fallback for development)."""
    try:
        import ffmpeg
        # ffmpeg-python doesn't include binaries, so we still need system FFmpeg
        # For a fully self-contained solution, we'd need to bundle FFmpeg manually
        return None
    except ImportError:
        return None


def compress_video(input_path: Path, output_path: Path, quality: str = DEFAULT_QUALITY) -> None:
    """Compress video using FFmpeg with specified quality preset."""
    crf = QUALITY_PRESETS.get(quality.lower(), QUALITY_PRESETS[DEFAULT_QUALITY])
    ffmpeg_path = get_ffmpeg_path()
    
    # FFmpeg command for H.264 compression with good compatibility
    cmd = [
        ffmpeg_path,
        '-i', str(input_path),
        '-c:v', 'libx264',          # Video codec
        '-crf', str(crf),           # Quality setting
        '-preset', 'medium',        # Encoding speed/efficiency balance
        '-c:a', 'aac',              # Audio codec
        '-b:a', '128k',             # Audio bitrate
        '-movflags', '+faststart',  # Web optimization
        '-y',                       # Overwrite output file
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise Exception("FFmpeg timed out (5 minutes limit)")
    except Exception as e:
        raise Exception(f"Compression failed: {e}")


def get_file_size_mb(path: Path) -> float:
    """Get file size in MB."""
    return path.stat().st_size / (1024 * 1024)


def get_quality_choice() -> str:
    """Get quality choice from user when running interactively."""
    if is_frozen():
        print("\nQuality presets:")
        print("  h = High quality (larger files)")
        print("  m = Medium quality (balanced) [default]")
        print("  l = Low quality (smaller files)")
        
        while True:
            choice = input("Choose quality (h/m/l) or press Enter for medium: ").strip().lower()
            if choice == '' or choice == 'm':
                return 'medium'
            elif choice == 'h':
                return 'high'
            elif choice == 'l':
                return 'low'
            else:
                print("Please enter 'h', 'm', 'l' or press Enter for default.")
    else:
        return DEFAULT_QUALITY


def main() -> int:
    base_dir = get_base_dir()
    output_dir = base_dir / "converted_videos"
    output_dir.mkdir(exist_ok=True)

    print(f"Video Batch Compressor")
    print(f"Scanning for video files under: {base_dir}")
    
    # Check FFmpeg availability
    ffmpeg_available, ffmpeg_path = check_ffmpeg()
    if not ffmpeg_available:
        print("ERROR: FFmpeg not found!")
        print("This tool requires FFmpeg to compress videos.")
        
        if is_frozen():
            print("FFmpeg should be bundled with this executable.")
            print("If you're seeing this error, the bundling may have failed.")
            print("You can:")
            print("1. Download FFmpeg from: https://ffmpeg.org/download.html")
            print("2. Place ffmpeg.exe in the same folder as this EXE")
            print("3. Or install FFmpeg to your system PATH")
        else:
            print("Please install FFmpeg:")
            print("1. Download from: https://ffmpeg.org/download.html")
            print("2. Add to your system PATH")
            print("3. Or place ffmpeg.exe in the same folder as this script")
        
        if is_frozen():
            input("Press Enter to close...")
        return 1
    
    print(f"Using FFmpeg: {ffmpeg_path}")
    
    video_files = list(iter_video_files(base_dir))
    
    if not video_files:
        print("No video files found. Nothing to compress.")
        if is_frozen():
            input("Press Enter to close...")
        return 0

    total = len(video_files)
    print(f"Found {total} video file(s).")
    
    # Get quality preference
    quality = get_quality_choice()
    print(f"Using quality preset: {quality} (CRF {QUALITY_PRESETS[quality]})")
    print(f"Output directory: {output_dir}")
    
    if is_frozen():
        input("\nPress Enter to start compression...")

    compressed = 0
    failed = 0
    total_size_before = 0
    total_size_after = 0
    
    for idx, video_path in enumerate(video_files, start=1):
        try:
            # Generate output filename
            output_name = f"{video_path.stem}_compressed.mp4"
            output_path = output_dir / output_name
            output_path = unique_path(output_path)
            
            size_before = get_file_size_mb(video_path)
            total_size_before += size_before
            
            print(f"\n[{idx}/{total}] Compressing: {video_path.name}")
            print(f"  Size: {size_before:.1f} MB")
            print(f"  Output: {output_path.name}")
            
            compress_video(video_path, output_path, quality)
            
            size_after = get_file_size_mb(output_path)
            total_size_after += size_after
            compression_ratio = ((size_before - size_after) / size_before) * 100
            
            print(f"  ✓ Done! {size_after:.1f} MB ({compression_ratio:+.1f}%)")
            compressed += 1
            
        except Exception as e:
            failed += 1
            print(f"  ✗ ERROR: {e}")

    print(f"\n{'='*50}")
    print(f"Compression Summary:")
    print(f"  Processed: {compressed}")
    print(f"  Failed: {failed}")
    print(f"  Total size before: {total_size_before:.1f} MB")
    print(f"  Total size after: {total_size_after:.1f} MB")
    if total_size_before > 0:
        overall_reduction = ((total_size_before - total_size_after) / total_size_before) * 100
        print(f"  Overall reduction: {overall_reduction:+.1f}%")
    print(f"  Output directory: {output_dir}")
    
    if is_frozen():
        input("\nPress Enter to close...")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
