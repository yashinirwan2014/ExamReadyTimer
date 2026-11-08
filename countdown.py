"""Graphical exam planner and countdown for ExamReadyTimer."""
import csv
from datetime import date
from reminders import due_reminders, load_sent_reminders, reminder_key, save_sent_reminders
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from storage import initialize_user_data

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
DATA_FILE = DATA_DIR / "dataexams.csv"
BG, NAVY, MUTED = "#F3F5FB", "#25316D", "#68708A"
EXAM_TYPES = ("Board", "School", "Entrance", "Mock", "Practical", "Other")
PRIORITIES = ("High", "Medium", "Low")
FIELDS = ("Exam", "Year", "Month", "Day", "Subject", "ExamType", "Priority", "ReminderDays", "Notes")


def read_exams():
    exams = []
    if DATA_FILE.exists():
        with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
            for row in csv.DictReader(stream):
                try:
                    name = (row.get("Exam") or "").strip()
                    exam_date = date(int(row["Year"]), int(row["Month"]), int(row["Day"]))
                    if name:
                        exams.append({
                            "name": name, "date": exam_date,
                            "subject": (row.get("Subject") or "").strip(),
                            "exam_type": (row.get("ExamType") or "Other").strip() or "Other",
                            "priority": (row.get("Priority") or "Medium").strip() or "Medium",
                            "reminder_days": int(row.get("ReminderDays") or 7),
                            "notes": (row.get("Notes") or "").strip(),
                        })
                except (KeyError, TypeError, ValueError):
                    continue
    return exams


def save_exams(exams):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".csv.tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for item in exams:
            d = item["date"]
            writer.writerow({
                "Exam": item["name"], "Year": d.year, "Month": d.month, "Day": d.day,
                "Subject": item.get("subject", ""), "ExamType": item.get("exam_type", "Other"),
                "Priority": item.get("priority", "Medium"),
                "ReminderDays": item.get("reminder_days", 7), "Notes": item.get("notes", ""),
            })
    temp.replace(DATA_FILE)


class ExamCountdown:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Exam Planner")
        root.geometry("940x680")
        root.minsize(760, 560)
        root.configure(bg=BG)
        self.exams = read_exams()
        self.build()
        self.refresh()
        self.reminder_state_file = DATA_DIR / ".reminders-sent.json"
        self.sent_reminders = load_sent_reminders(self.reminder_state_file)
        self.check_reminders()
        self.reminder_after_id = self.root.after(60_000, self.check_reminders)

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="Exam Planner & Countdown", bg=NAVY, fg="white",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Keep every paper, practical and mock exam on your radar.",
                 bg=NAVY, fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=22, pady=16)
        body.pack(fill="both", expand=True)
        form = tk.LabelFrame(body, text="Add an exam", bg=BG, fg=NAVY, padx=12, pady=10)
        form.pack(fill="x", pady=(0, 12))
        self.name_var = tk.StringVar()
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.subject_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Board")
        self.priority_var = tk.StringVar(value="High")
        self.reminder_var = tk.StringVar(value="7")
        self.notes_var = tk.StringVar()
        tk.Label(form, text="Exam name", bg=BG).grid(row=0, column=0, sticky="w")
        tk.Entry(form, textvariable=self.name_var, width=24).grid(row=1, column=0, padx=(0, 9), sticky="ew")
        tk.Label(form, text="Date (YYYY-MM-DD)", bg=BG).grid(row=0, column=1, sticky="w")
        tk.Entry(form, textvariable=self.date_var, width=17).grid(row=1, column=1, padx=(0, 9), sticky="ew")
        tk.Label(form, text="Subject", bg=BG).grid(row=0, column=2, sticky="w")
        tk.Entry(form, textvariable=self.subject_var, width=18).grid(row=1, column=2, padx=(0, 9), sticky="ew")
        tk.Label(form, text="Exam type", bg=BG).grid(row=2, column=0, sticky="w", pady=(9, 0))
        ttk.Combobox(form, textvariable=self.type_var, values=EXAM_TYPES, state="readonly", width=20).grid(row=3, column=0, sticky="ew", padx=(0, 9))
        tk.Label(form, text="Priority", bg=BG).grid(row=2, column=1, sticky="w", pady=(9, 0))
        ttk.Combobox(form, textvariable=self.priority_var, values=PRIORITIES, state="readonly", width=14).grid(row=3, column=1, sticky="ew", padx=(0, 9))
        tk.Label(form, text="Reminder lead (days)", bg=BG).grid(row=2, column=2, sticky="w", pady=(9, 0))
        tk.Entry(form, textvariable=self.reminder_var, width=8).grid(row=3, column=2, sticky="ew", padx=(0, 9))
        tk.Label(form, text="Notes / preparation focus", bg=BG).grid(row=0, column=3, sticky="w")
        tk.Entry(form, textvariable=self.notes_var, width=24).grid(row=1, column=3, rowspan=3, sticky="ew")
        ttk.Button(form, text="Add exam", command=self.add).grid(row=1, column=4, rowspan=3, padx=(5, 0))
        for col in range(4):
            form.columnconfigure(col, weight=1)
        table_frame = tk.Frame(body, bg=BG)
        table_frame.pack(fill="both", expand=True)
        columns = ("date", "subject", "kind", "priority", "countdown", "reminder")
        self.table = ttk.Treeview(table_frame, columns=columns, show="tree headings", selectmode="browse")
        self.table.heading("#0", text="EXAM")
        for key, label in (("date", "DATE"), ("subject", "SUBJECT"), ("kind", "TYPE"),
                           ("priority", "PRIORITY"), ("countdown", "COUNTDOWN"), ("reminder", "REMINDER")):
            self.table.heading(key, text=label)
        self.table.column("#0", width=160)
        self.table.column("date", width=100, anchor="center")
        self.table.column("subject", width=110)
        self.table.column("kind", width=90, anchor="center")
        self.table.column("priority", width=75, anchor="center")
        self.table.column("countdown", width=130, anchor="center")
        self.table.column("reminder", width=115, anchor="center")
        self.table.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scroll.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scroll.set)
        controls = tk.Frame(body, bg=BG)
        controls.pack(fill="x", pady=(10, 0))
        ttk.Button(controls, text="Delete selected exam", command=self.delete).pack(side="right")
        self.summary = tk.Label(controls, text="", bg=BG, fg=NAVY, font=("Arial", 10, "bold"))
        self.summary.pack(side="left")
        tk.Label(self.root, text="Reminders appear once when their window begins. Keep the Exam Planner open to receive them.",
                 bg=BG, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=24, pady=(0, 10))

    def refresh(self):
        self.table.delete(*self.table.get_children())
        today = date.today()
        self.exams.sort(key=lambda item: item["date"])
        for index, item in enumerate(self.exams):
            days = (item["date"] - today).days
            countdown = "Exam today!" if days == 0 else (f"{days} days left" if days > 0 else f"Passed {abs(days)} days ago")
            reminder_date = item["date"].fromordinal(item["date"].toordinal() - item["reminder_days"])
            reminder = "Reminder window" if reminder_date <= today <= item["date"] else f"From {reminder_date:%d %b}"
            self.table.insert("", "end", iid=str(index), text=item["name"],
                              values=(item["date"].strftime("%d %b %Y"), item["subject"] or "—",
                                      item["exam_type"], item["priority"], countdown, reminder))
        upcoming = sum(item["date"] >= today for item in self.exams)
        self.summary.config(text=f"{upcoming} upcoming • {len(self.exams) - upcoming} past • {len(self.exams)} total")

    def check_reminders(self):
        """Show each exam reminder once while the planner is running."""
        due = due_reminders(self.exams, date.today(), self.sent_reminders)
        if due:
            # Persist before showing the dialog so closing it cannot repeat alerts.
            self.sent_reminders.update(reminder_key(item) for item in due)
            try:
                save_sent_reminders(self.reminder_state_file, self.sent_reminders)
            except OSError as exc:
                messagebox.showwarning("Reminder could not be saved",
                                       f"The reminder will be shown again next time.\n{exc}",
                                       parent=self.root)
                self.sent_reminders.difference_update(reminder_key(item) for item in due)
            lines = []
            for item in due:
                days = (item["date"] - date.today()).days
                when = "today" if days == 0 else f"in {days} day(s)"
                subject = f" — {item['subject']}" if item.get("subject") else ""
                lines.append(f"• {item['name']}{subject}: {when}")
            self.root.bell()
            messagebox.showinfo("Exam reminders", "Your exam reminder window has started:\n\n" +
                                "\n".join(lines), parent=self.root)
        self.reminder_after_id = self.root.after(60_000, self.check_reminders)

    def add(self):
        name = self.name_var.get().strip()
        try:
            exam_date = date.fromisoformat(self.date_var.get().strip())
            reminder_days = int(self.reminder_var.get().strip())
            if not 0 <= reminder_days <= 365:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Check the date or reminder", "Use YYYY-MM-DD and a reminder lead from 0 to 365 days.", parent=self.root)
            return
        if not name:
            messagebox.showwarning("Exam name required", "Enter an exam name.", parent=self.root)
            return
        if any(x["name"].casefold() == name.casefold() and x["date"] == exam_date for x in self.exams):
            messagebox.showinfo("Already added", "That exam is already in your list.", parent=self.root)
            return
        self.exams.append({
            "name": name, "date": exam_date, "subject": self.subject_var.get().strip(),
            "exam_type": self.type_var.get(), "priority": self.priority_var.get(),
            "reminder_days": reminder_days, "notes": self.notes_var.get().strip(),
        })
        try:
            save_exams(self.exams)
        except OSError as exc:
            self.exams.pop()
            messagebox.showerror("Could not save", str(exc), parent=self.root)
            return
        for variable in (self.name_var, self.subject_var, self.notes_var):
            variable.set("")
        self.refresh()

    def delete(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select an exam", "Choose an exam to delete.", parent=self.root)
            return
        index = int(selected[0])
        removed = self.exams.pop(index)
        try:
            save_exams(self.exams)
        except OSError as exc:
            self.exams.insert(index, removed)
            messagebox.showerror("Could not save", str(exc), parent=self.root)
        self.refresh()


def main():
    root = tk.Tk()
    ExamCountdown(root)
    root.mainloop()


if __name__ == "__main__":
    main()
