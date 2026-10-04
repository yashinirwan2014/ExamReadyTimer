
import tkinter as tk
import subprocess
import sys

window = tk.Tk()

window.title("ExamReadyTimer | Study Dashboard")
window.geometry("750x650")
window.configure(bg="#F3F5FB")

title = tk.Label(
    window,
    text="ExamReady",
    font=("Arial", 30, "bold"),
    bg="#F3F5FB",
    fg="#25316D"
)
title.pack(pady=(25, 5))

subtitle = tk.Label(
    window,
    text="STUDY  •  FOCUS  •  PREPARE",
    font=("Arial", 11),
    bg="#F3F5FB",
    fg="#68708A"
)
subtitle.pack(pady=(0, 20))

description = tk.Label(
    window,
    text="What would you like to work on today?",
    font=("Arial", 14),
    bg="#F3F5FB",
    fg="#30364F"
)
description.pack(pady=10)


def open_feature(filename):
    subprocess.Popen([sys.executable, filename])


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
        width=25,
        height=2,
        bg="#FFFFFF",
        fg="#25316D",
        activebackground="#DDE4FF",
        relief="flat",
        cursor="hand2",
        command=lambda f=filename: open_feature(f)
    )

    button.pack(pady=6)

footer = tk.Label(
    window,
    text="One chapter at a time. One step closer.",
    font=("Arial", 10, "italic"),
    bg="#F3F5FB",
    fg="#68708A"
)
footer.pack(pady=20)

window.mainloop()
