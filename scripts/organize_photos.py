"""
Photo Organizer by Date

Behavior:
- When run as a bundled EXE dropped into any folder, it scans that folder (and subfolders)
  for image files, reads their date metadata, creates a "results" directory with year/month
  structure, and copies images there while preserving originals.
- When run as a script via Python, it scans the current working directory.

Structure created:
results/
├── 2023/
│   ├── 01-January/
│   ├── 02-February/
│   └── ...
├── 2024/
│   ├── 01-January/
│   └── ...

Dependencies:
- Pillow (PIL) for EXIF data reading
- shutil for file copying

Notes:
- If double-clicking the EXE, a prompt at the end will keep the console open.
- Falls back to file modification date if EXIF date is unavailable.
- Handles duplicate filenames by adding numeric suffixes.
"""

from __future__ import annotations

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Iterable, Optional

# Common image extensions
IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp',
    '.nef', '.cr2', '.arw', '.dng', '.raf', '.orf', '.rw2', '.pef', '.srw'
}


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
    # For packaged EXE, use the EXE location; for script, use the working directory
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def iter_image_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip the results folder itself if it already exists
        if Path(dirpath) == (root / "results"):
            continue
        for name in filenames:
            if Path(name).suffix.lower() in IMAGE_EXTENSIONS:
                yield Path(dirpath) / name


def get_image_date(image_path: Path) -> datetime:
    """Extract date from EXIF data, fall back to file modification date."""
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        with Image.open(image_path) as img:
            exif_data = img.getexif()
            
            if exif_data:
                # Try different EXIF date fields
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ('DateTime', 'DateTimeOriginal', 'DateTimeDigitized'):
                        try:
                            return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                        except (ValueError, TypeError):
                            continue
    except Exception:
        pass
    
    # Fall back to file modification time
    return datetime.fromtimestamp(image_path.stat().st_mtime)


def get_month_name(month: int) -> str:
    """Convert month number to formatted string with name."""
    months = [
        "01-January", "02-February", "03-March", "04-April",
        "05-May", "06-June", "07-July", "08-August",
        "09-September", "10-October", "11-November", "12-December"
    ]
    return months[month - 1]


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


def organize_photo(image_path: Path, results_dir: Path) -> None:
    """Copy image to organized folder structure based on its date."""
    try:
        img_date = get_image_date(image_path)
        year = img_date.year
        month = img_date.month
        
        # Create year/month folder structure
        month_folder = results_dir / str(year) / get_month_name(month)
        month_folder.mkdir(parents=True, exist_ok=True)
        
        # Copy file with unique name if needed
        dest_path = month_folder / image_path.name
        dest_path = unique_path(dest_path)
        
        shutil.copy2(image_path, dest_path)
        return dest_path
        
    except Exception as e:
        raise Exception(f"Failed to organize {image_path}: {e}")


def main() -> int:
    base_dir = get_base_dir()
    results_dir = base_dir / "results"
    results_dir.mkdir(exist_ok=True)

    print(f"Scanning for image files under: {base_dir}")
    image_files = list(iter_image_files(base_dir))
    
    if not image_files:
        print("No image files found. Nothing to organize.")
        if is_frozen():
            input("Press Enter to close...")
        return 0

    total = len(image_files)
    print(f"Found {total} image file(s). Organizing by date to: {results_dir}")

    organized = 0
    failed = 0
    
    for idx, img_path in enumerate(image_files, start=1):
        try:
            dest_path = organize_photo(img_path, results_dir)
            img_date = get_image_date(img_path)
            print(f"[{idx}/{total}] {img_path.name} ({img_date.strftime('%Y-%m-%d')}) -> {dest_path.relative_to(results_dir)}")
            organized += 1
        except Exception as e:
            failed += 1
            print(f"ERROR: {e}")

    print(f"\nDone! Organized: {organized}, Failed: {failed}")
    print(f"Photos organized in: {results_dir}")
    
    if is_frozen():
        input("Press Enter to close...")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())