import os
from pathlib import Path

from storage import get_data_path, get_user_data_dir, initialize_user_data


def test_user_data_dir_respects_xdg_override(monkeypatch, tmp_path):
    monkeypatch.setattr("storage.sys.platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    assert get_user_data_dir() == tmp_path / "xdg" / "ExamReadyTimer"


def test_initialize_copies_seed_files_only_once(tmp_path):
    app_dir = tmp_path / "app"
    user_dir = tmp_path / "user"
    app_dir.mkdir()
    (app_dir / "dataexams.csv").write_text("Exam,Year,Month,Day\n", encoding="utf-8")

    result = initialize_user_data(app_dir=app_dir, data_dir=user_dir, filenames=("dataexams.csv",))
    target = result / "dataexams.csv"
    assert target.read_text(encoding="utf-8") == "Exam,Year,Month,Day\n"

    target.write_text("Exam,Year,Month,Day\nMy exam,2027,3,1\n", encoding="utf-8")
    (app_dir / "dataexams.csv").write_text("Exam,Year,Month,Day\nNew starter row\n", encoding="utf-8")
    initialize_user_data(app_dir=app_dir, data_dir=user_dir, filenames=("dataexams.csv",))
    assert "My exam" in target.read_text(encoding="utf-8")


def test_get_data_path_rejects_directory_traversal(tmp_path):
    try:
        get_data_path("../outside.csv", data_dir=tmp_path)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected unsafe filename to be rejected")
