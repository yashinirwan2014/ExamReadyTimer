"""Graphical Pomodoro timer for ExamReadyTimer."""
import csv
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from storage import initialize_user_data
from theme import apply_dark_theme
from navigation import add_home_button
from study_engine import log_session, schedule_revision
from completion_sound import play_completion_chime
from session_state import clear_session, load_session, save_session

BG, NAVY, MUTED = "#080808", "#101010", "#FFFFFF"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
SESSION_FILE = DATA_DIR / "study_sessions.csv"
REVISION_FILE = DATA_DIR / "revision_schedule.csv"
SESSION_STATE_FILE = DATA_DIR / "pomodoro_state.json"
SUBJECT_FILE = DATA_DIR / "dataorsubjects.csv"


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Pomodoro")
        root.geometry("520x570")
        root.minsize(420, 480)
        apply_dark_theme(root)
        self.study_minutes = tk.IntVar(value=25)
        self.break_minutes = tk.IntVar(value=5)
        self.total_sessions = tk.IntVar(value=4)
        self.session = 1
        self.phase = "Study"
        self.remaining = 0
        self.phase_duration_seconds = 0
        self.running = False
        self.completed = False
        self.saved_session_pending = False
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
        self.restore_saved_session()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        add_home_button(self.root, self.close)

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Pomodoro Timer", bg=NAVY, fg="#FFFFFF",
                 font=("Momo Trust Display", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Focus deeply. Rest properly. Repeat.",
                 bg=NAVY, fg="#FFFFFF", font=("Momo Trust Display", 10)).pack(anchor="w", pady=(4, 0))
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
        self.phase_label = tk.Label(body, text="Ready to focus?", bg=BG, fg="#FFFFFF",
                                    font=("Momo Trust Display", 16, "bold"))
        self.phase_label.pack(pady=(35, 5))
        self.clock = tk.Label(body, text="25:00", bg=BG, fg="#FFFFFF", font=("Momo Trust Display", 54, "bold"))
        self.clock.pack(pady=4)
        self.progress = ttk.Progressbar(body, maximum=100, mode="determinate")
        self.progress.pack(fill="x", pady=14)
        self.session_label = tk.Label(body, text="Session 1 of 4", bg=BG, fg=MUTED)
        self.session_label.pack()
        # Keep every timer action in a clearly visible, roomy two-row control panel.
        controls = tk.Frame(body, bg=BG)
        controls.pack(fill="x", pady=18)
        self.start_button = ttk.Button(controls, text="Start", command=self.start, width=14)
        self.pause_button = ttk.Button(controls, text="Pause", command=self.pause, width=14)
        self.resume_button = ttk.Button(controls, text="Resume", command=self.resume, width=14)
        self.stop_button = ttk.Button(controls, text="Stop", command=self.stop, width=14)
        self.reset_button = ttk.Button(controls, text="Reset", command=self.reset, width=14)
        for button, row, column in (
            (self.start_button, 0, 0), (self.pause_button, 0, 1),
            (self.resume_button, 0, 2), (self.stop_button, 1, 0),
            (self.reset_button, 1, 1),
        ):
            button.grid(row=row, column=column, padx=5, pady=5, sticky="ew")
        for column in range(3):
            controls.columnconfigure(column, weight=1)
        tk.Label(body, text="Pause keeps your remaining time. Stop ends the current timer; Reset starts the set over.",
                 bg=BG, fg=MUTED, font=("Momo Trust Display", 9),
                 wraplength=430, justify="center").pack(pady=(4, 0))

    def start(self):
        if self.completed:
            messagebox.showinfo("Sessions completed", "Reset the timer to begin another set of sessions.", parent=self.root)
            return
        if self.saved_session_pending:
            replace_saved = messagebox.askyesno(
                "Saved session available",
                "Starting a new session will replace the saved unfinished session. Start a new session?",
                parent=self.root,
            )
            if not replace_saved:
                return
            self.saved_session_pending = False
            clear_session(SESSION_STATE_FILE)
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
        self.save_state()
        self.tick()

    def resume(self):
        """Resume a paused or restored session without resetting its remaining time."""
        if self.running:
            return
        if self.remaining <= 0:
            messagebox.showinfo("Nothing to resume", "Press Start to begin a new focus session.", parent=self.root)
            return
        if self.completed:
            messagebox.showinfo("Sessions completed", "Reset the timer before starting another set.", parent=self.root)
            return
        self.start()

    def tick(self):
        self.after_id = None
        self.clock.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        self.phase_label.config(text=f"{self.phase} time")
        self.session_label.config(text=f"Session {self.session} of {self.total_sessions.get()}")
        total = max(self.phase_duration_seconds, 1)
        self.progress["value"] = 100 * (1 - self.remaining / total)
        if self.remaining <= 0:
            play_completion_chime(self.root.bell)
            if self.phase == "Study":
                self.record_study_block()
                if self.session >= self.total_sessions.get():
                    self.running = False
                    self.completed = True
                    self.phase_label.config(text="All sessions completed! 🎉")
                    self.clock.config(text="00:00")
                    self.progress["value"] = 100
                    clear_session(SESSION_STATE_FILE)
                    return
                self.phase = "Break"
            else:
                self.phase = "Study"
                self.session += 1
            self.phase_duration_seconds = (
                self.study_minutes.get() if self.phase == "Study" else self.break_minutes.get()
            ) * 60
            self.remaining = self.phase_duration_seconds
            self.phase_label.config(text=f"{self.phase} time — starting now")
            self.clock.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
            self.session_label.config(text=f"Session {self.session} of {self.total_sessions.get()}")
            self.progress["value"] = 0
            self.save_state()
            self.after_id = self.root.after(1000, self.tick)
            return
        self.remaining -= 1
        self.save_state()
        self.after_id = self.root.after(1000, self.tick)

    def save_state(self):
        if self.completed:
            clear_session(SESSION_STATE_FILE)
            return
        save_session(SESSION_STATE_FILE, {
            "study_minutes": self.study_minutes.get(),
            "break_minutes": self.break_minutes.get(),
            "total_sessions": self.total_sessions.get(),
            "session": self.session,
            "phase": self.phase,
            "remaining": self.remaining,
            "phase_duration_seconds": self.phase_duration_seconds,
            "completed": self.completed,
            "subject": self.subject_var.get(),
            "chapter": self.chapter_var.get(),
            "running": False,
        })

    def restore_saved_session(self):
        state = load_session(SESSION_STATE_FILE)
        if state is None:
            return
        if not messagebox.askyesno(
            "Continue previous session",
            "A previous Pomodoro session was saved. Would you like to continue where you left off?",
            parent=self.root,
        ):
            # Keep the snapshot and prevent a new timer from silently overwriting it.
            self.saved_session_pending = True
            return
        self.study_minutes.set(state["study_minutes"])
        self.break_minutes.set(state["break_minutes"])
        self.total_sessions.set(state["total_sessions"])
        self.session = state["session"]
        self.phase = state["phase"]
        self.remaining = state["remaining"]
        self.phase_duration_seconds = state["phase_duration_seconds"]
        self.completed = state["completed"]
        self.subject_var.set(state["subject"])
        self.chapter_var.set(state["chapter"])
        self.update_chapters()
        self.clock.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        self.phase_label.config(text=f"{self.phase} time — session restored")
        self.session_label.config(text=f"Session {self.session} of {self.total_sessions.get()}")
        total = max(self.phase_duration_seconds, 1)
        self.progress["value"] = 100 * (1 - self.remaining / total)

    def close(self):
        self.pause()
        self.save_state()
        self.root.destroy()

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
        self.save_state()

    def stop(self):
        """End the current timer and return to the ready state."""
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.session, self.phase, self.remaining = 1, "Study", 0
        self.phase_duration_seconds = 0
        self.completed = False
        self.saved_session_pending = False
        clear_session(SESSION_STATE_FILE)
        self.clock.config(text=f"{self.study_minutes.get():02d}:00")
        self.phase_label.config(text="Stopped — ready to focus?")
        self.session_label.config(text=f"Session 1 of {self.total_sessions.get()}")
        self.progress["value"] = 0

    def reset(self):
        self.pause()
        self.session, self.phase, self.remaining = 1, "Study", 0
        self.phase_duration_seconds = 0
        self.completed = False
        clear_session(SESSION_STATE_FILE)
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
