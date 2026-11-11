import json

from session_state import clear_session, load_session, save_session


def sample_state():
    return {
        "study_minutes": 25,
        "break_minutes": 5,
        "total_sessions": 4,
        "session": 2,
        "phase": "Break",
        "remaining": 173,
        "phase_duration_seconds": 300,
        "completed": False,
        "subject": "Physics",
        "chapter": "Ray Optics",
        "running": True,
    }


def test_session_round_trip_always_restores_paused(tmp_path):
    path = tmp_path / "pomodoro_state.json"
    save_session(path, sample_state())
    restored = load_session(path)
    assert restored == {**sample_state(), "running": False}


def test_corrupt_or_invalid_session_is_ignored(tmp_path):
    path = tmp_path / "pomodoro_state.json"
    path.write_text("{not valid json", encoding="utf-8")
    assert load_session(path) is None
    path.write_text(json.dumps({**sample_state(), "remaining": 9999}), encoding="utf-8")
    assert load_session(path) is None


def test_clear_session_removes_snapshot(tmp_path):
    path = tmp_path / "pomodoro_state.json"
    save_session(path, sample_state())
    clear_session(path)
    assert load_session(path) is None
