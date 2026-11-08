"""Persistent, once-per-exam reminder scheduling for ExamReadyTimer.

Reminders are evaluated while the Exam Planner window is open. The helper is
kept independent of Tkinter so date logic and persistence can be tested.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path


def reminder_key(exam: dict) -> str:
    """Stable key that naturally resets when an exam date or name changes."""
    return f"{exam['name'].strip().casefold()}|{exam['date'].isoformat()}"


def due_reminders(exams: list[dict], today: date, sent: set[str]) -> list[dict]:
    """Return exams whose reminder window has started and has not been shown."""
    due = []
    for exam in exams:
        try:
            lead = int(exam.get("reminder_days", 7))
            if not 0 <= lead <= 365:
                continue
            start = exam["date"] - timedelta(days=lead)
            key = reminder_key(exam)
            if start <= today <= exam["date"] and key not in sent:
                due.append(exam)
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
    return sorted(due, key=lambda item: item["date"])


def load_sent_reminders(path: str | Path) -> set[str]:
    """Load reminder keys; tolerate missing or damaged state files safely."""
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(payload, list) and all(isinstance(item, str) for item in payload):
            return set(payload)
    except (OSError, ValueError, TypeError):
        pass
    return set()


def save_sent_reminders(path: str | Path, sent: set[str]) -> None:
    """Atomically save reminder keys so a restart does not repeat alerts."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(sorted(sent), ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    temporary.replace(target)
