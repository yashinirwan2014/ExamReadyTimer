"""Graphical Pomodoro timer for ExamReadyTimer."""
import csv
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from storage import initialize_user_data
from study_engine import log_session, schedule_revision

BG, NAVY, MUTED = "#0B1020", "#172544", "#9AA9C8"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
SESSION_FILE = DATA_DIR / "study_sessions.csv"
REVISION_FILE = DATA_DIR / "revision_schedule.csv"
SUBJECT_FILE = DATA_DIR / "dataorsubjects.csv"


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Pomodoro")
        root.geometry("520x570")
        root.minsize(420, 480)
        root.configure(bg=BG)
        root.option_add("*Foreground", "#E8EEFF")
        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#0B1020")
        style.configure("TLabel", background="#0B1020", foreground="#E8EEFF")
        style.configure("TButton", background="#263657", foreground="#E8EEFF", padding=7)
        style.map("TButton", background=[("active", "#34496F")])
        style.configure("TEntry", fieldbackground="#18243D", foreground="#E8EEFF")
        style.configure("TCombobox", fieldbackground="#18243D", background="#263657", foreground="#E8EEFF")
        style.configure("Treeview", background="#111B30", fieldbackground="#111B30", foreground="#E8EEFF")
        style.configure("Treeview.Heading", background="#263657", foreground="#E8EEFF")
        self.study_minutes = tk.IntVar(value=25)
        self.break_minutes = tk.IntVar(value=5)
        self.total_sessions = tk.IntVar(value=4)
        self.session = 1
        self.phase = "Study"
        self.remaining = 0
        self.phase_duration_seconds = 0
        self.running = False
        self.completed = False
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
        tk.Label(header, text="Pomodoro Timer", bg=NAVY, fg="#18243D",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Focus deeply. Rest properly. Repeat.",
                 bg=NAVY, fg="#C7D4F2", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=24, pady=22)
        body.pack(fill="both", expand=True)
        settings = tk.Frame(body, bg=BG)
        settings.pack(fill="x")
        for col, (label, var) in enumerate((("Study minutes", self.study_minutes),
                                             ("Break minutes", self.break_minutes),
                                             ("Sessions", self.total_sessions))):
            tk.Label(settings, text=label, bg=BG, fg=MUTED).grid(row=0, column=col, padx=5)
            tk.Spinbox(settings, from_=1, to=180 if col < 2 else 20, width=7,
                       textvariable=var, justify="center").grid(row=1, column=col, padx=5, pady=6)
        study_target = tk.Frame(body, bg=BG)
        study_target.pack(fill="x", pady=(12, 0))
        tk.Label(study_target, text="Subject (optional)", bg=BG, fg=MUTED).grid(row=0, column=0, sticky="w")
        self.subject_combo = ttk.Combobox(study_target, textvariable=self.subject_var,
                                          values=sorted(self.subjects), state="readonly", width=22)
        self.subject_combo.grid(row=1, column=0, padx=(0, 8), sticky="ew")
        self.subject_combo.bind("<<ComboboxSelected>>", self.update_chapters)
        tk.Label(study_target, text="Chapter / topic", bg=BG, fg=MUTED).grid(row=0, column=1, sticky="w")
        self.chapter_combo = ttk.Combobox(study_target, textvariable=self.chapter_var, state="normal", width=24)
        self.chapter_combo.grid(row=1, column=1, sticky="ew")
        study_target.columnconfigure(0, weight=1)
        study_target.columnconfigure(1, weight=1)
        self.phase_label = tk.Label(body, text="Ready to focus?", bg=BG, fg=NAVY,
                                    font=("Arial", 16, "bold"))
        self.phase_label.pack(pady=(35, 5))
        self.clock = tk.Label(body, text="25:00", bg=BG, fg=NAVY, font=("Arial", 54, "bold"))
        self.clock.pack(pady=4)
        self.progress = ttk.Progressbar(body, maximum=100, mode="determinate")
        self.progress.pack(fill="x", pady=14)
        self.session_label = tk.Label(body, text="Session 1 of 4", bg=BG, fg=MUTED)
        self.session_label.pack()
        controls = tk.Frame(body, bg=BG)
        controls.pack(pady=24)
        ttk.Button(controls, text="Start", command=self.start).pack(side="left", padx=5)
        ttk.Button(controls, text="Pause", command=self.pause).pack(side="left", padx=5)
        ttk.Button(controls, text="Reset", command=self.reset).pack(side="left", padx=5)
        tk.Label(body, text="You can pause or reset a session at any time.",
                 bg=BG, fg=MUTED, font=("Arial", 9)).pack(pady=(8, 0))

    def start(self):
        if self.completed:
            messagebox.showinfo("Sessions completed", "Reset the timer to begin another set of sessions.", parent=self.root)
            return
        if self.running:
            return
        if self.remaining <= 0:
            try:
                if self.study_minutes.get() < 1 or self.break_minutes.get() < 1 or self.total_sessions.get() < 1:
                    raise ValueError
            except (tk.TclError, ValueError):
                messagebox.showwarning("Check your settings", "Use positive whole numbers for all timer settings.", parent=self.root)
                return
            self.phase_duration_seconds = (self.study_minutes.get() if self.phase == "Study" else self.break_minutes.get()) * 60
            self.remaining = self.phase_duration_seconds
        self.running = True
        self.tick()

    def tick(self):
        self.clock.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        self.phase_label.config(text=f"{self.phase} time")
        self.session_label.config(text=f"Session {self.session} of {self.total_sessions.get()}")
        total = max(self.phase_duration_seconds, 1)
        self.progress["value"] = 100 * (1 - self.remaining / total)
        if self.remaining <= 0:
            self.root.bell()
            if self.phase == "Study":
                self.record_study_block()
                if self.session >= self.total_sessions.get():
                    self.running = False
                    self.completed = True
                    self.phase_label.config(text="All sessions completed! 🎉")
                    messagebox.showinfo("Well done!", "You've completed all your Pomodoro sessions.", parent=self.root)
                    return
                self.phase = "Break"
            else:
                self.phase = "Study"
                self.session += 1
            self.phase_duration_seconds = (self.study_minutes.get() if self.phase == "Study" else self.break_minutes.get()) * 60
            self.remaining = self.phase_duration_seconds
            messagebox.showinfo("Session complete", f"Time for {self.phase.lower()}!", parent=self.root)
            self.tick()
            return
        self.remaining -= 1
        self.after_id = self.root.after(1000, self.tick)

    def update_chapters(self, _event=None):
        chapters = self.subjects.get(self.subject_var.get(), [])
        self.chapter_combo["values"] = chapters
        if chapters and self.chapter_var.get() not in chapters:
            self.chapter_var.set(chapters[0])

    def record_study_block(self):
        subject = self.subject_var.get().strip()
        chapter = self.chapter_var.get().strip()
        if not subject:
            return
        try:
            log_session(SESSION_FILE, subject, chapter, max(1, self.phase_duration_seconds // 60), "Pomodoro")
            if chapter:
                schedule_revision(REVISION_FILE, subject, chapter)
        except (OSError, ValueError) as exc:
            messagebox.showwarning("Study log not saved", str(exc), parent=self.root)

    def pause(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def reset(self):
        self.pause()
        self.session, self.phase, self.remaining = 1, "Study", 0
        self.phase_duration_seconds = 0
        self.completed = False
        self.clock.config(text=f"{self.study_minutes.get():02d}:00")
        self.phase_label.config(text="Ready to focus?")
        self.session_label.config(text=f"Session 1 of {self.total_sessions.get()}")
        self.progress["value"] = 0


def main():
    root = tk.Tk()
    PomodoroTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
