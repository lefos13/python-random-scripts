"""
Duplicate File Finder

Behavior:
- When run as a bundled EXE dropped into any folder, it scans that folder (and subfolders)
  for duplicate files by comparing SHA-256 hashes, and optionally moves duplicates to a
  timestamped "Duplicates_YYYYMMDD" folder for manual review.
- When run as a script via Python, it scans the current working directory.

Structure created:
Duplicates_20250910/
├── duplicate_file_1.jpg
├── duplicate_file_2.pdf
└── ...

Dependencies:
- hashlib (built-in) for file hashing
- shutil (built-in) for file operations

Notes:
- If double-clicking the EXE, a prompt at the end will keep the console open.
- Uses SHA-256 hash for reliable duplicate detection.
- Preserves one copy of each file in original location.
- Shows file sizes and paths for easy identification.
- Interactive mode asks before moving files.
"""

from __future__ import annotations

import sys
import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import defaultdict


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
    # Always use the current working directory, regardless of whether it's an EXE or script
    return Path.cwd()


def calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except (OSError, IOError) as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return ""


def get_file_size_mb(path: Path) -> float:
    """Get file size in MB."""
    try:
        return path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0


def scan_for_duplicates(root_dir: Path, exclude_dirs: Set[str] = None) -> Dict[str, List[Path]]:
    """Scan directory for duplicate files and return hash -> file_paths mapping."""
    if exclude_dirs is None:
        exclude_dirs = set()
    
    file_hashes = defaultdict(list)
    total_files = 0
    processed_files = 0
    
    print("Scanning files and calculating hashes...")
    
    # First pass: count total files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip excluded directories
        dir_path = Path(dirpath)
        if any(exclude_dir in dir_path.parts for exclude_dir in exclude_dirs):
            continue
        total_files += len(filenames)
    
    # Second pass: calculate hashes
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dir_path = Path(dirpath)
        
        # Skip excluded directories
        if any(exclude_dir in dir_path.parts for exclude_dir in exclude_dirs):
            continue
        
        for filename in filenames:
            file_path = dir_path / filename
            processed_files += 1
            
            if processed_files % 10 == 0 or processed_files == total_files:
                print(f"  Progress: {processed_files}/{total_files} files processed", end='\r')
            
            file_hash = calculate_file_hash(file_path)
            if file_hash:  # Only add if hash was successfully calculated
                file_hashes[file_hash].append(file_path)
    
    print(f"\n  Completed: {processed_files} files processed")
    
    # Filter to only return duplicates (more than one file with same hash)
    duplicates = {hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) > 1}
    
    return duplicates


def display_duplicates(duplicates: Dict[str, List[Path]]) -> None:
    """Display found duplicates in a readable format."""
    if not duplicates:
        print("No duplicate files found!")
        return
    
    total_duplicate_files = sum(len(paths) - 1 for paths in duplicates.values())  # -1 because we keep one copy
    total_duplicate_size = 0
    
    print(f"\nFound {len(duplicates)} sets of duplicate files:")
    print("=" * 60)
    
    for i, (file_hash, file_paths) in enumerate(duplicates.items(), 1):
        file_size = get_file_size_mb(file_paths[0])
        duplicate_size = file_size * (len(file_paths) - 1)  # Size of files that would be removed
        total_duplicate_size += duplicate_size
        
        print(f"\nDuplicate Set #{i} ({len(file_paths)} files, {file_size:.2f} MB each):")
        print(f"  Hash: {file_hash[:16]}...")
        
        for j, path in enumerate(file_paths):
            status = "[KEEP]" if j == 0 else "[DUPLICATE]"
            print(f"    {status} {path}")
    
    print("=" * 60)
    print(f"Total: {total_duplicate_files} duplicate files consuming {total_duplicate_size:.2f} MB")


def get_user_choice() -> str:
    """Get user's choice for handling duplicates."""
    if not is_frozen():
        return 'report'  # Default to report-only for script mode
    
    print("\nChoose an action:")
    print("  r = Report only (show duplicates but don't move files)")
    print("  m = Move duplicates to review folder")
    print("  q = Quit without doing anything")
    
    while True:
        choice = input("Enter your choice (r/m/q): ").strip().lower()
        if choice in ['r', 'report', 'show']:
            return 'report'
        elif choice in ['m', 'move']:
            return 'move'
        elif choice in ['q', 'quit', 'exit']:
            return 'quit'
        else:
            print("Please enter 'r', 'm', or 'q'")


def move_duplicates(duplicates: Dict[str, List[Path]], base_dir: Path) -> int:
    """Move duplicate files to a timestamped folder."""
    if not duplicates:
        return 0
    
    # Create timestamped folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    duplicates_dir = base_dir / f"Duplicates_{timestamp}"
    duplicates_dir.mkdir(exist_ok=True)
    
    moved_count = 0
    failed_count = 0
    
    print(f"\nMoving duplicates to: {duplicates_dir}")
    
    for file_hash, file_paths in duplicates.items():
        # Keep the first file, move the rest
        for i, duplicate_path in enumerate(file_paths[1:], 1):
            try:
                # Create unique filename if needed
                dest_name = duplicate_path.name
                dest_path = duplicates_dir / dest_name
                
                # Handle name conflicts
                counter = 1
                while dest_path.exists():
                    stem = duplicate_path.stem
                    suffix = duplicate_path.suffix
                    dest_name = f"{stem}_copy{counter}{suffix}"
                    dest_path = duplicates_dir / dest_name
                    counter += 1
                
                # Move the file
                shutil.move(str(duplicate_path), str(dest_path))
                print(f"  Moved: {duplicate_path.name} -> {dest_path.name}")
                moved_count += 1
                
            except Exception as e:
                print(f"  ERROR moving {duplicate_path}: {e}")
                failed_count += 1
    
    print(f"\nMoved {moved_count} duplicate files to {duplicates_dir}")
    if failed_count > 0:
        print(f"Failed to move {failed_count} files")
    
    return moved_count


def main() -> int:
    base_dir = get_base_dir()
    
    print("Duplicate File Finder")
    print(f"Scanning directory: {base_dir}")
    
    # Exclude common output directories from scanning
    exclude_dirs = {
        'Duplicates_' + datetime.now().strftime("%Y%m%d"),  # Today's duplicates folder
        'converted_videos',
        'results',
        '.git',
        '.venv',
        '__pycache__',
        'node_modules'
    }
    
    # Also exclude any existing Duplicates_* folders
    try:
        for item in base_dir.iterdir():
            if item.is_dir() and item.name.startswith('Duplicates_'):
                exclude_dirs.add(item.name)
    except OSError:
        pass
    
    print(f"Excluding directories: {', '.join(sorted(exclude_dirs))}")
    
    # Find duplicates
    duplicates = scan_for_duplicates(base_dir, exclude_dirs)
    
    # Display results
    display_duplicates(duplicates)
    
    if not duplicates:
        if is_frozen():
            input("Press Enter to close...")
        return 0
    
    # Get user choice
    choice = get_user_choice()
    
    if choice == 'quit':
        print("Operation cancelled.")
        if is_frozen():
            input("Press Enter to close...")
        return 0
    elif choice == 'report':
        print("Report complete. No files were moved.")
    elif choice == 'move':
        moved_count = move_duplicates(duplicates, base_dir)
        if moved_count > 0:
            print(f"\nDuplicate cleanup complete! Review files in the Duplicates folder.")
            print("You can safely delete them if they are truly duplicates.")
    
    if is_frozen():
        input("Press Enter to close...")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
