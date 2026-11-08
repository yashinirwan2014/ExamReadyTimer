"""Weekly time-blocking timetable for ExamReadyTimer."""
import csv
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from storage import initialize_user_data
from theme import apply_dark_theme
from schedule_utils import duration_minutes, times_overlap

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
DATA_FILE = DATA_DIR / "datatimetable.csv"
BG, NAVY, MUTED = "#0B1020", "#172544", "#FFFFFF"
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
TASK_TYPES = ("Deep Work", "Revision", "Practice", "Reading", "Break", "Other")
PRIORITIES = ("High", "Medium", "Low")
STATUSES = ("Planned", "Completed")
FIELDS = ("Day", "StartTime", "EndTime", "Subject", "TaskType", "Priority", "Status", "Notes")


def load_plans():
    plans = []
    if DATA_FILE.exists():
        with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
            for row in csv.DictReader(stream):
                day = (row.get("Day") or "").strip()
                subject = (row.get("Subject") or "").strip()
                if day and subject:
                    plans.append({
                        "day": day, "start": (row.get("StartTime") or "09:00").strip(),
                        "end": (row.get("EndTime") or "10:00").strip(), "subject": subject,
                        "task_type": (row.get("TaskType") or "Study").strip() or "Study",
                        "priority": (row.get("Priority") or "Medium").strip() or "Medium",
                        "status": (row.get("Status") or "Planned").strip() or "Planned",
                        "notes": (row.get("Notes") or "").strip(),
                    })
    return plans


def save_plans(plans):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".csv.tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for item in plans:
            writer.writerow({
                "Day": item["day"], "StartTime": item["start"], "EndTime": item["end"],
                "Subject": item["subject"], "TaskType": item["task_type"],
                "Priority": item["priority"], "Status": item["status"], "Notes": item.get("notes", ""),
            })
    temp.replace(DATA_FILE)


class StudyTimetable:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Smart Study Timetable")
        root.geometry("980x680")
        root.minsize(780, 560)
        apply_dark_theme(root)
        self.plans = load_plans()
        self.editing_index = None
        self.build()
        self.refresh()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="Smart Study Timetable", bg=NAVY, fg="#E8EEFF",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Time-block your week, catch clashes and track completed sessions.",
                 bg=NAVY, fg="#FFFFFF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=22, pady=16)
        body.pack(fill="both", expand=True)
        form = tk.LabelFrame(body, text="Build a study block", bg=BG, fg="#E8EEFF", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 12))
        self.day_var = tk.StringVar(value=DAYS[0])
        self.start_var = tk.StringVar(value="09:00")
        self.end_var = tk.StringVar(value="10:00")
        self.subject_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Deep Work")
        self.priority_var = tk.StringVar(value="Medium")
        self.notes_var = tk.StringVar()
        labels = (("Day", 0), ("Start (24h)", 1), ("End (24h)", 2), ("Subject / task", 3),
                  ("Session type", 4), ("Priority", 5))
        for label, col in labels:
            tk.Label(form, text=label, bg=BG).grid(row=0, column=col, sticky="w", padx=(0, 7))
        ttk.Combobox(form, textvariable=self.day_var, values=DAYS, state="readonly", width=12).grid(row=1, column=0, sticky="ew", padx=(0, 7))
        tk.Entry(form, textvariable=self.start_var, width=9).grid(row=1, column=1, sticky="ew", padx=(0, 7))
        tk.Entry(form, textvariable=self.end_var, width=9).grid(row=1, column=2, sticky="ew", padx=(0, 7))
        tk.Entry(form, textvariable=self.subject_var, width=24).grid(row=1, column=3, sticky="ew", padx=(0, 7))
        ttk.Combobox(form, textvariable=self.type_var, values=TASK_TYPES, state="readonly", width=14).grid(row=1, column=4, sticky="ew", padx=(0, 7))
        ttk.Combobox(form, textvariable=self.priority_var, values=PRIORITIES, state="readonly", width=10).grid(row=1, column=5, sticky="ew")
        tk.Label(form, text="Notes / chapter target", bg=BG).grid(row=2, column=0, sticky="w", pady=(9, 0))
        tk.Entry(form, textvariable=self.notes_var).grid(row=3, column=0, columnspan=5, sticky="ew", padx=(0, 9))
        self.save_button = ttk.Button(form, text="Add block", command=self.save_form)
        self.save_button.grid(row=3, column=5, sticky="ew")
        for col in range(6):
            form.columnconfigure(col, weight=1)
        self.table = ttk.Treeview(body, columns=("day", "time", "task", "type", "priority", "duration", "status"),
                                  show="headings", selectmode="browse")
        headings = (("day", "DAY"), ("time", "TIME BLOCK"), ("task", "SUBJECT / TASK"),
                    ("type", "SESSION"), ("priority", "PRIORITY"), ("duration", "LENGTH"), ("status", "STATUS"))
        for key, label in headings:
            self.table.heading(key, text=label)
        for key, width in (("day", 95), ("time", 125), ("task", 220), ("type", 115),
                           ("priority", 80), ("duration", 75), ("status", 95)):
            self.table.column(key, width=width, anchor="center" if key != "task" else "w")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_select)
        controls = tk.Frame(body, bg=BG)
        controls.pack(fill="x", pady=(10, 0))
        ttk.Button(controls, text="Mark complete / planned", command=self.toggle_status).pack(side="left")
        ttk.Button(controls, text="Clear form", command=self.clear_form).pack(side="left", padx=8)
        ttk.Button(controls, text="Delete selected", command=self.delete).pack(side="right")
        self.summary = tk.Label(controls, text="", bg=BG, fg="#E8EEFF", font=("Arial", 10, "bold"))
        self.summary.pack(side="right", padx=12)
        tk.Label(self.root, text="Tip: overlapping blocks are flagged before saving. Duration and weekly totals are calculated automatically.",
                 bg=BG, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=24, pady=(0, 10))

    def refresh(self):
        self.table.delete(*self.table.get_children())
        order = {day: index for index, day in enumerate(DAYS)}
        self.plans.sort(key=lambda item: (order.get(item["day"], 99), item["start"]))
        total_minutes = completed_minutes = 0
        for index, item in enumerate(self.plans):
            try:
                minutes = duration_minutes(item["start"], item["end"])
            except ValueError:
                minutes = 0
            total_minutes += minutes
            if item["status"] == "Completed":
                completed_minutes += minutes
            self.table.insert("", "end", iid=str(index), values=(
                item["day"], f'{item["start"]}–{item["end"]}', item["subject"],
                item["task_type"], item["priority"], f"{minutes} min", item["status"]))
        self.summary.config(text=f"{total_minutes // 60}h {total_minutes % 60:02d}m planned • {completed_minutes // 60}h {completed_minutes % 60:02d}m done")

    def persist(self):
        try:
            save_plans(self.plans)
        except OSError as exc:
            messagebox.showerror("Could not save", str(exc), parent=self.root)
            return False
        return True

    def selected_index(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Select a block", "Choose a timetable block first.", parent=self.root)
            return None
        return int(selection[0])

    def on_select(self, _event=None):
        selection = self.table.selection()
        if not selection:
            return
        index = int(selection[0])
        item = self.plans[index]
        self.editing_index = index
        self.day_var.set(item["day"])
        self.start_var.set(item["start"])
        self.end_var.set(item["end"])
        self.subject_var.set(item["subject"])
        self.type_var.set(item["task_type"] if item["task_type"] in TASK_TYPES else "Other")
        self.priority_var.set(item["priority"] if item["priority"] in PRIORITIES else "Medium")
        self.notes_var.set(item["notes"])
        self.save_button.config(text="Update block")

    def clear_form(self):
        self.editing_index = None
        self.day_var.set(DAYS[0])
        self.start_var.set("09:00")
        self.end_var.set("10:00")
        self.subject_var.set("")
        self.type_var.set("Deep Work")
        self.priority_var.set("Medium")
        self.notes_var.set("")
        self.save_button.config(text="Add block")
        self.table.selection_remove(self.table.selection())

    def save_form(self):
        subject = self.subject_var.get().strip()
        if not subject:
            messagebox.showwarning("Task required", "Enter a subject, chapter or study task.", parent=self.root)
            return
        start, end = self.start_var.get().strip(), self.end_var.get().strip()
        try:
            duration_minutes(start, end)
        except ValueError:
            messagebox.showwarning("Invalid time block", "Use 24-hour HH:MM times and make sure the end is later than the start.", parent=self.root)
            return
        candidate = {
            "day": self.day_var.get(), "start": start, "end": end, "subject": subject,
            "task_type": self.type_var.get(), "priority": self.priority_var.get(),
            "status": "Planned", "notes": self.notes_var.get().strip(),
        }
        conflicts = []
        for index, existing in enumerate(self.plans):
            if index == self.editing_index or existing["day"] != candidate["day"]:
                continue
            try:
                overlap = times_overlap(start, end, existing["start"], existing["end"])
            except ValueError:
                overlap = False
            if overlap:
                conflicts.append(f'{existing["start"]}–{existing["end"]} {existing["subject"]}')
        if conflicts and not messagebox.askyesno(
            "Time conflict detected",
            "This block overlaps with:\n" + "\n".join(conflicts) + "\n\nSave it anyway?",
            parent=self.root
        ):
            return
        if self.editing_index is None:
            self.plans.append(candidate)
            changed_index = len(self.plans) - 1
        else:
            changed_index = self.editing_index
            old = self.plans[changed_index]
            candidate["status"] = old["status"]
            self.plans[changed_index] = candidate
        if self.persist():
            self.clear_form()
            self.refresh()
        else:
            if self.editing_index is None:
                self.plans.pop()
            else:
                self.plans[changed_index] = old

    def toggle_status(self):
        index = self.selected_index()
        if index is None:
            return
        item = self.plans[index]
        item["status"] = "Completed" if item["status"] != "Completed" else "Planned"
        if self.persist():
            self.refresh()
        else:
            item["status"] = "Planned" if item["status"] == "Completed" else "Completed"

    def delete(self):
        index = self.selected_index()
        if index is None:
            return
        removed = self.plans.pop(index)
        if not self.persist():
            self.plans.insert(index, removed)
        self.clear_form()
        self.refresh()


def main():
    root = tk.Tk()
    StudyTimetable(root)
    root.mainloop()


if __name__ == "__main__":
    main()
