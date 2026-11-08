"""Study Intelligence Suite: time ledger, adaptive planning and spaced revision."""
from __future__ import annotations

import csv
import sys
import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk

from storage import initialize_user_data
from study_engine import (
    build_adaptive_plan, build_recovery_plan, complete_revision,
    load_due_revisions, load_sessions, log_session, schedule_revision,
    session_analytics,
)

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
SESSION_FILE = DATA_DIR / "study_sessions.csv"
REVISION_FILE = DATA_DIR / "revision_schedule.csv"
SUBJECT_FILE = DATA_DIR / "dataorsubjects.csv"
EXAM_FILE = DATA_DIR / "dataexams.csv"
TIMETABLE_FILE = DATA_DIR / "datatimetable.csv"
BG, NAVY, MUTED = "#F3F5FB", "#25316D", "#68708A"


def read_subjects() -> dict[str, list[dict]]:
    subjects: dict[str, list[dict]] = {}
    if not SUBJECT_FILE.exists():
        return subjects
    with SUBJECT_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            subject = (row.get("Subject") or "").strip()
            chapter = (row.get("Chapter") or "").strip()
            if not subject or not chapter or chapter.casefold() == "full subject syllabus":
                continue
            subjects.setdefault(subject, []).append({
                "chapter": chapter, "status": (row.get("Status") or "Pending").strip()
            })
    return subjects


def read_exams() -> list[dict]:
    exams = []
    if not EXAM_FILE.exists():
        return exams
    with EXAM_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            try:
                exam_date = date(int(row["Year"]), int(row["Month"]), int(row["Day"]))
            except (ValueError, KeyError, TypeError):
                continue
            exams.append({"subject": (row.get("Subject") or "").strip(),
                          "date": exam_date, "priority": row.get("Priority", "Medium")})
    return exams


def read_timetable() -> list[dict]:
    items = []
    if not TIMETABLE_FILE.exists():
        return items
    with TIMETABLE_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            items.append({
                "day": row.get("Day", ""), "start": row.get("StartTime", "00:00"),
                "end": row.get("EndTime", ""), "subject": row.get("Subject", ""),
                "task_type": row.get("TaskType", "Study"), "status": row.get("Status", "Planned"),
                "notes": row.get("Notes", ""),
            })
    return items


class StudyIntelligence:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ExamReadyTimer | Study Intelligence Suite")
        root.geometry("980x760")
        root.minsize(760, 620)
        root.configure(bg=BG)
        self.subjects = read_subjects()
        self.timer_after = None
        self.remaining_seconds = 0
        self.timer_total_seconds = 0
        self.timer_running = False
        self.build()
        self.refresh_all()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=22, pady=17)
        header.pack(fill="x")
        tk.Label(header, text="Study Intelligence Suite", bg=NAVY, fg="white",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Track real effort • Plan the next step • Revise at the right time",
                 bg=NAVY, fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=14)
        self.session_tab = tk.Frame(self.tabs, bg=BG, padx=18, pady=16)
        self.plan_tab = tk.Frame(self.tabs, bg=BG, padx=18, pady=16)
        self.revision_tab = tk.Frame(self.tabs, bg=BG, padx=18, pady=16)
        self.stats_tab = tk.Frame(self.tabs, bg=BG, padx=18, pady=16)
        self.tabs.add(self.session_tab, text="Study Session")
        self.tabs.add(self.plan_tab, text="Adaptive Plan")
        self.tabs.add(self.revision_tab, text="Revision")
        self.tabs.add(self.stats_tab, text="Analytics")
        self.build_session()
        self.build_plan()
        self.build_revision()
        self.build_stats()
        tk.Label(self.root, text="Your session history and revision schedule stay on this device and are included in ZIP backups.",
                 bg=BG, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=20, pady=(0, 9))

    def build_session(self):
        tab = self.session_tab
        tk.Label(tab, text="Log a focused study session", bg=BG, fg=NAVY,
                 font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 12))
        form = tk.Frame(tab, bg=BG)
        form.pack(fill="x")
        self.subject_var = tk.StringVar()
        self.chapter_var = tk.StringVar()
        self.minutes_var = tk.StringVar(value="25")
        self.kind_var = tk.StringVar(value="Focus")
        tk.Label(form, text="Subject", bg=BG, fg=MUTED).grid(row=0, column=0, sticky="w")
        self.subject_combo = ttk.Combobox(form, textvariable=self.subject_var,
                                         values=sorted(self.subjects), state="readonly", width=32)
        self.subject_combo.grid(row=1, column=0, padx=(0, 10), pady=(4, 10), sticky="ew")
        self.subject_combo.bind("<<ComboboxSelected>>", self.update_chapters)
        tk.Label(form, text="Chapter / topic", bg=BG, fg=MUTED).grid(row=0, column=1, sticky="w")
        self.chapter_combo = ttk.Combobox(form, textvariable=self.chapter_var, state="normal", width=32)
        self.chapter_combo.grid(row=1, column=1, padx=(0, 10), pady=(4, 10), sticky="ew")
        tk.Label(form, text="Minutes", bg=BG, fg=MUTED).grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.minutes_var, width=12).grid(row=3, column=0, sticky="w", pady=(4, 10))
        tk.Label(form, text="Session type", bg=BG, fg=MUTED).grid(row=2, column=1, sticky="w")
        ttk.Combobox(form, textvariable=self.kind_var, values=["Focus", "Pomodoro", "Revision", "Practice", "Reading", "Mock test"],
                     state="readonly", width=20).grid(row=3, column=1, sticky="w", pady=(4, 10))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        controls = tk.Frame(tab, bg=BG)
        controls.pack(anchor="w", pady=(5, 12))
        ttk.Button(controls, text="Save completed session", command=self.save_manual_session).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Start focus timer", command=self.start_timer).pack(side="left", padx=8)
        ttk.Button(controls, text="Pause", command=self.pause_timer).pack(side="left", padx=8)
        ttk.Button(controls, text="Save elapsed time", command=self.save_elapsed).pack(side="left", padx=8)
        self.clock = tk.Label(tab, text="25:00", bg=BG, fg=NAVY, font=("Arial", 42, "bold"))
        self.clock.pack(anchor="w", pady=(8, 2))
        self.timer_status = tk.Label(tab, text="Choose a subject and topic. Timer sessions are logged when completed or saved.",
                                     bg=BG, fg=MUTED, wraplength=820, justify="left")
        self.timer_status.pack(anchor="w", pady=(0, 12))
        tk.Label(tab, text="RECENT STUDY SESSIONS", bg=BG, fg=NAVY,
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 5))
        self.recent_table = ttk.Treeview(tab, columns=("date", "subject", "chapter", "minutes", "type"),
                                         show="headings", height=8)
        for key, label, width in [("date", "DATE", 100), ("subject", "SUBJECT", 180),
                                  ("chapter", "CHAPTER / TOPIC", 300), ("minutes", "MINUTES", 85),
                                  ("type", "TYPE", 110)]:
            self.recent_table.heading(key, text=label)
            self.recent_table.column(key, width=width, anchor="center" if key in ("date", "minutes", "type") else "w")
        self.recent_table.pack(fill="both", expand=True)

    def build_plan(self):
        tab = self.plan_tab
        tk.Label(tab, text="Build a realistic plan for today", bg=BG, fg=NAVY,
                 font=("Arial", 16, "bold")).pack(anchor="w")
        controls = tk.Frame(tab, bg=BG)
        controls.pack(fill="x", pady=12)
        self.available_var = tk.StringVar(value="180")
        self.chapter_minutes_var = tk.StringVar(value="45")
        tk.Label(controls, text="Available minutes", bg=BG, fg=MUTED).grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.available_var, width=12).grid(row=1, column=0, padx=(0, 14), sticky="w")
        tk.Label(controls, text="Minutes per chapter block", bg=BG, fg=MUTED).grid(row=0, column=1, sticky="w")
        ttk.Entry(controls, textvariable=self.chapter_minutes_var, width=12).grid(row=1, column=1, padx=(0, 14), sticky="w")
        ttk.Button(controls, text="Generate adaptive plan", command=self.generate_plan).grid(row=1, column=2, sticky="w")
        ttk.Button(controls, text="Find missed blocks", command=self.show_recovery).grid(row=1, column=3, padx=8, sticky="w")
        self.plan_summary = tk.Label(tab, text="The plan prioritises subjects with nearer exams and gives less recently studied subjects a gentle boost.",
                                     bg=BG, fg=MUTED, wraplength=850, justify="left")
        self.plan_summary.pack(anchor="w", pady=(0, 10))
        self.plan_table = ttk.Treeview(tab, columns=("subject", "chapter", "minutes", "reason"), show="headings")
        for key, label, width in [("subject", "SUBJECT", 190), ("chapter", "CHAPTER / TASK", 390),
                                  ("minutes", "MINUTES", 90), ("reason", "WHY THIS", 160)]:
            self.plan_table.heading(key, text=label)
            self.plan_table.column(key, width=width, anchor="center" if key == "minutes" else "w")
        self.plan_table.pack(fill="both", expand=True)
        tk.Label(tab, text="This is a suggested allocation, not a fixed timetable. Adjust it around breaks, school and your actual energy.",
                 bg=BG, fg=MUTED, wraplength=850, justify="left").pack(anchor="w", pady=(10, 0))

    def build_revision(self):
        tab = self.revision_tab
        tk.Label(tab, text="Spaced revision queue", bg=BG, fg=NAVY,
                 font=("Arial", 16, "bold")).pack(anchor="w")
        tk.Label(tab, text="After a logged session, add a 1, 3, 7, 14 and 30-day review cycle for that topic.",
                 bg=BG, fg=MUTED).pack(anchor="w", pady=(5, 10))
        controls = tk.Frame(tab, bg=BG)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Button(controls, text="Schedule selected session topic", command=self.schedule_selected_topic).pack(side="left")
        ttk.Button(controls, text="Mark selected review complete", command=self.complete_selected_revision).pack(side="left", padx=10)
        self.revision_table = ttk.Treeview(tab, columns=("due", "subject", "chapter", "interval"),
                                           show="headings")
        for key, label, width in [("due", "DUE DATE", 120), ("subject", "SUBJECT", 190),
                                  ("chapter", "CHAPTER / TOPIC", 390), ("interval", "INTERVAL", 100)]:
            self.revision_table.heading(key, text=label)
            self.revision_table.column(key, width=width, anchor="center" if key in ("due", "interval") else "w")
        self.revision_table.pack(fill="both", expand=True)
        self.revision_note = tk.Label(tab, text="", bg=BG, fg=MUTED)
        self.revision_note.pack(anchor="w", pady=(10, 0))

    def build_stats(self):
        tab = self.stats_tab
        tk.Label(tab, text="Your real study-time analytics", bg=BG, fg=NAVY,
                 font=("Arial", 16, "bold")).pack(anchor="w")
        self.stats_summary = tk.Label(tab, text="", bg=BG, fg=NAVY, font=("Arial", 13, "bold"),
                                      justify="left")
        self.stats_summary.pack(anchor="w", pady=14)
        tk.Label(tab, text="SUBJECT BREAKDOWN", bg=BG, fg=NAVY,
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(8, 5))
        self.stats_table = ttk.Treeview(tab, columns=("subject", "hours", "minutes"), show="headings", height=12)
        for key, label, width in [("subject", "SUBJECT", 330), ("hours", "HOURS", 120), ("minutes", "MINUTES", 120)]:
            self.stats_table.heading(key, text=label)
            self.stats_table.column(key, width=width, anchor="w" if key == "subject" else "center")
        self.stats_table.pack(fill="both", expand=True)
        ttk.Button(tab, text="Refresh analytics", command=self.refresh_stats).pack(anchor="e", pady=12)

    def update_chapters(self, _event=None):
        chapters = [x["chapter"] for x in self.subjects.get(self.subject_var.get(), [])]
        self.chapter_combo["values"] = chapters
        if chapters and self.chapter_var.get() not in chapters:
            self.chapter_var.set(chapters[0])

    def selected_details(self):
        subject = self.subject_var.get().strip()
        chapter = self.chapter_var.get().strip()
        if not subject:
            raise ValueError("Choose a subject first.")
        return subject, chapter

    def save_manual_session(self):
        try:
            subject, chapter = self.selected_details()
            minutes = int(self.minutes_var.get())
            log_session(SESSION_FILE, subject, chapter, minutes, self.kind_var.get())
            if chapter:
                schedule_revision(REVISION_FILE, subject, chapter)
        except (ValueError, OSError) as exc:
            messagebox.showwarning("Could not save session", str(exc), parent=self.root)
            return
        self.timer_status.config(text=f"Saved {minutes} minutes for {subject}.")
        self.refresh_all()

    def start_timer(self):
        if self.timer_running:
            return
        try:
            self.selected_details()
            if self.remaining_seconds <= 0:
                minutes = int(self.minutes_var.get())
                if not 1 <= minutes <= 240:
                    raise ValueError("Timer duration must be from 1 to 240 minutes.")
                self.remaining_seconds = minutes * 60
                self.timer_total_seconds = self.remaining_seconds
        except (ValueError, tk.TclError) as exc:
            messagebox.showwarning("Check session details", str(exc), parent=self.root)
            return
        self.timer_running = True
        self.timer_status.config(text="Focus session running. Your time is recorded only when completed or saved.")
        self.tick()

    def tick(self):
        self.clock.config(text=f"{self.remaining_seconds // 60:02d}:{self.remaining_seconds % 60:02d}")
        if self.remaining_seconds <= 0:
            self.timer_running = False
            self.root.bell()
            try:
                self._save_timer_session()
            except (ValueError, OSError, tk.TclError) as exc:
                self.timer_status.config(text=f"Session finished, but the log could not be saved: {exc}. Use Save elapsed time to retry.")
                return
            self.timer_status.config(text="Focus session completed and added to your study ledger.")
            messagebox.showinfo("Session complete", "Your completed focus session has been saved.", parent=self.root)
            return
        self.remaining_seconds -= 1
        self.timer_after = self.root.after(1000, self.tick)

    def pause_timer(self):
        self.timer_running = False
        if self.timer_after:
            self.root.after_cancel(self.timer_after)
            self.timer_after = None
        self.timer_status.config(text="Timer paused. Use Save elapsed time to keep the completed minutes.")

    def _save_timer_session(self):
        elapsed = self.timer_total_seconds - self.remaining_seconds
        minutes = elapsed // 60
        if minutes > 0:
            subject, chapter = self.selected_details()
            log_session(SESSION_FILE, subject, chapter, minutes, "Focus")
            if chapter:
                schedule_revision(REVISION_FILE, subject, chapter)
        display_minutes = max(1, self.timer_total_seconds // 60)
        self.remaining_seconds = 0
        self.timer_total_seconds = 0
        self.clock.config(text=f"{display_minutes:02d}:00")
        self.refresh_all()

    def save_elapsed(self):
        if self.timer_total_seconds <= 0:
            messagebox.showinfo("No elapsed session", "Start the focus timer first. There is no elapsed time to save yet.", parent=self.root)
            return
        if self.timer_after:
            self.root.after_cancel(self.timer_after)
            self.timer_after = None
        self.timer_running = False
        try:
            self._save_timer_session()
        except (ValueError, OSError, tk.TclError) as exc:
            messagebox.showwarning("Could not save elapsed time", str(exc), parent=self.root)
            return
        self.timer_status.config(text="Elapsed focus time saved to your study ledger.")

    def generate_plan(self):
        try:
            available = int(self.available_var.get())
            block = int(self.chapter_minutes_var.get())
            plan = build_adaptive_plan(self.subjects, read_exams(), available,
                                       chapter_minutes=block, sessions=load_sessions(SESSION_FILE))
        except (ValueError, OSError) as exc:
            messagebox.showwarning("Check plan settings", str(exc), parent=self.root)
            return
        self.plan_table.delete(*self.plan_table.get_children())
        for item in plan:
            self.plan_table.insert("", "end", values=(item["subject"], item["chapter"], item["minutes"], item["reason"]))
        total = sum(x["minutes"] for x in plan)
        self.plan_summary.config(text=f"{len(plan)} suggested blocks • {total} planned minutes • Based on your pending chapters, upcoming exams and recent subject activity.")

    def show_recovery(self):
        missed = build_recovery_plan(read_timetable())
        self.plan_table.delete(*self.plan_table.get_children())
        for item in missed:
            self.plan_table.insert("", "end", values=(item["subject"], item["recovery"], "Reschedule", "Missed timetable block"))
        self.plan_summary.config(text=f"{len(missed)} earlier planned blocks today have passed and are not marked completed. These are recovery suggestions, not proof that you missed studying.")

    def schedule_selected_topic(self):
        selection = self.recent_table.selection()
        if not selection:
            messagebox.showinfo("Choose a session", "Select a recent session first.", parent=self.root)
            return
        values = self.recent_table.item(selection[0], "values")
        try:
            schedule_revision(REVISION_FILE, values[1], values[2])
        except (ValueError, OSError) as exc:
            messagebox.showwarning("Could not schedule revision", str(exc), parent=self.root)
            return
        self.refresh_revisions()
        self.tabs.select(self.revision_tab)

    def complete_selected_revision(self):
        selection = self.revision_table.selection()
        if not selection:
            messagebox.showinfo("Choose a review", "Select a due review first.", parent=self.root)
            return
        values = self.revision_table.item(selection[0], "values")
        try:
            complete_revision(REVISION_FILE, values[1], values[2])
        except (ValueError, OSError) as exc:
            messagebox.showwarning("Could not complete review", str(exc), parent=self.root)
            return
        self.refresh_revisions()

    def refresh_sessions(self):
        self.recent_table.delete(*self.recent_table.get_children())
        sessions = load_sessions(SESSION_FILE)
        for item in reversed(sessions[-12:]):
            self.recent_table.insert("", "end", values=(item["date"].isoformat(), item["subject"],
                                                        item.get("chapter", ""), item["minutes"],
                                                        item.get("session_type", "Focus")))

    def refresh_revisions(self):
        self.revision_table.delete(*self.revision_table.get_children())
        due = load_due_revisions(REVISION_FILE)
        for item in due:
            self.revision_table.insert("", "end", values=(item["due"].isoformat(), item["subject"],
                                                           item["chapter"], f'{item.get("interval_days", 1)} days'))
        self.revision_note.config(text=f"{len(due)} reviews due. Completed reviews automatically move to the next interval.")

    def refresh_stats(self):
        sessions = load_sessions(SESSION_FILE)
        stats = session_analytics(sessions)
        self.stats_summary.config(text=(
            f'Today: {stats["today_minutes"] // 60}h {stats["today_minutes"] % 60}m\n'
            f'Last 7 days: {stats["last_7_minutes"] // 60}h {stats["last_7_minutes"] % 60}m\n'
            f'Last 30 days: {stats["last_30_minutes"] // 60}h {stats["last_30_minutes"] % 60}m\n'
            f'Current streak: {stats["streak_days"]} days   •   Total sessions: {stats["session_count"]}'
        ))
        self.stats_table.delete(*self.stats_table.get_children())
        for subject, minutes in stats["by_subject"].items():
            self.stats_table.insert("", "end", values=(subject, f"{minutes / 60:.1f}", minutes))

    def refresh_all(self):
        self.refresh_sessions()
        self.refresh_revisions()
        self.refresh_stats()


def main():
    root = tk.Tk()
    StudyIntelligence(root)
    root.mainloop()


if __name__ == "__main__":
    main()
