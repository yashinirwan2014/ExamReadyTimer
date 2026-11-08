from datetime import date

import csv

import focus
import pomodoro
import studyhub
from study_engine import load_due_revisions, load_sessions


class Value:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def read_csv(path):
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_pomodoro_completed_block_is_saved_to_session_ledger(tmp_path, monkeypatch):
    sessions = tmp_path / "sessions.csv"
    revisions = tmp_path / "revisions.csv"
    monkeypatch.setattr(pomodoro, "SESSION_FILE", sessions)
    monkeypatch.setattr(pomodoro, "REVISION_FILE", revisions)

    timer = pomodoro.PomodoroTimer.__new__(pomodoro.PomodoroTimer)
    timer.subject_var = Value("Physics")
    timer.chapter_var = Value("Ray Optics")
    timer.phase_duration_seconds = 25 * 60
    timer.root = object()

    timer.record_study_block()

    saved = load_sessions(sessions)
    assert len(saved) == 1
    assert saved[0]["session_type"] == "Pomodoro"
    assert saved[0]["subject"] == "Physics"
    assert saved[0]["chapter"] == "Ray Optics"
    assert saved[0]["minutes"] == 25
    due = load_due_revisions(revisions, date.max)
    assert len(due) == 5
    assert {row["chapter"] for row in due} == {"Ray Optics"}


def test_focus_completed_block_is_saved_to_session_ledger(tmp_path, monkeypatch):
    sessions = tmp_path / "sessions.csv"
    revisions = tmp_path / "revisions.csv"
    monkeypatch.setattr(focus, "SESSION_FILE", sessions)
    monkeypatch.setattr(focus, "REVISION_FILE", revisions)

    timer = focus.FocusMode.__new__(focus.FocusMode)
    timer.subject_var = Value("Chemistry")
    timer.chapter_var = Value("Chemical Bonding")
    timer.total_seconds = 50 * 60
    timer.root = object()

    timer.record_completed_session()

    saved = load_sessions(sessions)
    assert len(saved) == 1
    assert saved[0]["session_type"] == "Focus"
    assert saved[0]["subject"] == "Chemistry"
    assert saved[0]["chapter"] == "Chemical Bonding"
    assert saved[0]["minutes"] == 50
    due = load_due_revisions(revisions, date.max)
    assert len(due) == 5
    assert {row["chapter"] for row in due} == {"Chemical Bonding"}


def test_timer_ledger_is_not_written_without_a_selected_subject(tmp_path, monkeypatch):
    pomodoro_sessions = tmp_path / "pomodoro.csv"
    focus_sessions = tmp_path / "focus.csv"
    monkeypatch.setattr(pomodoro, "SESSION_FILE", pomodoro_sessions)
    monkeypatch.setattr(focus, "SESSION_FILE", focus_sessions)

    pomodoro_timer = pomodoro.PomodoroTimer.__new__(pomodoro.PomodoroTimer)
    pomodoro_timer.subject_var = Value("")
    pomodoro_timer.chapter_var = Value("Ray Optics")
    pomodoro_timer.phase_duration_seconds = 25 * 60
    pomodoro_timer.record_study_block()

    focus_timer = focus.FocusMode.__new__(focus.FocusMode)
    focus_timer.subject_var = Value("")
    focus_timer.chapter_var = Value("Chemical Bonding")
    focus_timer.total_seconds = 50 * 60
    focus_timer.record_completed_session()

    assert not pomodoro_sessions.exists()
    assert not focus_sessions.exists()


class Label:
    def __init__(self):
        self.text = None

    def config(self, **kwargs):
        self.text = kwargs.get("text", self.text)


def test_studyhub_preserves_elapsed_timer_when_less_than_one_minute(tmp_path, monkeypatch):
    monkeypatch.setattr(studyhub, "SESSION_FILE", tmp_path / "sessions.csv")
    monkeypatch.setattr(studyhub, "REVISION_FILE", tmp_path / "revisions.csv")
    timer = studyhub.StudyIntelligence.__new__(studyhub.StudyIntelligence)
    timer.timer_total_seconds = 1500
    timer.remaining_seconds = 1470  # 30 seconds elapsed
    timer.clock = Label()
    timer.selected_details = lambda: ("Physics", "Optics")
    timer.refresh_all = lambda: None

    saved = timer._save_timer_session()

    assert saved == 0
    assert timer.timer_total_seconds == 1500
    assert timer.remaining_seconds == 1470
    assert not (tmp_path / "sessions.csv").exists()


def test_studyhub_saves_full_elapsed_minutes_and_resets_timer(tmp_path, monkeypatch):
    sessions = tmp_path / "sessions.csv"
    revisions = tmp_path / "revisions.csv"
    monkeypatch.setattr(studyhub, "SESSION_FILE", sessions)
    monkeypatch.setattr(studyhub, "REVISION_FILE", revisions)
    timer = studyhub.StudyIntelligence.__new__(studyhub.StudyIntelligence)
    timer.timer_total_seconds = 1500
    timer.remaining_seconds = 1440  # 60 seconds elapsed
    timer.clock = Label()
    timer.selected_details = lambda: ("Physics", "Optics")
    timer.refresh_all = lambda: None

    saved = timer._save_timer_session()

    assert saved == 1
    assert len(load_sessions(sessions)) == 1
    assert load_sessions(sessions)[0]["minutes"] == 1
    assert len(load_due_revisions(revisions, date.max)) == 5
    assert timer.timer_total_seconds == 0
    assert timer.remaining_seconds == 0
