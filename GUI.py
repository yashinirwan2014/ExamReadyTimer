import tkinter as tk
import subprocess
import sys
from pathlib import Path

window = tk.Tk()

window.title("ExamReadyTimer | Study Dashboard")
window.geometry("750x700")
window.configure(bg="#F3F5FB")


def open_feature(filename):
    app_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    if getattr(sys, "frozen", False):
        executable_names = {\n            "countdown.py": "ExamCountdown",\n            "pomodoro.py": "PomodoroTimer",\n            "timetable.py": "StudyTimetable",\n            "tracker.py": "SubjectTracker",\n            "progress.py": "ProgressAnalytics",\n            "focus.py": "FocusMode",\n        }\n        executable_name = executable_names[filename] + (".exe" if sys.platform == "win32" else "")
        command = [str(app_dir / executable_name)]
    else:
        command = [sys.executable, str(app_dir / filename)]

    subprocess.Popen(command, cwd=str(app_dir))


title = tk.Label(
    window,
    text="ExamReady",
    font=("Arial", 30, "bold"),
    bg="#F3F5FB",
    fg="#25316D"
)
title.pack(pady=(30, 5))

subtitle = tk.Label(
    window,
    text="STUDY  •  FOCUS  •  PREPARE",
    font=("Arial", 11),
    bg="#F3F5FB",
    fg="#68708A"
)
subtitle.pack()

description = tk.Label(
    window,
    text="Your personal exam preparation dashboard",
    font=("Arial", 14),
    bg="#F3F5FB",
    fg="#30364F"
)
description.pack(pady=(25, 20))

features = [
    ("Exam Countdown", "countdown.py"),
    ("Pomodoro Timer", "pomodoro.py"),
    ("Study Timetable", "timetable.py"),
    ("Subject Tracker", "tracker.py"),
    ("Progress Analytics", "progress.py"),
    ("Focus Mode", "focus.py")
]

for feature, filename in features:
    button = tk.Button(
        window,
        text=feature,
        font=("Arial", 13, "bold"),
        width=28,
        height=2,
        bg="#FFFFFF",
        fg="#25316D",
        activebackground="#DDE4FF",
        relief="flat",
        cursor="hand2",
        command=lambda f=filename: open_feature(f)
    )
    button.pack(pady=5)

footer = tk.Label(
    window,
    text="One chapter at a time. One step closer.",
    font=("Arial", 10, "italic"),
    bg="#F3F5FB",
    fg="#68708A"
)
footer.pack(pady=25)

window.mainloop()
