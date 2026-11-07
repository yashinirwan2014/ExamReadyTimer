"""Distraction-free focus timer for ExamReadyTimer."""
import tkinter as tk
from tkinter import ttk, messagebox

BG, NAVY, MUTED = "#F3F5FB", "#25316D", "#68708A"


class FocusMode:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Focus Mode")
        root.geometry("500x480")
        root.minsize(400, 400)
        root.configure(bg=BG)
        self.minutes = tk.IntVar(value=50)
        self.remaining = 0
        self.running = False
        self.after_id = None
        self.build()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Focus Mode", bg=NAVY, fg="white",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="One task. One session. No distractions.",
                 bg=NAVY, fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=26, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Focus duration (minutes)", bg=BG, fg=MUTED).pack()
        tk.Spinbox(body, from_=1, to=240, width=8, textvariable=self.minutes,
                   justify="center").pack(pady=8)
        self.clock = tk.Label(body, text="50:00", bg=BG, fg=NAVY,
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
            self.remaining = self.minutes.get() * 60
        self.running = True
        self.status.config(text="Focus session in progress 📚")
        self.tick()

    def tick(self):
        self.clock.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        total = max(self.minutes.get() * 60, 1)
        self.progress["value"] = 100 * (1 - self.remaining / total)
        if self.remaining <= 0:
            self.running = False
            self.status.config(text="Focus session completed! 🎯")
            self.root.bell()
            messagebox.showinfo("Session complete", "Great work! Take a short break.", parent=self.root)
            return
        self.remaining -= 1
        self.after_id = self.root.after(1000, self.tick)

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
        self.clock.config(text=f"{self.minutes.get():02d}:00")
        self.status.config(text="Ready when you are.")
        self.progress["value"] = 0


def main():
    root = tk.Tk()
    FocusMode(root)
    root.mainloop()


if __name__ == "__main__":
    main()
