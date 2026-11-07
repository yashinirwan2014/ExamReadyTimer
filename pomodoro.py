"""Graphical Pomodoro timer for ExamReadyTimer."""
import sys\nfrom pathlib import Path\nimport tkinter as tk
from tkinter import ttk, messagebox

BG, NAVY, MUTED = "#F3F5FB", "#25316D", "#68708A"


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Pomodoro")
        root.geometry("520x570")
        root.minsize(420, 480)
        root.configure(bg=BG)
        self.study_minutes = tk.IntVar(value=25)
        self.break_minutes = tk.IntVar(value=5)
        self.total_sessions = tk.IntVar(value=4)
        self.session = 1
        self.phase = "Study"
        self.remaining = 0
        self.running = False
        self.after_id = None
        self.build()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Pomodoro Timer", bg=NAVY, fg="white",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Focus deeply. Rest properly. Repeat.",
                 bg=NAVY, fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
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
        if self.running:
            return
        if self.remaining <= 0:
            try:
                if self.study_minutes.get() < 1 or self.break_minutes.get() < 1 or self.total_sessions.get() < 1:
                    raise ValueError
            except (tk.TclError, ValueError):
                messagebox.showwarning("Check your settings", "Use positive whole numbers for all timer settings.", parent=self.root)
                return
            self.remaining = (self.study_minutes.get() if self.phase == "Study" else self.break_minutes.get()) * 60
        self.running = True
        self.tick()

    def tick(self):
        self.clock.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        self.phase_label.config(text=f"{self.phase} time")
        self.session_label.config(text=f"Session {self.session} of {self.total_sessions.get()}")
        total = (self.study_minutes.get() if self.phase == "Study" else self.break_minutes.get()) * 60
        self.progress["value"] = 100 * (1 - self.remaining / max(total, 1))
        if self.remaining <= 0:
            self.root.bell()
            if self.phase == "Study":
                if self.session >= self.total_sessions.get():
                    self.running = False
                    self.phase_label.config(text="All sessions completed! 🎉")
                    messagebox.showinfo("Well done!", "You've completed all your Pomodoro sessions.", parent=self.root)
                    return
                self.phase = "Break"
            else:
                self.phase = "Study"
                self.session += 1
            self.remaining = (self.study_minutes.get() if self.phase == "Study" else self.break_minutes.get()) * 60
            messagebox.showinfo("Session complete", f"Time for {self.phase.lower()}!", parent=self.root)
            self.tick()
            return
        self.remaining -= 1
        self.after_id = self.root.after(1000, self.tick)

    def pause(self):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def reset(self):
        self.pause()
        self.session, self.phase, self.remaining = 1, "Study", 0
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
