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

A standalone tool to convert NEF images to JPG.

### Setup

Install dependencies:

```powershell
pip install rawpy pillow
```

### Usage

Run as script:

```powershell
python scripts/nef_to_jpg.py
```

Or build and run EXE (drop into any folder with NEFs):

```powershell
pip install pyinstaller
& .\.venv\Scripts\pyinstaller.exe -F -n nef_to_jpg.exe -c -s -i NONE -p src --name nef_to_jpg scripts\nef_to_jpg.py
.\dist\nef_to_jpg.exe
```

The tool scans the current folder (and subfolders) for .NEF files, creates a `results` folder with mirrored structure, converts to JPG (quality 90), and preserves originals.

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
