"""Distraction-free focus timer for ExamReadyTimer."""
import csv
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from storage import initialize_user_data
from theme import apply_dark_theme
from study_engine import log_session, schedule_revision

BG, NAVY, MUTED = "#0B1020", "#172544", "#FFFFFF"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
SESSION_FILE = DATA_DIR / "study_sessions.csv"
REVISION_FILE = DATA_DIR / "revision_schedule.csv"
SUBJECT_FILE = DATA_DIR / "dataorsubjects.csv"


class FocusMode:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Focus Mode")
        root.geometry("500x480")
        root.minsize(400, 400)
        apply_dark_theme(root)
        self.minutes = tk.IntVar(value=50)
        self.remaining = 0
        self.total_seconds = 0
        self.running = False
        self.after_id = None
        self.subjects = {}
        if SUBJECT_FILE.exists():
            with SUBJECT_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
                for row in csv.DictReader(stream):
                    subject = (row.get("Subject") or "").strip()
                    chapter = (row.get("Chapter") or "").strip()
                    if subject and chapter and chapter.casefold() != "full subject syllabus":
                        self.subjects.setdefault(subject, []).append(chapter)
        self.subject_var = tk.StringVar()
        self.chapter_var = tk.StringVar()
        self.build()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Focus Mode", bg=NAVY, fg="#E8EEFF",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="One task. One session. Stay on track.",
                 bg=NAVY, fg="#FFFFFF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=26, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Subject (optional)", bg=BG, fg=MUTED).pack()
        self.subject_combo = ttk.Combobox(body, textvariable=self.subject_var,
                                          values=sorted(self.subjects), state="readonly", width=34)
        self.subject_combo.pack(pady=(4, 8))
        self.subject_combo.bind("<<ComboboxSelected>>", self.update_chapters)
        tk.Label(body, text="Chapter / topic", bg=BG, fg=MUTED).pack()
        self.chapter_combo = ttk.Combobox(body, textvariable=self.chapter_var, state="normal", width=34)
        self.chapter_combo.pack(pady=(4, 8))
        tk.Label(body, text="Focus duration (minutes)", bg=BG, fg=MUTED).pack()
        tk.Spinbox(body, from_=1, to=240, width=8, textvariable=self.minutes,
                   justify="center").pack(pady=8)
        self.clock = tk.Label(body, text="50:00", bg=BG, fg="#E8EEFF",
                              font=("Arial", 54, "bold"))
        self.clock.pack(pady=18)
        self.status = tk.Label(body, text="Ready when you are.", bg=BG, fg=MUTED)
        self.status.pack()
        self.progress = ttk.Progressbar(body, maximum=100)
        self.progress.pack(fill="x", pady=18)
        controls = tk.Frame(body, bg=BG)
        controls.pack(pady=10)
        ttk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5)
        ttk.Button(controls, text="Pause", command=self.pause).pack(side="left", padx=5)
        ttk.Button(controls, text="Reset", command=self.reset).pack(side="left", padx=5)

    def start(self):
        if self.running:
            return
        if self.remaining <= 0:
            try:
                if self.minutes.get() < 1:
                    raise ValueError
            except (tk.TclError, ValueError):
                messagebox.showwarning("Invalid duration", "Choose a whole number between 1 and 240.", parent=self.root)
                return
            self.total_seconds = self.minutes.get() * 60
            self.remaining = self.total_seconds
        self.running = True
        self.status.config(text="Focus session in progress 📚")
        self.tick()

    def tick(self):
        self.clock.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        total = max(self.total_seconds, 1)
        self.progress["value"] = 100 * (1 - self.remaining / total)
        if self.remaining <= 0:
            self.running = False
            self.status.config(text="Focus session completed! 🎯")
            self.record_completed_session()
            self.total_seconds = 0
            self.root.bell()
            messagebox.showinfo("Session complete", "Great work! Your completed session has been logged when a subject was selected.", parent=self.root)
            return
        self.remaining -= 1
        self.after_id = self.root.after(1000, self.tick)

    def update_chapters(self, _event=None):
        chapters = self.subjects.get(self.subject_var.get(), [])
        self.chapter_combo["values"] = chapters
        if chapters and self.chapter_var.get() not in chapters:
            self.chapter_var.set(chapters[0])

    def record_completed_session(self):
        subject = self.subject_var.get().strip()
        chapter = self.chapter_var.get().strip()
        if not subject:
            return
        try:
            log_session(SESSION_FILE, subject, chapter, max(1, self.total_seconds // 60), "Focus")
            if chapter:
                schedule_revision(REVISION_FILE, subject, chapter)
        except (OSError, ValueError) as exc:
            messagebox.showwarning("Study log not saved", str(exc), parent=self.root)

    def pause(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if self.remaining:
            self.status.config(text="Paused")

    def reset(self):
        self.pause()
        self.remaining = 0
        self.total_seconds = 0
        self.clock.config(text=f"{self.minutes.get():02d}:00")
        self.status.config(text="Ready when you are.")
        self.progress["value"] = 0


def main():
    root = tk.Tk()
    FocusMode(root)
    root.mainloop()


if __name__ == "__main__":
    main()
