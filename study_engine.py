"""Study intelligence services: session ledger, adaptive plans and spaced revision."""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean

SESSION_FIELDS = ("date", "started_at", "ended_at", "minutes", "subject", "chapter", "session_type", "notes")
REVISION_FIELDS = ("subject", "chapter", "due_date", "interval_days", "status", "last_reviewed")
DEFAULT_INTERVALS = (1, 3, 7, 14, 30)


def _read_rows(path: str | Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def _write_rows(path: str | Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def load_sessions(path: str | Path) -> list[dict]:
    result = []
    for row in _read_rows(path):
        try:
            minutes = int(row.get("minutes", "0"))
            day = date.fromisoformat(row["date"])
        except (ValueError, KeyError, TypeError):
            continue
        if minutes <= 0:
            continue
        result.append({**row, "minutes": minutes, "day": day})
    return sorted(result, key=lambda x: (x["day"], x.get("started_at", "")))


def delete_session(path: str | Path, session: dict) -> bool:
    """Delete exactly one selected ledger entry; leave other sessions untouched.

    The CSV format predates unique session IDs, so the complete stored row is
    used as its identity. If identical entries exist, one matching entry is
    removed per call.
    """
    rows = _read_rows(path)
    target = {field: str(session.get(field, "")) for field in SESSION_FIELDS}
    for index, row in enumerate(rows):
        if all(str(row.get(field, "")) == target[field] for field in SESSION_FIELDS):
            del rows[index]
            _write_rows(path, SESSION_FIELDS, rows)
            return True
    return False


def log_session(path: str | Path, subject: str, chapter: str, minutes: int,
                session_type: str = "Focus", notes: str = "",
                started_at: datetime | None = None, ended_at: datetime | None = None) -> dict:
    subject = subject.strip()
    chapter = chapter.strip()
    if not subject:
        raise ValueError("Choose a subject before saving a study session.")
    if not isinstance(minutes, int) or minutes < 1 or minutes > 1440:
        raise ValueError("Session duration must be a whole number from 1 to 1440 minutes.")
    ended_at = ended_at or datetime.now()
    started_at = started_at or ended_at - timedelta(minutes=minutes)
    row = {
        "date": ended_at.date().isoformat(),
        "started_at": started_at.isoformat(timespec="minutes"),
        "ended_at": ended_at.isoformat(timespec="minutes"),
        "minutes": minutes,
        "subject": subject,
        "chapter": chapter,
        "session_type": session_type.strip() or "Focus",
        "notes": notes.strip(),
    }
    rows = _read_rows(path)
    rows.append(row)
    _write_rows(path, SESSION_FIELDS, rows)
    return row


def session_analytics(sessions: list[dict], today: date | None = None) -> dict:
    today = today or date.today()
    by_subject = defaultdict(int)
    by_day = defaultdict(int)
    for item in sessions:
        day = item.get("day")
        if not isinstance(day, date):
            try:
                day = date.fromisoformat(item["date"])
            except (KeyError, ValueError, TypeError):
                continue
        minutes = int(item.get("minutes", 0))
        if minutes <= 0:
            continue
        by_subject[item.get("subject", "Unassigned")] += minutes
        by_day[day] += minutes
    streak = 0
    cursor = today
    if cursor not in by_day:
        cursor -= timedelta(days=1)
    while cursor in by_day:
        streak += 1
        cursor -= timedelta(days=1)
    last_7 = sum(value for day, value in by_day.items() if today - timedelta(days=6) <= day <= today)
    last_30 = sum(value for day, value in by_day.items() if today - timedelta(days=29) <= day <= today)
    return {
        "total_minutes": sum(by_day.values()),
        "today_minutes": by_day.get(today, 0),
        "last_7_minutes": last_7,
        "last_30_minutes": last_30,
        "streak_days": streak,
        "by_subject": dict(sorted(by_subject.items(), key=lambda pair: (-pair[1], pair[0].casefold()))),
        "by_day": dict(by_day),
        "session_count": len(sessions),
    }


def schedule_revision(path: str | Path, subject: str, chapter: str,
                      reviewed_on: date | None = None,
                      intervals: tuple[int, ...] = DEFAULT_INTERVALS) -> list[dict]:
    subject, chapter = subject.strip(), chapter.strip()
    if not subject or not chapter:
        raise ValueError("A subject and chapter are required to schedule revision.")
    if not intervals or any(not isinstance(x, int) or x < 1 for x in intervals):
        raise ValueError("Revision intervals must be positive whole days.")
    reviewed_on = reviewed_on or date.today()
    rows = [r for r in _read_rows(path)
            if not (r.get("subject", "").casefold() == subject.casefold()
                    and r.get("chapter", "").casefold() == chapter.casefold()
                    and r.get("status", "Due").casefold() == "due")]
    for interval in intervals:
        rows.append({
            "subject": subject, "chapter": chapter,
            "due_date": (reviewed_on + timedelta(days=interval)).isoformat(),
            "interval_days": interval, "status": "Due",
            "last_reviewed": reviewed_on.isoformat(),
        })
    _write_rows(path, REVISION_FIELDS, rows)
    return rows


def load_due_revisions(path: str | Path, today: date | None = None) -> list[dict]:
    today = today or date.today()
    due = []
    for row in _read_rows(path):
        try:
            due_date = date.fromisoformat(row["due_date"])
        except (KeyError, ValueError, TypeError):
            continue
        if row.get("status", "Due").casefold() == "due" and due_date <= today:
            due.append({**row, "due": due_date})
    return sorted(due, key=lambda x: (x["due"], x["subject"].casefold(), x["chapter"].casefold()))


def complete_revision(path: str | Path, subject: str, chapter: str,
                      reviewed_on: date | None = None) -> dict:
    reviewed_on = reviewed_on or date.today()
    rows = _read_rows(path)
    candidates = []
    for row in rows:
        if (row.get("subject", "").casefold() == subject.casefold()
                and row.get("chapter", "").casefold() == chapter.casefold()
                and row.get("status", "Due").casefold() == "due"):
            try:
                if date.fromisoformat(row["due_date"]) <= reviewed_on:
                    candidates.append(row)
            except (KeyError, ValueError):
                continue
    if not candidates:
        raise ValueError("No due revision was found for this chapter.")
    target = min(candidates, key=lambda x: date.fromisoformat(x["due_date"]))
    target["status"] = "Completed"
    target["last_reviewed"] = reviewed_on.isoformat()
    interval = int(target.get("interval_days") or 1)
    next_interval = {1: 3, 3: 7, 7: 14, 14: 30, 30: 60}.get(interval, min(interval * 2, 60))
    for row in rows:
        if (row is not target
                and row.get("subject", "").casefold() == subject.casefold()
                and row.get("chapter", "").casefold() == chapter.casefold()
                and row.get("status", "Due").casefold() == "due"):
            row["status"] = "Superseded"
    rows.append({
        "subject": subject, "chapter": chapter,
        "due_date": (reviewed_on + timedelta(days=next_interval)).isoformat(),
        "interval_days": next_interval, "status": "Due",
        "last_reviewed": reviewed_on.isoformat(),
    })
    _write_rows(path, REVISION_FIELDS, rows)
    return rows[-1]


def build_adaptive_plan(subjects: dict[str, list[dict]], exams: list[dict],
                        available_minutes: int, today: date | None = None,
                        chapter_minutes: int = 45, sessions: list[dict] | None = None) -> list[dict]:
    """Rank pending chapters by exam urgency and lower recent study allocation."""
    if available_minutes < 0 or chapter_minutes < 1:
        raise ValueError("Available time must be non-negative and chapter time must be positive.")
    today = today or date.today()
    sessions = sessions or []
    recent = defaultdict(int)
    for item in sessions:
        try:
            day = item.get("day") or date.fromisoformat(item["date"])
            if today - timedelta(days=6) <= day <= today:
                recent[item.get("subject", "").casefold()] += int(item.get("minutes", 0))
        except (ValueError, KeyError, TypeError):
            continue
    urgency = {}
    for exam in exams:
        subject = (exam.get("subject") or "").casefold()
        exam_date = exam.get("date")
        if isinstance(exam_date, str):
            try:
                exam_date = date.fromisoformat(exam_date)
            except ValueError:
                continue
        if not subject or not isinstance(exam_date, date) or exam_date < today:
            continue
        days = (exam_date - today).days
        priority = {"high": 1.25, "medium": 1.0, "low": 0.8}.get(str(exam.get("priority", "Medium")).casefold(), 1.0)
        score = priority * (1 + 14 / (days + 2))
        urgency[subject] = max(urgency.get(subject, 0), score)
    candidates = []
    for subject, chapters in subjects.items():
        pending = [x for x in chapters if str(x.get("status", "Pending")).casefold() != "completed"
                   and str(x.get("chapter", "")).strip()
                   and str(x.get("chapter", "")).casefold() != "full subject syllabus"]
        for chapter in pending:
            key = subject.casefold()
            score = urgency.get(key, 1.0) / (1 + recent[key] / 300)
            candidates.append((score, subject, chapter["chapter"]))
    candidates.sort(key=lambda x: (-x[0], x[1].casefold(), x[2].casefold()))
    plan, remaining = [], available_minutes
    for score, subject, chapter in candidates:
        if remaining <= 0:
            break
        duration = min(chapter_minutes, remaining)
        plan.append({
            "subject": subject, "chapter": chapter, "minutes": duration,
            "reason": "Exam priority" if subject.casefold() in urgency else "Pending syllabus",
            "priority_score": round(score, 3),
        })
        remaining -= duration
    return plan


def build_recovery_plan(timetable: list[dict], today: date | None = None,
                        now_time: str | None = None) -> list[dict]:
    """Identify today's uncompleted timetable blocks that have fully elapsed."""
    today = today or date.today()
    now_time = now_time or datetime.now().strftime("%H:%M")
    try:
        current_time = datetime.strptime(now_time, "%H:%M")
    except (TypeError, ValueError) as exc:
        raise ValueError("Current time must use HH:MM format.") from exc

    weekday = today.strftime("%A")
    missed = []
    for item in timetable:
        if item.get("day") != weekday or str(item.get("status", "Planned")).casefold() == "completed":
            continue
        start, end = item.get("start", ""), item.get("end", "")
        try:
            start_time = datetime.strptime(start, "%H:%M")
            end_time = datetime.strptime(end, "%H:%M")
        except (TypeError, ValueError):
            # Ignore malformed or incomplete timetable rows instead of crashing the planner.
            continue
        # A block is only "missed" after it has ended, not while it is still in progress.
        # Overnight blocks are not inferred from the timetable's day-only format.
        if end_time <= start_time or end_time > current_time:
            continue
        subject = item.get("subject", "")
        missed.append({
            "subject": subject,
            "task": item.get("task_type", "Study"),
            "start": start, "end": end,
            "notes": item.get("notes", ""),
            "recovery": f"Reschedule {subject or 'study'} ({start}–{end})",
        })
    return sorted(missed, key=lambda x: x["start"])
