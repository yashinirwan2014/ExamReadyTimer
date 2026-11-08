"""Safe ZIP backup and restore helpers for ExamReadyTimer user data."""
from __future__ import annotations

from pathlib import Path
import zipfile

from storage import DATA_FILES, initialize_user_data

BACKUP_FILES = DATA_FILES + (".reminders-sent.json",)


def backup_data(destination: str | Path, data_dir: str | Path | None = None) -> Path:
    folder = initialize_user_data(data_dir=data_dir)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in BACKUP_FILES:
            source = folder / filename
            if source.is_file():
                archive.write(source, arcname=filename)
    return destination


def restore_data(archive_path: str | Path, data_dir: str | Path | None = None) -> list[str]:
    folder = initialize_user_data(data_dir=data_dir)
    restored = []
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        safe_members = {}
        for name in names:
            # Only exact known app data filenames are accepted; no directory paths.
            if name in BACKUP_FILES:
                if name in safe_members:
                    raise ValueError(f"Backup contains duplicate entry: {name}")
                safe_members[name] = name
        if not safe_members:
            raise ValueError("This ZIP does not contain any ExamReadyTimer data files.")
        for filename in safe_members:
            content = archive.read(filename)
            target = folder / filename
            temporary = target.with_suffix(target.suffix + ".restore-tmp")
            temporary.write_bytes(content)
            temporary.replace(target)
            restored.append(filename)
    return restored
