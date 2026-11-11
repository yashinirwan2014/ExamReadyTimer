"""Shared navigation helpers for ExamReadyTimer feature windows."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

def dashboard_command(app_dir=None, frozen=None):
    """Return the correct dashboard launch command for source and packaged builds."""
    folder = Path(app_dir) if app_dir is not None else APP_DIR
    is_frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    if is_frozen:
        executable = folder / ("ExamReadyTimer.exe" if sys.platform == "win32" else "ExamReadyTimer")
        return [str(executable)]
    return [sys.executable, str(folder / "main.py")]

def add_home_button(root, before_home=None):
    """Add a Back to Home control without changing stored study data."""
    bar = tk.Frame(root, bg="#080808", padx=12, pady=8)
    bar.pack(fill="x", side="top")
    button = ttk.Button(bar, text="← Back to Home", command=lambda: _go_home(root, before_home))
    button.pack(side="left")
    return button

def _go_home(root, before_home=None):
    if before_home is not None:
        before_home()
    else:
        root.destroy()
    subprocess.Popen(dashboard_command(), cwd=str(Path.home()))
