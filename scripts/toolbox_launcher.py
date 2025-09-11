"""Unified Toolbox Launcher

A Tkinter-based GUI that exposes buttons for each available standalone tool.
Supports running as a script or packaged EXE.

Behavior:
- Each button launches the corresponding script in a separate subprocess (isolated).
- Working directory = directory where the EXE/script is located (drop-and-run friendly).
- Provides status area and minimal logging inside the UI.
- Adds --run-tool internal argument to allow recursion or potential direct module dispatch later.

Dependencies: Only standard library (Tkinter is bundled with CPython on Windows).
"""
from __future__ import annotations

import sys
import subprocess
import threading
import queue
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Callable
import importlib.util
import importlib

# Detect packaged mode
IS_FROZEN = getattr(sys, "frozen", False)
BASE_DIR = Path(sys.executable).parent if IS_FROZEN else Path.cwd()
SCRIPTS_DIR = BASE_DIR / "scripts"

# When frozen, PyInstaller places code under a temp dir accessible via sys._MEIPASS
MEIPASS_DIR = Path(getattr(sys, '_MEIPASS', BASE_DIR))

# Allow import of scripts as a package when bundled
if IS_FROZEN:
    if str(MEIPASS_DIR) not in sys.path:
        sys.path.insert(0, str(MEIPASS_DIR))
    # Also attempt to add scripts dir if it exists inside MEIPASS
    embedded_scripts = MEIPASS_DIR / 'scripts'
    if embedded_scripts.exists():
        if str(embedded_scripts) not in sys.path:
            sys.path.insert(0, str(embedded_scripts))

# Tool registry: key -> dict(meta)
TOOLS: Dict[str, Dict[str, str]] = {
    "nef_to_jpg": {"label": "NEF → JPG Converter", "script": "nef_to_jpg.py", "module": "scripts.nef_to_jpg", "desc": "Convert RAW/NEF images to JPG (parallel in CLI)."},
    "organize_photos": {"label": "Photo Organizer by Date", "script": "organize_photos.py", "module": "scripts.organize_photos", "desc": "Organize photos into year/month folders."},
    "video_compressor": {"label": "Video Batch Compressor", "script": "video_compressor.py", "module": "scripts.video_compressor", "desc": "Compress videos to smaller sizes (FFmpeg)."},
    "find_duplicates": {"label": "Duplicate File Finder", "script": "find_duplicates.py", "module": "scripts.find_duplicates", "desc": "Find duplicate files by hash (SHA-256)."},
    "battery_report": {"label": "Battery Health Report", "script": "battery_report.py", "module": "scripts.battery_report", "desc": "Generate Windows battery analysis report."},
    "sort_by_extension": {"label": "Sort Files by Extension", "script": "sort_by_extension.py", "module": "scripts.sort_by_extension", "desc": "Copy files into folders per extension."},
    "sort_by_type": {"label": "Sort Files by Type", "script": "sort_by_type.py", "module": "scripts.sort_by_type", "desc": "Organize files by broad categories (Docs, Media...)."},
    "example_tool": {"label": "Example Tool", "script": "example_tool.py", "module": "scripts.example_tool", "desc": "Demo argument echo tool."},
}

LOG_MAX_LINES = 500

class LauncherGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Standalone Tools Launcher")
        self.root.geometry("780x520")
        self.root.minsize(680, 480)
        self.processes = []  # Track subprocess PIDs
        self.log_queue: queue.Queue[str] = queue.Queue()

        self._build_ui()
        self._schedule_log_pump()

    def _build_ui(self):
        # Top frame with title
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=10, pady=8)
        ttk.Label(header, text="Standalone Tools Launcher", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(header, text="Working Folder", command=self._open_folder_dialog).pack(side="right")

        # Tools frame (scrollable)
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=(0,8))

        canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        scroll_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.tools_frame = ttk.Frame(canvas)
        self.tools_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0,0), window=self.tools_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Populate tools
        for key, meta in TOOLS.items():
            self._add_tool_row(key, meta)

        # Log frame
        log_frame = ttk.LabelFrame(self.root, text="Activity Log")
        log_frame.pack(fill="both", expand=False, padx=10, pady=(0,8))
        self.log_text = tk.Text(log_frame, height=10, wrap="word", state="disabled", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)

        # Footer
        footer = ttk.Frame(self.root)
        footer.pack(fill="x", padx=10, pady=(0,8))
        ttk.Button(footer, text="Exit", command=self.root.quit).pack(side="right")
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(footer, textvariable=self.status_var).pack(side="left")

    def _add_tool_row(self, key: str, meta: Dict[str, str]):
        frame = ttk.Frame(self.tools_frame)
        frame.pack(fill="x", pady=4)

        btn = ttk.Button(frame, text=meta["label"], width=28,
                          command=lambda k=key: self.launch_tool(k))
        btn.pack(side="left")

        desc = ttk.Label(frame, text=meta.get("desc", ""), anchor="w")
        desc.pack(side="left", fill="x", expand=True, padx=10)

    def _append_log(self, text: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text.rstrip() + "\n")
        # Trim
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > LOG_MAX_LINES:
            self.log_text.delete('1.0', f"{lines-LOG_MAX_LINES}.0")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _schedule_log_pump(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                self._append_log(line)
        except queue.Empty:
            pass
        self.root.after(200, self._schedule_log_pump)

    def _open_folder_dialog(self):
        folder = filedialog.askdirectory(initialdir=str(BASE_DIR))
        if folder:
            self.log_queue.put(f"[info] Selected folder (no effect yet): {folder}")

    def launch_tool(self, key: str):
        meta = TOOLS[key]
        self.status_var.set(f"Launching {meta['label']}...")
        self.log_queue.put(f"[launch] {meta['label']}")

        if IS_FROZEN:
            # Try import first (module must be included by PyInstaller)
            module_name = meta.get('module')
            if module_name:
                try:
                    module = importlib.import_module(module_name)
                    run_func = getattr(module, 'main', None)
                    if callable(run_func):
                        threading.Thread(target=lambda: self._run_module_entry(run_func, meta['label']), daemon=True).start()
                        self.log_queue.put(f"[module] Imported & running: {module_name}")
                        return
                except Exception as e:
                    self.log_queue.put(f"[import-error] {module_name}: {e}")
            # If import fails, inform user (cannot rely on external python in pure single EXE)
            messagebox.showerror("Unavailable", f"Could not import tool module: {module_name}\nThe script may not have been bundled.")
            self.status_var.set("Import failed.")
            return

        # Non-frozen: run via subprocess (keeps isolation and console output in separate window)
        script_path = (SCRIPTS_DIR / meta['script']).resolve()
        if not script_path.exists():
            messagebox.showerror("Missing", f"Script not found: {script_path}")
            return
        try:
            proc = subprocess.Popen([sys.executable, str(script_path)], cwd=str(BASE_DIR))
            self.processes.append(proc)
            self.log_queue.put(f"[pid {proc.pid}] started -> {script_path.name}")
            threading.Thread(target=self._watch_process, args=(proc, meta['label']), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Launch Error", f"Failed to start: {e}")
            self.status_var.set("Launch failed")
            return

    def _watch_process(self, proc: subprocess.Popen, label: str):
        rc = proc.wait()
        self.log_queue.put(f"[pid {proc.pid}] {label} exited with code {rc}")
        self.status_var.set(f"Finished: {label} (code {rc})")

    def _run_module_entry(self, func: Callable, label: str):
        try:
            # Redirect stdin, stdout, stderr to prevent "lost sys.std*" errors in GUI context
            import io
            original_stdin = sys.stdin
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            # Provide mock input that simulates user pressing Enter or answering 'y' to prompts
            # Most tools ask for confirmation - we'll auto-confirm since user clicked the button
            mock_inputs = "y\n" * 10  # Provide multiple 'y' responses for any confirmation prompts
            sys.stdin = io.StringIO(mock_inputs)
            
            captured_output = io.StringIO()
            sys.stdout = captured_output
            sys.stderr = captured_output
            
            rc = func()
            
            # Log any captured output (truncate if too long)
            output_text = captured_output.getvalue()
            if output_text.strip():
                # Truncate long output for UI display
                if len(output_text) > 500:
                    output_text = output_text[:500] + "...[truncated]"
                self.log_queue.put(f"[output] {label}: {output_text.strip()}")
                
        except SystemExit as se:
            rc = int(se.code) if hasattr(se, 'code') and se.code is not None else 0
        except Exception as e:
            self.log_queue.put(f"[error] {label} crashed: {e}")
            self.status_var.set(f"Error: {label}")
            return
        finally:
            # Restore original streams
            sys.stdin = original_stdin
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
        self.log_queue.put(f"[module] {label} finished with code {rc}")
        self.status_var.set(f"Finished: {label} (code {rc})")


def main() -> int:
    # Internal dispatch option placeholder (future use)
    if '--run-tool' in sys.argv:
        # Could implement direct import dispatch here if desired
        print("Direct dispatch not yet implemented.")
        return 1

    root = tk.Tk()
    LauncherGUI(root)
    root.mainloop()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
