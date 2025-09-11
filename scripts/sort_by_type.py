"""
File Sorter by Type

Behavior:
- When run as a bundled EXE dropped into any folder, it scans that folder (and subfolders)
  for files, sorts them by type into organized subfolders within a "sorted_by_type" directory,
  and preserves the original files.
- When run as a script via Python, it scans the current working directory.

Categories:
- Documents: PDF, DOC, DOCX, TXT, RTF, ODT, PPT, PPTX, XLS, XLSX, etc.
- Images: JPG, PNG, GIF, BMP, TIFF, SVG, WEBP, ICO, etc.
- Media: MP4, AVI, MP3, WAV, FLAC, MKV, MOV, WMV, AAC, etc.
- Executables: EXE, MSI, DEB, RPM, APP, DMG, BAT, SH, PS1, etc.
- Archives: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ, etc.
- Code: PY, JS, HTML, CSS, CPP, C, H, JAVA, etc.
- Others: Everything else that doesn't fit the above categories

Structure created:
sorted_by_type/
├── Documents/
│   ├── document1.pdf
│   └── report.docx
├── Images/
│   ├── photo1.jpg
│   └── logo.png
├── Media/
│   ├── video.mp4
│   └── song.mp3
├── Executables/
│   ├── installer.exe
│   └── setup.msi
├── Archives/
│   ├── backup.zip
│   └── files.tar.gz
├── Code/
│   ├── script.py
│   └── index.html
└── Others/
    ├── README
    └── unknown.xyz

Dependencies:
- shutil (built-in) for file copying
- pathlib (built-in) for path handling

Notes:
- If double-clicking the EXE, a prompt at the end will keep the console open.
- Preserves original files in their original locations.
- Handles duplicate filenames by adding numeric suffixes.
- Creates organized folder structure by file type categories.
- Files without extensions or unknown extensions go to "Others" category.
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

# File type categories mapping
FILE_TYPE_CATEGORIES = {
    "Documents": {
        "pdf", "doc", "docx", "txt", "rtf", "odt", "ods", "odp",
        "ppt", "pptx", "pps", "ppsx", "xls", "xlsx", "xlsm", "csv",
        "epub", "mobi", "azw", "azw3", "fb2", "lit", "lrf", "pdb",
        "djvu", "djv", "tex", "latex", "md", "markdown", "org",
        "rst", "asciidoc", "adoc", "pages", "numbers", "key",
        "wps", "wpt", "dif", "slk", "prn", "ots", "fods", "uos",
        "sxw", "stw", "sxc", "stc", "sxi", "sti", "sxd", "std"
    },
    
    "Images": {
        "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "svg",
        "webp", "ico", "cur", "ani", "psd", "ai", "eps", "raw",
        "nef", "cr2", "cr3", "arw", "dng", "orf", "rw2", "pef", "srw",
        "heic", "heif", "avif", "jxl", "jp2", "j2k", "jpf", "jpx",
        "jpm", "mj2", "exr", "hdr", "pic", "pct", "sgi", "tga",
        "pcx", "ppm", "pgm", "pbm", "pnm", "xbm", "xpm", "dds"
    },
    
    "Media": {
        # Video formats
        "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v",
        "3gp", "3g2", "asf", "rm", "rmvb", "vob", "ogv", "dv",
        "ts", "mts", "m2ts", "mxf", "f4v", "divx", "xvid",
        
        # Audio formats
        "mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "opus",
        "ape", "alac", "aiff", "au", "ra", "amr", "ac3", "dts",
        "tta", "wv", "tak", "spx", "gsm", "voc", "snd", "caf"
    },
    
    "Executables": {
        "exe", "msi", "msp", "msu", "app", "dmg", "pkg", "deb",
        "rpm", "snap", "flatpak", "appimage", "run", "bin", "com",
        "bat", "cmd", "sh", "bash", "zsh", "fish", "ps1", "psm1",
        "vbs", "vbe", "js", "jse", "wsf", "wsh", "scr", "pif",
        "gadget", "inf", "ins", "isp", "job", "lnk", "msc",
        "reg", "rgs", "scf", "sct", "shb", "shs", "u3p", "vb"
    },
    
    "Archives": {
        "zip", "rar", "7z", "tar", "gz", "bz2", "xz", "lzma",
        "z", "lz", "lz4", "zst", "br", "ar", "cpio", "shar",
        "iso", "img", "dmg", "toast", "vcd", "cab", "msi",
        "ace", "arj", "arc", "pak", "pk3", "pk4", "war", "ear",
        "sar", "apk", "ipa", "deb", "rpm", "xpi", "crx",
        "egg", "whl", "gem", "nupkg", "vsix", "oxt"
    },
    
    "Code": {
        "py", "pyw", "pyc", "pyo", "pyd", "js", "jsx", "ts", "tsx",
        "html", "htm", "css", "scss", "sass", "less", "xml", "json",
        "yaml", "yml", "toml", "ini", "cfg", "conf", "config",
        "c", "cpp", "cxx", "cc", "h", "hpp", "hxx", "hh",
        "java", "class", "jar", "scala", "kt", "kts", "groovy",
        "cs", "vb", "fs", "fsx", "fsi", "ml", "mli",
        "php", "rb", "gem", "go", "rs", "swift", "m", "mm",
        "r", "R", "m", "pl", "pm", "t", "pod", "lua", "tcl",
        "sql", "db", "sqlite", "mdb", "accdb", "dbf", "gdb",
        "sh", "bash", "zsh", "fish", "awk", "sed", "vim", "el",
        "clj", "cljs", "cljc", "edn", "hs", "lhs", "elm", "ex",
        "exs", "eex", "heex", "dart", "pas", "pp", "inc", "asm",
        "s", "nasm", "yasm", "f", "f90", "f95", "f03", "f08",
        "for", "ftn", "fpp", "jl", "nb", "wl", "m", "mata"
    }
}

# Create reverse mapping for faster lookup
EXTENSION_TO_CATEGORY = {}
for category, extensions in FILE_TYPE_CATEGORIES.items():
    for ext in extensions:
        EXTENSION_TO_CATEGORY[ext] = category


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


def get_file_category(file_path: Path) -> str:
    """Get file category based on extension."""
    ext = file_path.suffix.lower()
    if ext:
        ext = ext[1:]  # Remove the leading dot
        return EXTENSION_TO_CATEGORY.get(ext, "Others")
    return "Others"


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


def copy_file_by_type(file_path: Path, sorted_dir: Path) -> Path:
    """Copy file to type-based subfolder (default)."""
    return move_or_copy_file_by_type(file_path, sorted_dir, move=False)

def move_file_by_type(file_path: Path, sorted_dir: Path) -> Path:
    """Move file to type-based subfolder."""
    return move_or_copy_file_by_type(file_path, sorted_dir, move=True)

def move_or_copy_file_by_type(file_path: Path, sorted_dir: Path, move: bool = False) -> Path:
    """Move or copy file to type-based subfolder based on the 'move' flag."""
    category = get_file_category(file_path)
    category_folder = sorted_dir / category
    category_folder.mkdir(parents=True, exist_ok=True)
    dest_path = category_folder / file_path.name
    dest_path = unique_path(dest_path)
    if move:
        shutil.move(str(file_path), str(dest_path))
    else:
        shutil.copy2(str(file_path), str(dest_path))
    return dest_path


def main() -> int:
    base_dir = get_base_dir()
    sorted_dir = base_dir / "sorted_by_type"
    sorted_dir.mkdir(exist_ok=True)

    print("📁 File Sorter by Type")
    print(f"Scanning directory: {base_dir}")
    print(f"Output directory: {sorted_dir}")
    print()
    print("📂 Categories:")
    for category, extensions in FILE_TYPE_CATEGORIES.items():
        sample_exts = list(extensions)[:5]  # Show first 5 extensions
        more = f" and {len(extensions) - 5} more" if len(extensions) > 5 else ""
        print(f"   • {category}: {', '.join(sample_exts)}{more}")
    print("   • Others: Files that don't match any category")

    # Exclude common output directories and system folders
    exclude_dirs = {
        'sorted_by_type',  # Our output directory
        'sorted_files',
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

    # Also exclude any existing sorted_by_type_* folders
    try:
        for item in base_dir.iterdir():
            if item.is_dir() and (item.name.startswith('sorted_by_type') or item.name.startswith('sorted_files')):
                exclude_dirs.add(item.name)
    except OSError:
        pass

    print(f"\n🚫 Excluding directories: {', '.join(sorted(exclude_dirs))}")

    # Scan for files
    print("\n🔍 Scanning for files...")
    all_files = list(iter_all_files(base_dir, exclude_dirs))

    if not all_files:
        print("No files found to sort.")
        if is_frozen():
            input(CLOSE_PROMPT)
        return 0

    # Group files by category for reporting
    files_by_category = defaultdict(list)
    total_size = 0

    for file_path in all_files:
        category = get_file_category(file_path)
        files_by_category[category].append(file_path)
        total_size += get_file_size_mb(file_path)

    # Show summary
    total_files = len(all_files)
    total_categories = len(files_by_category)

    print(f"\n📊 Found {total_files} files ({total_size:.1f} MB) in {total_categories} categories:")

    # Show categories with counts
    category_counts = [(cat, len(files)) for cat, files in files_by_category.items()]
    category_counts.sort(key=lambda x: x[1], reverse=True)

    for category, count in category_counts:
        percentage = (count / total_files) * 100
        size_mb = sum(get_file_size_mb(f) for f in files_by_category[category])
        print(f"   • {category}: {count} files ({percentage:.1f}%) - {size_mb:.1f} MB")

    # Ask for move/copy option
    move_files = False
    if is_frozen():
        print(f"\nThis will organize all files to subfolders in: {sorted_dir}")
        print("You can choose to either copy (preserve originals) or move (relocate) files.")
        while True:
            response = input("\nMove files instead of copying? (y/N): ").strip().lower()
            if response in ('y', 'yes'):
                move_files = True
                break
            elif response in ('n', 'no', ''):
                move_files = False
                break
            else:
                print("Please enter 'y' or 'n'.")
        print(f"\n{'Moving' if move_files else 'Copying'} files to organized subfolders...")
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm not in ('y', 'yes'):
            print("Operation cancelled.")
            input(CLOSE_PROMPT)
            return 0
    else:
        # For CLI, ask once at the start
        while True:
            response = input("\nMove files instead of copying? (y/N): ").strip().lower()
            if response in ('y', 'yes'):
                move_files = True
                break
            elif response in ('n', 'no', ''):
                move_files = False
                break
            else:
                print("Please enter 'y' or 'n'.")
        print(f"\n{'Moving' if move_files else 'Copying'} files to organized subfolders...")

    # Sort files
    copied_count = 0
    failed_count = 0

    for idx, file_path in enumerate(all_files, start=1):
        try:
            if idx % 50 == 0 or idx == total_files:
                print(f"   Progress: {idx}/{total_files} files processed", end='\r')

            move_or_copy_file_by_type(file_path, sorted_dir, move=move_files)
            copied_count += 1

        except Exception as e:
            failed_count += 1
            if failed_count <= 5:  # Show first few errors
                print(f"\n   ❌ Error {'moving' if move_files else 'copying'} {file_path.name}: {e}")

    print("\n\n✅ Sorting complete!")
    print(f"   Files {'moved' if move_files else 'copied'}: {copied_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Total size: {total_size:.1f} MB")

    # Show created folders
    try:
        created_folders = [f.name for f in sorted_dir.iterdir() if f.is_dir()]
        created_folders.sort()
        print(f"\n📁 Created {len(created_folders)} type folders:")
        for folder in created_folders:
            file_count = len(list((sorted_dir / folder).iterdir()))
            folder_size = sum(get_file_size_mb(f) for f in (sorted_dir / folder).iterdir())
            print(f"   • {folder}/ ({file_count} files, {folder_size:.1f} MB)")
    except Exception:
        pass

    print(f"\n📂 Sorted files location: {sorted_dir}")
    print(f"💡 Original files {'have been moved' if move_files else 'remain in their original locations'}")

    if failed_count > 0:
        print(f"\n⚠️  {failed_count} files could not be {'moved' if move_files else 'copied'} (permissions, locks, etc.)")

    # Show some insights
    print(f"\n📈 File Type Insights:")
    if "Images" in files_by_category:
        img_files = files_by_category["Images"]
        img_exts = defaultdict(int)
        for f in img_files:
            ext = f.suffix.lower()[1:] if f.suffix else "no_ext"
            img_exts[ext] += 1
        top_img = sorted(img_exts.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"   • Most common image formats: {', '.join(f'{ext} ({count})' for ext, count in top_img)}")

    if "Documents" in files_by_category:
        doc_files = files_by_category["Documents"]
        doc_size = sum(get_file_size_mb(f) for f in doc_files)
        print(f"   • Document collection: {len(doc_files)} files totaling {doc_size:.1f} MB")

    if "Media" in files_by_category:
        media_files = files_by_category["Media"]
        media_size = sum(get_file_size_mb(f) for f in media_files)
        print(f"   • Media collection: {len(media_files)} files totaling {media_size:.1f} MB")

    if is_frozen():
        print("\n" + "="*70)
        input(CLOSE_PROMPT)

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())