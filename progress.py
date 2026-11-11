"""Graphical syllabus progress analytics for ExamReadyTimer."""
import csv
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from storage import initialize_user_data
from theme import apply_dark_theme
from navigation import add_home_button

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
DATA_FILE = DATA_DIR / "dataorsubjects.csv"
BG, NAVY, MUTED = "#0B1020", "#172544", "#FFFFFF"


def calculate_progress(path=DATA_FILE):
    results = {}
    if not path.exists():
        return results
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            subject = (row.get("Subject") or "").strip()
            chapter = (row.get("Chapter") or "").strip()
            if not subject or not chapter or chapter.casefold() == "full subject syllabus":
                continue
            entry = results.setdefault(subject, {"total": 0, "completed": 0})
            entry["total"] += 1
            if (row.get("Status") or "").strip().casefold() == "completed":
                entry["completed"] += 1
    for item in results.values():
        item["percentage"] = round(item["completed"] / item["total"] * 100, 1) if item["total"] else 0.0
    return results


class ProgressAnalytics:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Progress Analytics")
        root.geometry("760x600")
        root.minsize(600, 450)
        apply_dark_theme(root)
        add_home_button(self.root)
        self.build()
        self.refresh()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Progress Analytics", bg=NAVY, fg="#E8EEFF",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Small steps add up. See how far you've come.",
                 bg=NAVY, fg="#FFFFFF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)
        self.summary = tk.Label(body, text="", bg=BG, fg="#E8EEFF", font=("Arial", 15, "bold"))
        self.summary.pack(anchor="w", pady=(0, 12))
        self.canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=BG)
        self.inner.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        ttk.Button(body, text="Refresh progress", command=self.refresh).pack(anchor="e", pady=(12, 0))
        tk.Label(self.root, text="Progress is calculated from your syllabus tracker.",
                 bg=BG, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=24, pady=(0, 12))

    def refresh(self):
        for child in self.inner.winfo_children():
            child.destroy()
        try:
            results = calculate_progress()
        except OSError as exc:
            messagebox.showerror("Could not read progress", str(exc), parent=self.root)
            return
        total = sum(x["total"] for x in results.values())
        done = sum(x["completed"] for x in results.values())
        overall = round(done / total * 100) if total else 0
        self.summary.config(text=f"Overall: {done} of {total} chapters completed  •  {overall}%")
        if not results:
            tk.Label(self.inner, text="No chapter data yet. Add chapters in Subject Tracker to see your progress.",
                     bg=BG, fg=MUTED, wraplength=560, justify="left").pack(anchor="w", pady=20)
            return
        for subject, item in sorted(results.items()):
            card = tk.Frame(self.inner, bg="#18243D", padx=14, pady=12, highlightthickness=1,
                            highlightbackground="#34415D")
            card.pack(fill="x", pady=5)
            top = tk.Frame(card, bg="#18243D")
            top.pack(fill="x")
            tk.Label(top, text=subject, bg="#18243D", fg="#E8EEFF",
                     font=("Arial", 11, "bold")).pack(side="left")
            tk.Label(top, text=f'{item["completed"]}/{item["total"]}  •  {item["percentage"]:.0f}%',
                     bg="#18243D", fg=MUTED).pack(side="right")
            bar = ttk.Progressbar(card, maximum=100, value=item["percentage"])
            bar.pack(fill="x", pady=(9, 0))


def main():
    root = tk.Tk()
    ProgressAnalytics(root)
    root.mainloop()


if __name__ == "__main__":
    main()
