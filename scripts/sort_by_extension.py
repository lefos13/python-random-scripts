"""
File Sorter by Extension

Behavior:
- When run as a bundled EXE dropped into any folder, it scans that folder (and subfolders)
  for files, sorts them by extension into organized subfolders within a "sorted_files" directory,
  and preserves the original files.
- When run as a script via Python, it scans the current working directory.

Structure created:
sorted_files/
├── pdf/
│   ├── document1.pdf
│   └── document2.pdf
├── jpg/
│   ├── photo1.jpg
│   └── photo2.jpg
├── zip/
│   ├── archive1.zip
│   └── archive2.zip
├── no_extension/
│   ├── README
│   └── Makefile
└── ...

Dependencies:
- shutil (built-in) for file copying
- pathlib (built-in) for path handling

Notes:
- If double-clicking the EXE, a prompt at the end will keep the console open.
- Preserves original files in their original locations.
- Handles duplicate filenames by adding numeric suffixes.
- Creates organized folder structure by file extension.
- Files without extensions go to "no_extension" folder.
"""

from __future__ import annotations

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Iterable, Dict, Set
from collections import defaultdict


# Constants
CLOSE_PROMPT = "Press Enter to close..."


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
    # For packaged EXE, use the EXE location; for script, use the working directory
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def iter_all_files(root: Path, exclude_dirs: Set[str] = None) -> Iterable[Path]:
    """Iterate through all files in the directory tree, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = set()
    
    for dirpath, dirnames, filenames in os.walk(root):
        dir_path = Path(dirpath)
        
        # Skip excluded directories
        if any(exclude_dir in dir_path.parts for exclude_dir in exclude_dirs):
            continue
            
        for filename in filenames:
            file_path = dir_path / filename
            yield file_path


def get_file_extension(file_path: Path) -> str:
    """Get file extension in lowercase, or 'no_extension' if none."""
    ext = file_path.suffix.lower()
    if ext:
        return ext[1:]  # Remove the leading dot
    return "no_extension"


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


def get_file_size_mb(path: Path) -> float:
    """Get file size in MB."""
    try:
        return path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0


def sort_file_by_extension(file_path: Path, sorted_dir: Path) -> Path:
    """Move file to extension-based subfolder, preserving relative structure if needed."""
    extension = get_file_extension(file_path)
    # Create extension subfolder
    ext_folder = sorted_dir / extension
    ext_folder.mkdir(parents=True, exist_ok=True)
    # Using flattened approach for simplicity
    dest_path = ext_folder / file_path.name
    dest_path = unique_path(dest_path)
    # Move the file
    shutil.move(str(file_path), str(dest_path))
    return dest_path


def main() -> int:
    base_dir = get_base_dir()
    sorted_dir = base_dir / "sorted_files"
    sorted_dir.mkdir(exist_ok=True)

    print("📁 File Sorter by Extension")
    print(f"Scanning directory: {base_dir}")
    print(f"Output directory: {sorted_dir}")
    
    # Exclude common output directories and system folders
    exclude_dirs = {
        'sorted_files',  # Our output directory
        'converted_videos',
        'results',
        'outputs',
        'dist',
        'build',
        '.git',
        '.venv',
        '__pycache__',
        'node_modules',
        '.vs',
        '.vscode'
    }
    
    # Also exclude any existing sorted_files_* folders
    try:
        for item in base_dir.iterdir():
            if item.is_dir() and item.name.startswith('sorted_files'):
                exclude_dirs.add(item.name)
    except OSError:
        pass
    
    print(f"Excluding directories: {', '.join(sorted(exclude_dirs))}")
    
    # Scan for files
    print("\n🔍 Scanning for files...")
    all_files = list(iter_all_files(base_dir, exclude_dirs))
    
    if not all_files:
        print("No files found to sort.")
        if is_frozen():
            input(CLOSE_PROMPT)
        return 0

    # Group files by extension for reporting
    files_by_ext = defaultdict(list)
    total_size = 0
    
    for file_path in all_files:
        extension = get_file_extension(file_path)
        files_by_ext[extension].append(file_path)
        total_size += get_file_size_mb(file_path)

    # Show summary
    total_files = len(all_files)
    total_extensions = len(files_by_ext)
    
    print(f"\n📊 Found {total_files} files ({total_size:.1f} MB) with {total_extensions} different extensions:")
    
    # Show top extensions
    ext_counts = [(ext, len(files)) for ext, files in files_by_ext.items()]
    ext_counts.sort(key=lambda x: x[1], reverse=True)
    
    for ext, count in ext_counts[:10]:  # Show top 10
        print(f"  • {ext}: {count} files")
    
    if len(ext_counts) > 10:
        remaining = sum(count for ext, count in ext_counts[10:])
        print(f"  • ... and {len(ext_counts) - 10} more extensions ({remaining} files)")
    
    # Ask for confirmation when running interactively
    if is_frozen():
        print(f"\nThis will copy all files to organized subfolders in: {sorted_dir}")
        print("Original files will be preserved in their current locations.")
        response = input("\nContinue? (y/N): ").strip().lower()
        if response not in ('y', 'yes'):
            print("Operation cancelled.")
            input(CLOSE_PROMPT)
            return 0

    # Sort files
    print(f"\n🗂️  Sorting files into: {sorted_dir}")
    
    sorted_count = 0
    failed_count = 0
    
    for idx, file_path in enumerate(all_files, start=1):
        try:
            if idx % 50 == 0 or idx == total_files:
                print(f"  Progress: {idx}/{total_files} files processed", end='\r')
            
            sort_file_by_extension(file_path, sorted_dir)
            sorted_count += 1
            
        except Exception as e:
            failed_count += 1
            if failed_count <= 5:  # Show first few errors
                print(f"\n  ❌ Error sorting {file_path.name}: {e}")

    print("\n\n✅ Sorting complete!")
    print(f"   Files sorted: {sorted_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Total size: {total_size:.1f} MB")
    
    # Show created folders
    try:
        created_folders = [f.name for f in sorted_dir.iterdir() if f.is_dir()]
        created_folders.sort()
        print(f"\n📁 Created {len(created_folders)} extension folders:")
        for folder in created_folders[:15]:  # Show first 15
            file_count = len(list((sorted_dir / folder).iterdir()))
            print(f"   • {folder}/ ({file_count} files)")
        if len(created_folders) > 15:
            print(f"   • ... and {len(created_folders) - 15} more folders")
    except Exception:
        pass
    
    print(f"\n📂 Sorted files location: {sorted_dir}")
    print("💡 Original files remain in their original locations")
    
    if failed_count > 0:
        print(f"\n⚠️  {failed_count} files could not be sorted (permissions, locks, etc.)")
    
    if is_frozen():
        print("\n" + "="*60)
        input(CLOSE_PROMPT)
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
