"""Graphical exam countdown manager for ExamReadyTimer."""
import csv
from datetime import date, datetime
import sys
from pathlib import Path\nimport tkinter as tk
from tkinter import ttk, messagebox
from storage import initialize_user_data

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent\nDATA_DIR = initialize_user_data(app_dir=APP_DIR)
DATA_FILE = DATA_DIR / "dataexams.csv"
BG, NAVY, MUTED = "#F3F5FB", "#25316D", "#68708A"


def read_exams():
    exams = []
    if DATA_FILE.exists():
        with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
            for row in csv.DictReader(stream):
                try:
                    name = (row.get("Exam") or "").strip()
                    exam_date = date(int(row["Year"]), int(row["Month"]), int(row["Day"]))
                    if name:
                        exams.append({"name": name, "date": exam_date})
                except (KeyError, TypeError, ValueError):
                    continue
    return exams


def save_exams(exams):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".csv.tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Exam", "Year", "Month", "Day"])
        for item in exams:
            d = item["date"]
            writer.writerow([item["name"], d.year, d.month, d.day])
    temp.replace(DATA_FILE)


class ExamCountdown:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Exam Countdown")
        root.geometry("760x560")
        root.minsize(620, 440)
        root.configure(bg=BG)
        self.exams = read_exams()
        self.build()
        self.refresh()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Exam Countdown", bg=NAVY, fg="white",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Keep every important exam date in sight.",
                 bg=NAVY, fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)
        form = tk.LabelFrame(body, text="Add an exam", bg=BG, fg=NAVY, padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))
        self.name_var = tk.StringVar()
        self.date_var = tk.StringVar(value=date.today().isoformat())
        tk.Label(form, text="Exam name", bg=BG).grid(row=0, column=0, sticky="w")
        tk.Entry(form, textvariable=self.name_var, width=30).grid(row=1, column=0, padx=(0, 12), sticky="ew")
        tk.Label(form, text="Exam date (YYYY-MM-DD)", bg=BG).grid(row=0, column=1, sticky="w")
        tk.Entry(form, textvariable=self.date_var, width=20).grid(row=1, column=1, padx=(0, 12), sticky="ew")
        ttk.Button(form, text="Add exam", command=self.add).grid(row=1, column=2)
        form.columnconfigure(0, weight=1)
        table_frame = tk.Frame(body, bg=BG)
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=("date", "remaining"), show="headings")
        self.table.heading("date", text="EXAM DATE")
        self.table.heading("remaining", text="COUNTDOWN")
        self.table.column("date", width=150, anchor="center")
        self.table.column("remaining", width=180, anchor="center")
        self.table.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scroll.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scroll.set)
        ttk.Button(body, text="Delete selected exam", command=self.delete).pack(anchor="e", pady=(10, 0))
        tk.Label(self.root, text="Exam dates are saved automatically on this device.",
                 bg=BG, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=24, pady=(0, 12))

    def refresh(self):
        self.table.delete(*self.table.get_children())
        today = date.today()
        self.exams.sort(key=lambda item: item["date"])
        for item in self.exams:
            days = (item["date"] - today).days
            label = "🎯 Exam is today!" if days == 0 else (f"{days} days remaining" if days > 0 else f"Passed {abs(days)} days ago")
            self.table.insert("", "end", iid=item["name"] + item["date"].isoformat(),
                              text=item["name"], values=(item["date"].strftime("%d %b %Y"), label))
        # Store names separately because Treeview's visible columns are date/countdown.
        self.table.heading("#0", text="EXAM")
        self.table.configure(show="tree headings")
        for iid, item in zip(self.table.get_children(), self.exams):
            self.table.item(iid, text=item["name"])

    def add(self):
        name = self.name_var.get().strip()
        try:
            exam_date = date.fromisoformat(self.date_var.get().strip())
        except ValueError:
            messagebox.showwarning("Invalid date", "Enter a valid date in YYYY-MM-DD format.", parent=self.root)
            return
        if not name:
            messagebox.showwarning("Exam name required", "Enter an exam name.", parent=self.root)
            return
        if any(x["name"].casefold() == name.casefold() and x["date"] == exam_date for x in self.exams):
            messagebox.showinfo("Already added", "That exam is already in your list.", parent=self.root)
            return
        self.exams.append({"name": name, "date": exam_date})
        try:
            save_exams(self.exams)
        except OSError as exc:
            self.exams.pop()
            messagebox.showerror("Could not save", str(exc), parent=self.root)
            return
        self.name_var.set("")
        self.refresh()

    def delete(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select an exam", "Choose an exam to delete.", parent=self.root)
            return
        name = self.table.item(selected[0], "text")
        exam_date = date.fromisoformat(self.table.item(selected[0], "values")[0] and
                                       next(x["date"].isoformat() for x in self.exams if x["name"] == name))
        self.exams = [x for x in self.exams if not (x["name"] == name and x["date"] == exam_date)]
        try:
            save_exams(self.exams)
        except OSError as exc:
            messagebox.showerror("Could not save", str(exc), parent=self.root)
        self.refresh()


def main():
    root = tk.Tk()
    ExamCountdown(root)
    root.mainloop()


if __name__ == "__main__":
    main()
