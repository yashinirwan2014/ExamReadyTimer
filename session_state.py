"""Atomic persistence for resumable ExamReadyTimer sessions."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def save_session(path: str | Path, state: dict[str, Any]) -> None:
    """Write a complete session snapshot without exposing a partial JSON file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    payload = dict(state)
    payload["running"] = False  # Restored sessions always resume paused.
    try:
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)


def load_session(path: str | Path) -> dict[str, Any] | None:
    """Load a valid session snapshot; reject malformed or incomplete state."""
    target = Path(path)
    if not target.is_file():
        return None
    try:
        with target.open("r", encoding="utf-8") as stream:
            state = json.load(stream)
        required = {
            "study_minutes": int, "break_minutes": int, "total_sessions": int,
            "session": int, "phase": str, "remaining": int,
            "phase_duration_seconds": int, "completed": bool,
            "subject": str, "chapter": str,
        }
        if not isinstance(state, dict):
            return None
        for key, expected in required.items():
            value = state.get(key)
            if expected is int and isinstance(value, bool):
                return None
            if not isinstance(value, expected):
                return None
        if (state["study_minutes"] < 1 or state["break_minutes"] < 1
                or state["total_sessions"] < 1 or state["session"] < 1
                or state["phase"] not in ("Study", "Break")
                or state["remaining"] < 0 or state["phase_duration_seconds"] < 0
                or state["remaining"] > state["phase_duration_seconds"]):
            return None
        state["running"] = False
        return state
    except (OSError, ValueError, TypeError):
        return None


def clear_session(path: str | Path) -> None:
    """Remove the saved snapshot after completion or an intentional reset."""
    Path(path).unlink(missing_ok=True)
