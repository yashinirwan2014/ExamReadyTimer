from datetime import date, datetime
import csv

import pytest

from study_engine import (
    build_adaptive_plan, build_recovery_plan, complete_revision,
    load_due_revisions, load_sessions, log_session, schedule_revision,
    session_analytics,
)


def test_log_session_persists_and_loads_session(tmp_path):
    path = tmp_path / "sessions.csv"
    row = log_session(path, "Physics", "Optics", 45, "Pomodoro",
                      started_at=datetime(2026, 11, 8, 10, 0),
                      ended_at=datetime(2026, 11, 8, 10, 45))
    sessions = load_sessions(path)
    assert row["minutes"] == 45
    assert len(sessions) == 1
    assert sessions[0]["subject"] == "Physics"
    assert sessions[0]["day"] == date(2026, 11, 8)


@pytest.mark.parametrize("minutes", [0, -1, 1441, 2.5])
def test_log_session_rejects_invalid_duration(tmp_path, minutes):
    with pytest.raises(ValueError):
        log_session(tmp_path / "sessions.csv", "Maths", "Algebra", minutes)


def test_analytics_reports_subject_totals_weekly_hours_and_streak():
    today = date(2026, 11, 8)
    sessions = [
        {"date": "2026-11-06", "minutes": 30, "subject": "Physics"},
        {"date": "2026-11-07", "minutes": 60, "subject": "Maths"},
        {"date": "2026-11-08", "minutes": 45, "subject": "Physics"},
    ]
    stats = session_analytics(sessions, today)
    assert stats["today_minutes"] == 45
    assert stats["last_7_minutes"] == 135
    assert stats["streak_days"] == 3
    assert stats["by_subject"] == {"Physics": 75, "Maths": 60}


def test_spaced_revision_creates_intervals_and_advances_after_completion(tmp_path):
    path = tmp_path / "revision.csv"
    schedule_revision(path, "Physics", "Optics", date(2026, 11, 8))
    due = load_due_revisions(path, date(2026, 11, 9))
    assert len(due) == 1
    assert due[0]["due"] == date(2026, 11, 9)
    complete_revision(path, "Physics", "Optics", date(2026, 11, 9))
    next_due = load_due_revisions(path, date(2026, 11, 12))
    assert len(next_due) == 1
    assert next_due[0]["due"] == date(2026, 11, 12)


def test_adaptive_plan_prioritizes_nearer_high_priority_exam(tmp_path):
    subjects = {
        "Physics": [{"chapter": "Optics", "status": "Pending"}],
        "History": [{"chapter": "Modern India", "status": "Pending"}],
    }
    exams = [
        {"subject": "Physics", "date": date(2026, 11, 10), "priority": "High"},
        {"subject": "History", "date": date(2026, 12, 10), "priority": "Low"},
    ]
    plan = build_adaptive_plan(subjects, exams, 60, today=date(2026, 11, 8),
                               chapter_minutes=45)
    assert plan[0]["subject"] == "Physics"
    assert sum(item["minutes"] for item in plan) == 60


def test_adaptive_plan_ignores_placeholder_and_completed_chapters():
    subjects = {"Physics": [
        {"chapter": "Full subject syllabus", "status": "Pending"},
        {"chapter": "Optics", "status": "Completed"},
        {"chapter": "Waves", "status": "Pending"},
    ]}
    plan = build_adaptive_plan(subjects, [], 90, today=date(2026, 11, 8))
    assert [item["chapter"] for item in plan] == ["Waves"]


def test_recovery_plan_only_returns_uncompleted_past_blocks_for_today():
    today = date(2026, 11, 8)  # Sunday
    timetable = [
        {"day": "Sunday", "start": "08:00", "end": "09:00", "subject": "Physics", "status": "Planned"},
        {"day": "Sunday", "start": "10:00", "end": "11:00", "subject": "Maths", "status": "Completed"},
        {"day": "Monday", "start": "08:00", "end": "09:00", "subject": "English", "status": "Planned"},
        {"day": "Sunday", "start": "20:00", "end": "21:00", "subject": "Chemistry", "status": "Planned"},
    ]
    result = build_recovery_plan(timetable, today, "12:00")
    assert [item["subject"] for item in result] == ["Physics"]
