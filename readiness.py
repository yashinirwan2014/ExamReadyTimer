"""Exam readiness gap analysis linking exam dates to pending syllabus work."""
from __future__ import annotations

import csv
import math
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from storage import initialize_user_data
from theme import apply_dark_theme
from navigation import add_home_button

APP_DIR = Path(__import__("sys").executable).resolve().parent if getattr(__import__("sys"), "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
EXAMS_FILE = DATA_DIR / "dataexams.csv"
SYLLABUS_FILE = DATA_DIR / "dataorsubjects.csv"
BG, NAVY, MUTED = "#0B1020", "#172544", "#FFFFFF"
DEFAULT_CHAPTER_HOURS = 1.5
DEFAULT_DAILY_HOURS = 3.0


def load_exam_data(path: str | Path = EXAMS_FILE) -> list[dict]:
    """Load valid exam rows using the same CSV schema as the Exam Planner."""
    exams = []
    path = Path(path)
    if not path.exists():
        return exams
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            try:
                name = (row.get("Exam") or "").strip()
                subject = (row.get("Subject") or "").strip()
                exam_date = date(int(row["Year"]), int(row["Month"]), int(row["Day"]))
            except (KeyError, TypeError, ValueError):
                continue
            if name:
                exams.append({
                    "name": name,
                    "subject": subject,
                    "date": exam_date,
                    "priority": (row.get("Priority") or "Medium").strip().title(),
                })
    return exams


def load_syllabus_data(path: str | Path = SYLLABUS_FILE) -> dict[str, dict]:
    """Return chapter counts by subject, ignoring the empty starter placeholder."""
    subjects: dict[str, dict] = {}
    path = Path(path)
    if not path.exists():
        return subjects
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            subject = (row.get("Subject") or "").strip()
            chapter = (row.get("Chapter") or "").strip()
            if not subject or not chapter or chapter.casefold() == "full subject syllabus":
                continue
            item = subjects.setdefault(subject, {"total": 0, "completed": 0, "pending": 0})
            item["total"] += 1
            if (row.get("Status") or "").strip().casefold() == "completed":
                item["completed"] += 1
            else:
                item["pending"] += 1
    return subjects


def analyze_readiness(
    exams: list[dict],
    subjects: dict[str, dict],
    daily_hours: float = DEFAULT_DAILY_HOURS,
    chapter_hours: float = DEFAULT_CHAPTER_HOURS,
    today: date | None = None,
) -> list[dict]:
    """Estimate whether pending chapters fit before each future exam.

    Estimates are planning aids, not predictions of marks or mastery. Subject
    matching is exact (case-insensitive) to avoid silently assigning the wrong
    syllabus to an exam.
    """
    if (not math.isfinite(daily_hours) or not math.isfinite(chapter_hours)
            or daily_hours <= 0 or chapter_hours <= 0):
        raise ValueError("Study hours and chapter hours must be finite numbers greater than zero.")
    today = today or date.today()
    normalized = {name.casefold(): value for name, value in subjects.items()}
    results = []
    for exam in exams:
        exam_date = exam["date"]
        days_left = (exam_date - today).days
        if days_left < 0:
            continue
        subject_name = (exam.get("subject") or "").strip()
        syllabus = normalized.get(subject_name.casefold()) if subject_name else None
        pending = int(syllabus["pending"]) if syllabus else None
        total = int(syllabus["total"]) if syllabus else None
        completed = int(syllabus["completed"]) if syllabus else None
        required_hours = round(pending * chapter_hours, 1) if pending is not None else None
        available_hours = round(days_left * daily_hours, 1)
        daily_required = round(required_hours / max(days_left, 1), 1) if required_hours is not None else None
        gap = round(max(0.0, required_hours - available_hours), 1) if required_hours is not None else None
        if syllabus is None:
            status = "Link a subject"
        elif pending == 0:
            status = "Syllabus complete"
        elif gap > 0:
            status = "At risk"
        elif required_hours > available_hours * 0.85:
            status = "Tight"
        else:
            status = "On track"
        results.append({
            "name": exam["name"], "subject": subject_name, "date": exam_date,
            "priority": exam.get("priority", "Medium"), "days_left": days_left,
            "pending": pending, "completed": completed, "total": total,
            "required_hours": required_hours, "available_hours": available_hours,
            "daily_required": daily_required, "gap_hours": gap, "status": status,
        })
    return sorted(results, key=lambda item: (item["date"], {"High": 0, "Medium": 1, "Low": 2}.get(item["priority"], 1)))


class ReadinessDashboard:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Exam Readiness")
        root.geometry("1020x650")
        root.minsize(780, 500)
        apply_dark_theme(root)
        add_home_button(self.root)
        self.daily_hours = tk.StringVar(value=str(DEFAULT_DAILY_HOURS))
        self.chapter_hours = tk.StringVar(value=str(DEFAULT_CHAPTER_HOURS))
        self.build()
        self.refresh()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="Exam Readiness Gap Engine", bg=NAVY, fg="#E8EEFF",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="See whether your remaining syllabus fits the time left before each exam.",
                 bg=NAVY, fg="#FFFFFF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=20, pady=16)
        body.pack(fill="both", expand=True)
        controls = tk.LabelFrame(body, text="Planning assumptions", bg=BG, fg="#E8EEFF", padx=12, pady=10)
        controls.pack(fill="x", pady=(0, 12))
        tk.Label(controls, text="Available study hours per day", bg=BG).grid(row=0, column=0, sticky="w")
        tk.Entry(controls, textvariable=self.daily_hours, width=9).grid(row=1, column=0, sticky="w", padx=(0, 18))
        tk.Label(controls, text="Estimated hours per pending chapter", bg=BG).grid(row=0, column=1, sticky="w")
        tk.Entry(controls, textvariable=self.chapter_hours, width=9).grid(row=1, column=1, sticky="w", padx=(0, 18))
        ttk.Button(controls, text="Recalculate", command=self.refresh).grid(row=1, column=2, sticky="w")
        self.summary = tk.Label(body, text="", bg=BG, fg="#E8EEFF", font=("Arial", 12, "bold"))
        self.summary.pack(anchor="w", pady=(0, 10))
        columns = ("exam", "subject", "date", "days", "syllabus", "needed", "capacity", "pace", "gap", "status")
        self.table = ttk.Treeview(body, columns=columns, show="headings")
        headings = (("exam", "EXAM"), ("subject", "SUBJECT"), ("date", "DATE"),
                    ("days", "DAYS LEFT"), ("syllabus", "PENDING / TOTAL"),
                    ("needed", "HOURS NEEDED"), ("capacity", "HOURS AVAILABLE"),
                    ("pace", "HOURS / DAY"), ("gap", "SHORTFALL"), ("status", "READINESS"))
        for key, label in headings:
            self.table.heading(key, text=label)
        widths = {"exam": 130, "subject": 115, "date": 95, "days": 75, "syllabus": 105,
                  "needed": 105, "capacity": 115, "pace": 100, "gap": 90, "status": 125}
        for key, width in widths.items():
            self.table.column(key, width=width, minwidth=65, anchor="center")
        self.table.pack(fill="both", expand=True)
        self.detail = tk.Label(body, text="", bg=BG, fg=MUTED, justify="left",
                               wraplength=930, font=("Arial", 10))
        self.detail.pack(anchor="w", pady=(10, 0))
        tk.Label(self.root,
                 text="Estimates use your chosen hours per chapter. They do not measure chapter difficulty or guarantee exam readiness.",
                 bg=BG, fg=MUTED, font=("Arial", 9), wraplength=950).pack(anchor="w", padx=22, pady=(0, 10))

    def refresh(self):
        try:
            daily = float(self.daily_hours.get())
            chapter = float(self.chapter_hours.get())
            results = analyze_readiness(load_exam_data(), load_syllabus_data(), daily, chapter)
        except (ValueError, OSError) as exc:
            messagebox.showwarning("Check planning values", str(exc), parent=self.root)
            return
        self.table.delete(*self.table.get_children())
        at_risk = 0
        linked = 0
        for item in results:
            if item["status"] == "At risk":
                at_risk += 1
            if item["pending"] is not None:
                linked += 1
            syllabus = f'{item["pending"]}/{item["total"]}' if item["pending"] is not None else "Not linked"
            needed = f'{item["required_hours"]:.1f}h' if item["required_hours"] is not None else "—"
            capacity = f'{item["available_hours"]:.1f}h'
            pace = f'{item["daily_required"]:.1f}h' if item["daily_required"] is not None else "—"
            gap = f'{item["gap_hours"]:.1f}h' if item["gap_hours"] is not None else "—"
            self.table.insert("", "end", values=(
                item["name"], item["subject"] or "—", item["date"].isoformat(),
                item["days_left"], syllabus, needed, capacity, pace, gap, item["status"]))
        self.summary.config(text=f"{len(results)} upcoming exams  •  {linked} linked to syllabus  •  {at_risk} currently at risk")
        if not results:
            self.detail.config(text="No upcoming exams found. Add exam dates in Exam Planner to generate a readiness forecast.")
        elif linked < len(results):
            self.detail.config(text="For exams showing 'Not linked', enter the exact subject name in Exam Planner and make sure that subject has chapters in Subject Tracker.")
        elif at_risk:
            self.detail.config(text="At-risk exams need more estimated study time than your daily capacity allows. Increase available study hours only if realistic, reduce the chapter-time estimate if appropriate, or prioritize the highest-risk syllabus.")
        else:
            self.detail.config(text="Your linked syllabus currently fits the capacity you entered. Keep chapter statuses updated to keep this estimate useful.")


def main():
    root = tk.Tk()
    ReadinessDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
