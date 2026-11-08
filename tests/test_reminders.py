from datetime import date
import json

from reminders import due_reminders, load_sent_reminders, reminder_key, save_sent_reminders


def exam(name="Physics", exam_date=date(2027, 3, 10), lead=7):
    return {"name": name, "date": exam_date, "reminder_days": lead}


def test_reminder_is_due_on_first_day_of_window_and_once_only():
    item = exam()
    today = date(2027, 3, 3)
    assert due_reminders([item], today, set()) == [item]
    assert due_reminders([item], today, {reminder_key(item)}) == []


def test_reminder_window_includes_exam_day_but_not_after():
    item = exam(lead=0)
    assert due_reminders([item], date(2027, 3, 10), set()) == [item]
    assert due_reminders([item], date(2027, 3, 11), set()) == []


def test_reminder_state_round_trip_and_corrupt_file(tmp_path):
    path = tmp_path / "reminders.json"
    keys = {reminder_key(exam()), reminder_key(exam("Maths"))}
    save_sent_reminders(path, keys)
    assert load_sent_reminders(path) == keys
    path.write_text("{broken", encoding="utf-8")
    assert load_sent_reminders(path) == set()


def test_invalid_lead_is_ignored():
    assert due_reminders([exam(lead=999)], date(2027, 3, 3), set()) == []
