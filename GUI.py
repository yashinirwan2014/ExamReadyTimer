import tkinter as tk
import subprocess
import sys
from pathlib import Path

from storage import initialize_user_data
from theme import apply_dark_theme

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
USER_DATA_DIR = initialize_user_data(app_dir=APP_DIR)

window = tk.Tk()

window.title("ExamReadyTimer | Study Dashboard")
window.geometry("750x760")
window.minsize(520, 600)
apply_dark_theme(window)


def open_feature(filename):
    app_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    if getattr(sys, "frozen", False):
        executable_names = {
            "countdown.py": "ExamCountdown",
            "pomodoro.py": "PomodoroTimer",
            "timetable.py": "StudyTimetable",
            "tracker.py": "SubjectTracker",
            "progress.py": "ProgressAnalytics",
            "focus.py": "FocusMode",
            "settings.py": "ExamReadySettings",
            "readiness.py": "ExamReadiness",
            "studyhub.py": "StudyIntelligence",
        }
        executable_name = executable_names[filename] + (".exe" if sys.platform == "win32" else "")
        command = [str(app_dir / executable_name)]
    else:
        command = [sys.executable, str(app_dir / filename)]

    subprocess.Popen(command, cwd=str(USER_DATA_DIR))


title = tk.Label(
    window,
    text="ExamReady",
    font=("Arial", 30, "bold"),
    bg="#0B1020",
    fg="#E8EEFF"
)
title.pack(pady=(24, 5))

subtitle = tk.Label(
    window,
    text="STUDY  •  FOCUS  •  PREPARE",
    font=("Arial", 11),
    bg="#0B1020",
    fg="#FFFFFF"
)
subtitle.pack()

description = tk.Label(
    window,
    text="Your personal exam preparation dashboard",
    font=("Arial", 14),
    bg="#0B1020",
    fg="#E8EEFF"
)
description.pack(pady=(18, 14))

features = [
    ("Exam Readiness Gap Engine", "readiness.py"),
    ("Study Intelligence Suite", "studyhub.py"),
    ("Exam Countdown", "countdown.py"),
    ("Pomodoro Timer", "pomodoro.py"),
    ("Study Timetable", "timetable.py"),
    ("Subject Tracker", "tracker.py"),
    ("Progress Analytics", "progress.py"),
    ("Focus Mode", "focus.py"),
    ("Settings & Backup", "settings.py")
]

for feature, filename in features:
    button = tk.Button(
        window,
        text=feature,
        font=("Arial", 12, "bold"),
        width=32,
        height=2,
        bg="#18243D",
        fg="#E8EEFF",
        activebackground="#34496F",
        relief="flat",
        cursor="hand2",
        command=lambda f=filename: open_feature(f)
    )
    button.pack(pady=4)

footer = tk.Label(
    window,
    text="One chapter at a time. One step closer.",
    font=("Arial", 10, "italic"),
    bg="#0B1020",
    fg="#FFFFFF"
)
footer.pack(pady=16)

window.mainloop()
