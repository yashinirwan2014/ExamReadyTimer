""""Real Tk widget interaction tests for the student-facing workflows.

Run on Linux with a display server, e.g.:
    xvfb-run --auto-servernum python -m pytest -q tests/test_gui_interactions.py
"""
import csv
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
import zipfile

import pytest

import GUI
import countdown
import focus
import pomodoro
import progress
import readiness
import settings
import studyhub
import timetable
import tracker


@pytest.fixture
def root():
    # The dedicated GUI job runs on Linux under Xvfb. Keep the portable
    # unit-test matrix display-independent on Windows/macOS and local shells.
    if sys.platform != "linux" or not os.environ.get("DISPLAY"):
        pytest.skip("GUI interaction tests run in the Linux/Xvfb workflow job.")
    try:
        window = tk.Tk()
    except tk.TclError as exc:
        pytest.skip(f"Tk display is unavailable: {exc}")
    window.withdraw()
    yield window
    try:
        window.destroy()
    except tk.TclError:
        pass


def button(parent, label):
    """Find a real Tk/ttk button by its visible label."""
    for child in parent.winfo_children():
        if isinstance(child, (tk.Button, ttk.Button)) and str(child.cget("text")) == label:
            return child
        found = button(child, label)
        if found is not None:
            return found
    return None


def click(parent, label):
    control = button(parent, label)
    assert control is not None, f"Visible button {label!r} was not built"
    control.invoke()
    parent.update_idletasks()


def silence_dialogs(monkeypatch, module):
    for name in ("showinfo", "showwarning", "showerror", "askyesno"):
        if hasattr(module.messagebox, name):
            monkeypatch.setattr(module.messagebox, name,
                                (lambda *args, **kwargs: True) if name == "askyesno"
                                else (lambda *args, **kwargs: None))


def write_subjects(path):
    path.write_text(
        "Subject,Chapter,Status\\nPhysics,Ray Optics,Pending\\n",
        encoding="utf-8",
    )


def test_dashboard_feature_buttons_launch_each_window(root, tmp_path, monkeypatch):
    monkeypatch.setattr(GUI, "USER_DATA_DIR", tmp_path)
    launched = []
    monkeypatch.setattr(GUI.subprocess, "Popen",
                        lambda command, cwd: launched.append((command, cwd)))
    GUI.build_dashboard(root)

    # Keep these labels in sync with the names actually shown on the dashboard.
    features = [
        ("Exam Readiness Check", "readiness.py"),
        ("Study Sessions & Revision", "studyhub.py"),
        ("Exam Countdown", "countdown.py"),
        ("Pomodoro Timer", "pomodoro.py"),
        ("Study Timetable", "timetable.py"),
        ("Subject Tracker", "tracker.py"),
        ("Progress Overview", "progress.py"),
        ("Focus Mode", "focus.py"),
        ("Settings & Backup", "settings.py"),
    ]
    for label, filename in features:
        click(root, label)

    assert len(launched) == len(features)
    assert [item[0][-1] for item in launched] == [
        str(GUI.APP_DIR / filename) for _, filename in features
    ]
    assert all(cwd == str(tmp_path) for _, cwd in launched)


def test_exam_planner_add_and_delete_through_buttons(root, tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(countdown, "DATA_DIR", data)
    monkeypatch.setattr(countdown, "DATA_FILE", data / "dataexams.csv")
    silence_dialogs(monkeypatch, countdown)

    app = countdown.ExamCountdown(root)
    app.name_var.set("Interaction test exam")
    app.date_var.set((date.today() + timedelta(days=40)).isoformat())
    app.subject_var.set("Physics")
    click(root, "Add exam")

    assert len(countdown.read_exams()) == 1
    row = app.table.get_children()[0]
    app.table.selection_set(row)
    click(root, "Delete selected exam")
    assert countdown.read_exams() == []


def test_timetable_add_complete_and_delete_through_buttons(root, tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(timetable, "DATA_DIR", data)
    monkeypatch.setattr(timetable, "DATA_FILE", data / "datatimetable.csv")
    silence_dialogs(monkeypatch, timetable)

    app = timetable.StudyTimetable(root)
    app.subject_var.set("Physics — Ray Optics")
    app.start_var.set("09:00")
    app.end_var.set("10:00")
    click(root, "Add block")
    assert len(timetable.load_plans()) == 1

    app.table.selection_set(app.table.get_children()[0])
    click(root, "Mark complete / planned")
    assert timetable.load_plans()[0]["status"] == "Completed"

    app.table.selection_set(app.table.get_children()[0])
    click(root, "Delete selected")
    assert timetable.load_plans() == []


def test_syllabus_tracker_full_crud_through_buttons(root, tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(tracker, "DATA_DIR", data)
    monkeypatch.setattr(tracker, "DATA_FILE", data / "dataorsubjects.csv")
    silence_dialogs(monkeypatch, tracker)
    answers = iter(["Physics", "Ray Optics", "Ray Optics - Updated", "Physics II"])
    monkeypatch.setattr(tracker.simpledialog, "askstring",
                        lambda *args, **kwargs: next(answers))
    app = tracker.SyllabusTracker(root)

    click(root, "+ Add subject")
    assert "Physics" in tracker.load_subjects()

    click(root, "+ Add chapter")
    assert any(x["chapter"] == "Ray Optics"
               for x in tracker.load_subjects()["Physics"])

    row = next(iid for iid in app.chapter_table.get_children()
               if app.chapter_table.item(iid, "values")[1] == "Ray Optics")
    app.chapter_table.selection_set(row)
    click(root, "Edit")
    assert any(x["chapter"] == "Ray Optics - Updated"
               for x in tracker.load_subjects()["Physics"])

    row = next(iid for iid in app.chapter_table.get_children()
               if app.chapter_table.item(iid, "values")[1] == "Ray Optics - Updated")
    app.chapter_table.selection_set(row)
    click(root, "Mark complete / pending")
    assert next(x for x in tracker.load_subjects()["Physics"]
                if x["chapter"] == "Ray Optics - Updated")["status"] == "Completed"

    row = app.chapter_table.get_children()[0]
    app.chapter_table.selection_set(row)
    click(root, "Delete")
    assert all(x["chapter"] != "Ray Optics - Updated"
               for x in tracker.load_subjects()["Physics"])

    click(root, "Rename subject")
    assert "Physics II" in tracker.load_subjects()
    assert "Physics" not in tracker.load_subjects()

    click(root, "Delete subject")
    assert "Physics II" not in tracker.load_subjects()


def test_dashboard_import_is_headless_and_has_no_storage_side_effects(tmp_path):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_home = tmp_path / "xdg-data"
    env = os.environ.copy()
    env.pop("DISPLAY", None)
    env["HOME"] = str(tmp_path)
    env["XDG_DATA_HOME"] = str(data_home)
    env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-c",
         "import GUI; assert GUI.USER_DATA_DIR is None"],
        cwd=repo_root, env=env, text=True, capture_output=True, timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (data_home / "ExamReadyTimer").exists()


@pytest.mark.parametrize("module,klass,minutes_attr,session_type", [
    (pomodoro, pomodoro.PomodoroTimer, "study_minutes", "Pomodoro"),
    (focus, focus.FocusMode, "minutes", "Focus"),
])
def test_timer_start_pause_and_completed_session_button_paths(
        root, tmp_path, monkeypatch, module, klass, minutes_attr, session_type):
    data = tmp_path / session_type.lower()
    data.mkdir()
    monkeypatch.setattr(module, "DATA_DIR", data)
    monkeypatch.setattr(module, "SESSION_FILE", data / "study_sessions.csv")
    monkeypatch.setattr(module, "REVISION_FILE", data / "revision_schedule.csv")
    monkeypatch.setattr(module, "SUBJECT_FILE", data / "dataorsubjects.csv")
    write_subjects(data / "dataorsubjects.csv")
    silence_dialogs(monkeypatch, module)

    app = klass(root)
    app.subject_var.set("Physics")
    app.chapter_var.set("Ray Optics")
    if module is pomodoro:
        app.total_sessions.set(1)
    click(root, "Start")
    assert app.running is True
    click(root, "Pause")
    assert app.running is False

    # Complete the same timer through its real completion handler without
    # waiting a full minute in CI.
    app.remaining = 0
    app.tick()
    with (data / "study_sessions.csv").open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["subject"] == "Physics"
    assert rows[0]["chapter"] == "Ray Optics"
    assert rows[0]["session_type"] == session_type


def test_settings_backup_and_restore_buttons(root, tmp_path, monkeypatch):
    data = tmp_path / "user-data"
    data.mkdir()
    monkeypatch.setattr(settings, "DATA_DIR", data)
    silence_dialogs(monkeypatch, settings)
    original = data / "dataexams.csv"
    original.write_text("Exam,Year\\nOriginal,2027\\n", encoding="utf-8")
    archive = tmp_path / "ExamReadyTimer-Backup.zip"
    monkeypatch.setattr(settings.filedialog, "asksaveasfilename",
                        lambda **kwargs: str(archive))
    monkeypatch.setattr(settings.filedialog, "askopenfilename",
                        lambda **kwargs: str(archive))

    settings.SettingsWindow(root)
    click(root, "Create backup")
    assert archive.is_file()
    with zipfile.ZipFile(archive) as saved:
        assert "dataexams.csv" in saved.namelist()

    original.write_text("Exam,Year\\nChanged,2028\\n", encoding="utf-8")
    click(root, "Restore backup")
    assert "Original" in original.read_text(encoding="utf-8")


def test_study_intelligence_save_session_and_generate_plan(root, tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    subjects = data / "dataorsubjects.csv"
    write_subjects(subjects)
    exams = data / "dataexams.csv"
    exams.write_text("Exam,Year,Month,Day,Subject,Priority\\n",
                     encoding="utf-8")
    monkeypatch.setattr(studyhub, "DATA_DIR", data)
    monkeypatch.setattr(studyhub, "SESSION_FILE", data / "study_sessions.csv")
    monkeypatch.setattr(studyhub, "REVISION_FILE", data / "revision_schedule.csv")
    monkeypatch.setattr(studyhub, "SUBJECT_FILE", subjects)
    monkeypatch.setattr(studyhub, "EXAM_FILE", exams)
    monkeypatch.setattr(studyhub, "TIMETABLE_FILE", data / "datatimetable.csv")
    silence_dialogs(monkeypatch, studyhub)

    app = studyhub.StudyIntelligence(root)
    app.subject_var.set("Physics")
    app.chapter_var.set("Ray Optics")
    app.minutes_var.set("35")
    click(root, "Save completed session")

    sessions = studyhub.load_sessions(data / "study_sessions.csv")
    assert len(sessions) == 1
    assert sessions[0]["minutes"] == 35
    assert sessions[0]["chapter"] == "Ray Optics"

    click(root, "Generate adaptive plan")
    planned = [app.plan_table.item(iid, "values")
               for iid in app.plan_table.get_children()]
    assert any(row[0] == "Physics" and row[1] == "Ray Optics"
               for row in planned)


def test_readiness_and_progress_refresh_buttons_render_data(root, tmp_path, monkeypatch):
    silence_dialogs(monkeypatch, readiness)
    monkeypatch.setattr(readiness, "load_exam_data", lambda: [{
        "name": "Physics", "subject": "Physics",
        "date": date.today() + timedelta(days=10), "priority": "High"
    }])
    monkeypatch.setattr(readiness, "load_syllabus_data", lambda: {
        "Physics": {"total": 4, "completed": 2, "pending": 2}
    })
    dashboard = readiness.ReadinessDashboard(root)
    click(root, "Recalculate")
    assert dashboard.table.get_children()
    assert "1 upcoming exams" in dashboard.summary.cget("text")

    monkeypatch.setattr(progress, "calculate_progress", lambda: {
        "Physics": {"total": 4, "completed": 2, "percentage": 50.0}
    })
    analytics = progress.ProgressAnalytics(root)
    click(root, "Refresh progress")
    assert "2 of 4 chapters completed" in analytics.summary.cget("text")
