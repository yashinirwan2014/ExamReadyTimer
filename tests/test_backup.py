from pathlib import Path
import zipfile

import pytest

from backup import backup_data, restore_data


def test_backup_and_restore_round_trip(tmp_path):
    data = tmp_path / "user-data"
    data.mkdir()
    (data / "dataexams.csv").write_text("Exam,Year,Month,Day\nMock,2027,2,3\n", encoding="utf-8")
    (data / "datatimetable.csv").write_text("Day,Subject\nMonday,Physics\n", encoding="utf-8")
    (data / "dataorsubjects.csv").write_text("Subject,Chapter,Status\nPhysics,Optics,Completed\n", encoding="utf-8")
    (data / ".reminders-sent.json").write_text('["physics|2027-02-03"]', encoding="utf-8")
    (data / "study_sessions.csv").write_text("date,minutes,subject\n2026-11-08,45,Physics\n", encoding="utf-8")
    (data / "revision_schedule.csv").write_text("subject,chapter,due_date\nPhysics,Optics,2026-11-09\n", encoding="utf-8")
    archive = tmp_path / "backup.zip"

    backup_data(archive, data)
    (data / "dataexams.csv").write_text("Exam,Year,Month,Day\n", encoding="utf-8")
    restored = restore_data(archive, data)

    assert set(restored) == {"dataexams.csv", "datatimetable.csv", "dataorsubjects.csv", ".reminders-sent.json", "study_sessions.csv", "revision_schedule.csv"}
    assert "Physics" in (data / "study_sessions.csv").read_text(encoding="utf-8")
    assert "Optics" in (data / "revision_schedule.csv").read_text(encoding="utf-8")
    assert "physics|2027-02-03" in (data / ".reminders-sent.json").read_text(encoding="utf-8")
    assert "Mock" in (data / "dataexams.csv").read_text(encoding="utf-8")


def test_restore_rejects_zip_slip_and_unknown_files(tmp_path):
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("../outside.csv", "unsafe")
        stream.writestr("other.txt", "not app data")
    with pytest.raises(ValueError):
        restore_data(archive, tmp_path / "user-data")
    assert not (tmp_path / "outside.csv").exists()


def test_restore_rejects_duplicate_data_entries(tmp_path):
    archive = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("dataexams.csv", "Exam,Year,Month,Day\n")
        stream.writestr("dataexams.csv", "different")
    with pytest.raises(ValueError):
        restore_data(archive, tmp_path / "user-data")


def test_restore_validates_entire_archive_before_changing_existing_data(tmp_path):
    data = tmp_path / "user-data"
    data.mkdir()
    existing = data / "dataexams.csv"
    existing.write_text("Exam,Year\\nExisting,2027\\n", encoding="utf-8")

    archive = tmp_path / "mixed-unsafe.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("dataexams.csv", "Exam,Year\\nReplacement,2028\\n")
        stream.writestr("../outside.txt", "unsafe")

    with pytest.raises(ValueError, match="unsupported entry"):
        restore_data(archive, data)
    assert existing.read_text(encoding="utf-8") == "Exam,Year\\nExisting,2027\\n"
    assert not (tmp_path / "outside.txt").exists()


def test_restore_rejects_corrupt_archive_without_partial_changes(tmp_path):
    data = tmp_path / "user-data"
    data.mkdir()
    existing = data / "dataexams.csv"
    existing.write_text("Exam,Year\\nExisting,2027\\n", encoding="utf-8")

    archive = tmp_path / "corrupt.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("dataexams.csv", "Exam,Year\\nReplacement,2028\\n")
        stream.writestr("datatimetable.csv", "Day,Subject\\nMonday,Physics\\n")
    raw = bytearray(archive.read_bytes())
    raw[-12] ^= 0xFF
    archive.write_bytes(raw)

    with pytest.raises((zipfile.BadZipFile, ValueError)):
        restore_data(archive, data)
    assert existing.read_text(encoding="utf-8") == "Exam,Year\\nExisting,2027\\n"
