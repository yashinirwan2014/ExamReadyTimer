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
    """Validate and stage a backup completely before replacing any user data."""
    folder = initialize_user_data(data_dir=data_dir)

    # Read and validate the complete archive before touching existing files.
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        safe_members: list[str] = []
        seen: set[str] = set()
        for info in archive.infolist():
            name = info.filename
            if info.is_dir() or name not in BACKUP_FILES:
                raise ValueError(f"Backup contains an unsupported entry: {name}")
            if name in seen:
                raise ValueError(f"Backup contains duplicate entry: {name}")
            seen.add(name)
            safe_members.append(name)

        if not safe_members:
            raise ValueError("This ZIP does not contain any ExamReadyTimer data files.")

        damaged = archive.testzip()
        if damaged is not None:
            raise ValueError(f"Backup contains a damaged file: {damaged}")

        contents = {name: archive.read(name) for name in safe_members}

    staged: dict[str, Path] = {}
    backups: dict[str, Path] = {}
    committed: list[str] = []
    try:
        # Stage every replacement first. A disk/write error here leaves live
        # data untouched.
        for filename, content in contents.items():
            target = folder / filename
            temporary = target.with_name(target.name + ".restore-tmp")
            temporary.unlink(missing_ok=True)
            temporary.write_bytes(content)
            staged[filename] = temporary

        # Keep originals until every staged file has been installed. If a
        # replacement fails, restore the originals before propagating the error.
        for filename in safe_members:
            target = folder / filename
            if target.exists():
                previous = target.with_name(target.name + ".restore-backup")
                previous.unlink(missing_ok=True)
                target.replace(previous)
                backups[filename] = previous
            staged[filename].replace(target)
            committed.append(filename)
    except Exception:
        for filename in reversed(committed):
            (folder / filename).unlink(missing_ok=True)
        for filename, previous in backups.items():
            if previous.exists():
                previous.replace(folder / filename)
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)
        for previous in backups.values():
            previous.unlink(missing_ok=True)

    return safe_members
