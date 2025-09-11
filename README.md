# Python Standalone Scripts Project

This project is set up to help you build Python scripts that can be used as standalone command-line tools.

## Structure

- `scripts/` — stand-alone scripts (run with `python scripts/<name>.py`).
- `src/mytools/` — installable package exposing CLI entry point `hello`.
- `pyproject.toml` — project metadata; defines the `hello` script.

## Prerequisites (Windows)

Install Python 3.10+ (include "Add python.exe to PATH"):

- Download: <https://www.python.org/downloads/windows/>
- Or via Microsoft Store: search "Python 3.x".

## Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Tip: If `python` is not found, reopen terminal after install or ensure PATH is set.

## Install the package in editable mode

```powershell
pip install -e .
```

This makes the `hello` command available while you develop.

## Try it

```powershell
# Run packaged CLI
hello

# Or run the sample script directly
python scripts/example_tool.py YourName
```

## NEF-to-JPG Converter

A standalone tool to convert NEF images to JPG with robust fallbacks.

### Setup

Install dependencies:

```powershell
pip install rawpy pillow
```

### Usage

Run as script (scans current folder):

```powershell
python scripts/nef_to_jpg.py
```

Options:

- `--mode auto|raw|embedded` (default: `auto`)
  - `auto`: try RAW decode first, then fall back to embedded JPEG if needed
  - `raw`: attempt only RAW decode (full, then half-size); fail if RAW not possible
  - `embedded`: extract embedded JPEG only (fast, works even if RAW decode fails)
- `--quality <1-100>` JPEG quality for saved images (default: 90)
- `--verbose` extra logging about which fallback is used

Examples:

```powershell
# Verbose auto-mode (recommended)
python scripts/nef_to_jpg.py --verbose

# Force raw-only (will fail if LibRaw cannot decode the NEF)
python scripts/nef_to_jpg.py --mode raw --verbose

# Force embedded-only (fast, ensures an output when RAW demosaic fails)
python scripts/nef_to_jpg.py --mode embedded --quality 92
```

Build and run EXE (drop into any folder with NEFs):

```powershell
pip install pyinstaller
& .\.venv\Scripts\pyinstaller.exe -F -n nef_to_jpg.exe -c -s -i NONE -p src --name nef_to_jpg scripts\nef_to_jpg.py
.\dist\nef_to_jpg.exe
```

The tool scans the current folder (and subfolders) for `.NEF` files, creates a `results/` folder with mirrored structure, converts to JPG (quality 90 by default), and preserves originals. If RAW decoding fails (driver/LibRaw limitations), the tool can extract the embedded JPEG to ensure an output.

## Photo Organizer by Date

A standalone tool to organize photos by their date into year/month folders.

### Photo Organizer Setup

Install dependencies (Pillow already included if you set up NEF converter):

```powershell
pip install pillow
```

### Photo Organizer Usage

Run as script:

```powershell
python scripts/organize_photos.py
```

Or build and run EXE (drop into any folder with photos):

```powershell
& .\.venv\Scripts\pyinstaller.exe -F -n organize_photos.exe -c -s -i NONE -p src --name organize_photos scripts\organize_photos.py
.\dist\organize_photos.exe
```

The tool scans for image files (JPG, PNG, NEF, CR2, etc.), reads EXIF date metadata (falls back to file modification date), and organizes them into `results/YYYY/MM-MonthName/` structure while preserving originals.

## Video Batch Compressor

A standalone tool to compress videos using FFmpeg with adjustable quality settings.

### Video Compressor Setup

#### Option 1: Self-contained EXE (Recommended)

Build with bundled FFmpeg (no separate installation needed):

```powershell
python build_video_compressor.py
```

This downloads FFmpeg automatically and creates `dist/video_compressor.exe` with everything bundled.

#### Option 2: Manual FFmpeg installation

Install FFmpeg separately:

- Download FFmpeg from: <https://ffmpeg.org/download.html>
- Extract and add to your system PATH, or place `ffmpeg.exe` in the same folder as the script/EXE

### Video Compressor Usage

Run as script:

```powershell
python scripts/video_compressor.py
```

Or run the self-contained EXE (drop into any folder with videos):

```powershell
.\dist\video_compressor.exe
```

The tool scans for video files (MP4, AVI, MOV, MKV, etc.), compresses them using H.264 with configurable quality (high/medium/low), and saves to `converted_videos/` folder while preserving originals. **The EXE includes FFmpeg - no separate installation required!**

## Duplicate File Finder Tool

A standalone tool to find duplicate files by hash and optionally move them to a timestamped folder for review.

### Duplicate Finder Tool Setup

No additional dependencies required (uses built-in Python libraries).

### Duplicate Finder Tool Usage

Run as script:

```powershell
python scripts/find_duplicates.py
```

Or build and run EXE (drop into any folder to scan):

```powershell
python build_find_duplicates.py
.\dist\find_duplicates.exe
```

The tool scans for all files recursively, calculates SHA-256 hashes to identify duplicates, shows detailed report with file sizes and paths, and optionally moves duplicates to `Duplicates_YYYYMMDD_HHMMSS/` folders while preserving one copy of each file.

## Battery Health Report Generator

A standalone tool that generates comprehensive battery health reports using Windows PowerCfg utility.

### Battery Report Tool Setup

No additional dependencies required (uses built-in Windows PowerCfg and Python libraries).

### Battery Report Tool Usage

Run as script:

```powershell
python scripts/battery_report.py
```

Or build and run EXE (drop into any folder):

```powershell
python build_battery_report.py
.\dist\battery_report.exe
```

**For full report details, run as administrator:**

- Right-click `battery_report.exe` → "Run as administrator"

The tool generates `Battery_Report_YYYYMMDD_HHMMSS.html` with enhanced styling, automatically opens it in your web browser, and includes battery design vs current capacity, charge cycles, usage history, power settings, and battery life estimates. **Windows only - requires laptop/tablet with battery.**

## JavaScript Development Environment Setup

A standalone tool that sets up a complete JavaScript development environment on a clean Windows PC.

### JS Dev Setup Tool Requirements

**IMPORTANT: Requires administrator privileges for software installation.**

### JS Dev Setup Tool Usage

**Must run as administrator:**

```powershell
python build_js_dev_setup.py
# Right-click dist/js_dev_setup.exe → "Run as administrator"
```

### Tools Installed

The setup tool automatically installs and configures:

- **NVM for Windows** - Node Version Manager for easy Node.js version switching
- **Node.js LTS** - Latest Long Term Support version via NVM
- **Git for Windows** - Version control with Bash integration
- **Visual Studio Code** - Code editor with recommended extensions
- **Google Chrome** - Browser for development and debugging
- **Windows Terminal** - Modern terminal experience

### VS Code Configuration

Automatically configures VS Code with:

- Recommended settings for JavaScript development
- Proper formatting and auto-save settings
- Git integration enabled

**Note:** Extensions are not automatically installed. You can install them manually from VS Code's Extensions marketplace after setup.

**Drop-and-run usage:** Copy `js_dev_setup.exe` to any Windows PC, right-click → "Run as administrator", and get a fully configured JavaScript development environment in minutes!

## Duplicate File Finder

A standalone tool to find duplicate files by hash and optionally move them to a timestamped folder for review.

### Duplicate Finder Setup

No additional dependencies needed (uses built-in Python libraries).

### Duplicate Finder Usage

Run as script:

```powershell
python scripts/find_duplicates.py
```

Or build and run EXE (drop into any folder to scan):

```powershell
python build_find_duplicates.py
# or manual build:
& .\.venv\Scripts\pyinstaller.exe --onefile --console --name find_duplicates --distpath dist scripts/find_duplicates.py
.\dist\find_duplicates.exe
```

The tool scans the current folder (and subfolders) for duplicate files using SHA-256 hash comparison, excludes common output directories, shows duplicate sets with file paths and sizes, and optionally moves duplicates to `Duplicates_YYYYMMDD_HHMMSS/` folder for manual review. Preserves one copy of each file in the original location.

## Optional: Use pipx to install globally (isolated)

```powershell
pip install --user pipx
pipx ensurepath
# Reopen terminal, then:
pipx install .
# Now `hello` is available on your PATH
```

## Optional: Build a single-file EXE with PyInstaller

```powershell
pip install pyinstaller
& .\.venv\Scripts\pyinstaller.exe -F -n hello.exe -c -s -i NONE -p src --name hello hello_entry.py
# or
python -m PyInstaller -F -n hello.exe -c -s -i NONE -p src --name hello hello_entry.py
# Result in dist\hello.exe
```

## VS Code task

A task "Run example_tool.py" is provided. After Python install and venv activation, run it from Terminal > Run Task.

---

Update this README as your project evolves.
