"""Portable per-user data storage for ExamReadyTimer.

Bundled CSV files are treated as starter data only. Editable copies live in
the operating system's per-user application data directory, so upgrades do
not overwrite student progress and installs need not be writable.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

APP_NAME = "ExamReadyTimer"
DATA_FILES = ("dataorsubjects.csv", "dataexams.csv", "datatimetable.csv", "study_sessions.csv", "revision_schedule.csv")


def get_user_data_dir(app_name: str = APP_NAME) -> Path:
    """Return the conventional per-user data directory for this platform."""
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or home / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share")
    return base / app_name


def initialize_user_data(
    app_dir: str | Path | None = None,
    data_dir: str | Path | None = None,
    filenames: tuple[str, ...] = DATA_FILES,
) -> Path:
    """Create the user data directory and seed only files not already present."""
    if app_dir is None:
        app_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    source_dir = Path(app_dir)
    destination_dir = Path(data_dir) if data_dir is not None else get_user_data_dir()
    destination_dir.mkdir(parents=True, exist_ok=True)

    for filename in filenames:
        source = source_dir / filename
        destination = destination_dir / filename
        if not destination.exists() and source.is_file():
            shutil.copy2(source, destination)

    return destination_dir


def get_data_path(filename: str, data_dir: str | Path | None = None) -> Path:
    """Return a path to an app data file in the per-user data directory."""
    if Path(filename).name != filename:
        raise ValueError("Data filename must not contain directory components.")
    return (Path(data_dir) if data_dir is not None else get_user_data_dir()) / filename
