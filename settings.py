"""Settings and data backup/restore window for ExamReadyTimer."""
import os
import subprocess
import sys
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from storage import initialize_user_data
from backup import backup_data, restore_data

BG, NAVY, MUTED = "#F3F5FB", "#25316D", "#68708A"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)


class SettingsWindow:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Settings & Backup")
        root.geometry("650x470")
        root.minsize(520, 400)
        root.configure(bg=BG)
        self.build()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Settings & Data Safety", bg=NAVY, fg="white",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Your study data belongs to you. Keep it safe.",
                 bg=NAVY, fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=24, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="STUDENT DATA", bg=BG, fg=NAVY,
                 font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(body, text="Exam dates, timetable entries and syllabus progress are stored here:",
                 bg=BG, fg=MUTED, wraplength=570, justify="left").pack(anchor="w", pady=(7, 5))
        path_box = tk.Frame(body, bg="white", padx=12, pady=12)
        path_box.pack(fill="x", pady=(0, 14))
        tk.Label(path_box, text=str(DATA_DIR), bg="white", fg=NAVY,
                 wraplength=550, justify="left").pack(anchor="w")
        ttk.Button(body, text="Open data folder", command=self.open_folder).pack(anchor="w", pady=(0, 18))
        tk.Label(body, text="BACKUP & RESTORE", bg=BG, fg=NAVY,
                 font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(body, text="Create a ZIP backup before changing devices or reinstalling. Restoring replaces matching data files.",
                 bg=BG, fg=MUTED, wraplength=570, justify="left").pack(anchor="w", pady=(7, 12))
        controls = tk.Frame(body, bg=BG)
        controls.pack(anchor="w")
        ttk.Button(controls, text="Create backup", command=self.create_backup).pack(side="left", padx=(0, 8))
        ttk.Button(controls, text="Restore backup", command=self.restore_backup).pack(side="left")
        tk.Label(body, text="Tip: Keep a copy of your backup somewhere separate from your computer.",
                 bg=BG, fg=MUTED, font=("Arial", 9), wraplength=560).pack(anchor="w", pady=(22, 0))

    def open_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(DATA_DIR)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(DATA_DIR)])
            else:
                subprocess.Popen(["xdg-open", str(DATA_DIR)])
        except (OSError, AttributeError) as exc:
            messagebox.showerror("Could not open folder", str(exc), parent=self.root)

    def create_backup(self):
        destination = filedialog.asksaveasfilename(
            parent=self.root, title="Save ExamReadyTimer backup",
            defaultextension=".zip", filetypes=[("ZIP backup", "*.zip")],
            initialfile="ExamReadyTimer-Backup.zip")
        if not destination:
            return
        try:
            backup_data(destination, DATA_DIR)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Backup failed", str(exc), parent=self.root)
            return
        messagebox.showinfo("Backup created", f"Your backup was saved to:\n{destination}", parent=self.root)

    def restore_backup(self):
        source = filedialog.askopenfilename(
            parent=self.root, title="Choose an ExamReadyTimer backup",
            filetypes=[("ZIP backup", "*.zip")])
        if not source:
            return
        if not messagebox.askyesno(
            "Replace existing data?",
            "Restoring will replace matching exam, timetable and syllabus files. Continue?",
            parent=self.root
        ):
            return
        try:
            restored = restore_data(source, DATA_DIR)
        except Exception as exc:
            messagebox.showerror("Restore failed", str(exc), parent=self.root)
            return
        messagebox.showinfo("Restore complete", "Restored: " + ", ".join(restored) +
                            "\nClose and reopen any open ExamReadyTimer windows to refresh their data.",
                            parent=self.root)


def main():
    root = tk.Tk()
    SettingsWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
