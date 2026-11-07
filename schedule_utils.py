"""Small, testable helpers for study schedule time calculations."""
from datetime import datetime


def duration_minutes(start: str, end: str) -> int:
    """Return duration for same-day HH:MM times; reject invalid or reversed ranges."""
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    minutes = int((end_time - start_time).total_seconds() // 60)
    if minutes <= 0:
        raise ValueError("End time must be later than start time.")
    return minutes


def times_overlap(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    """Return True when two same-day study blocks overlap."""
    duration_minutes(start_a, end_a)
    duration_minutes(start_b, end_b)
    a_start = datetime.strptime(start_a, "%H:%M")
    a_end = datetime.strptime(end_a, "%H:%M")
    b_start = datetime.strptime(start_b, "%H:%M")
    b_end = datetime.strptime(end_b, "%H:%M")
    return a_start < b_end and b_start < a_end
