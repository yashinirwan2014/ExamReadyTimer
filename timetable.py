"""Graphical weekly study timetable for ExamReadyTimer."""
import csv
import sys
from pathlib import Path\nimport tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from storage import initialize_user_data

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent\nDATA_DIR = initialize_user_data(app_dir=APP_DIR)
DATA_FILE = DATA_DIR / "datatimetable.csv"
BG, NAVY, MUTED = "#F3F5FB", "#25316D", "#68708A"
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def load_plans():
    plans = []
    if DATA_FILE.exists():
        with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as stream:
            for row in csv.DictReader(stream):
                day, subject = (row.get("Day") or "").strip(), (row.get("Subject") or "").strip()
                if day and subject:
                    plans.append({"day": day, "subject": subject})
    return plans


def save_plans(plans):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp = DATA_FILE.with_suffix(".csv.tmp")
    with temp.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["Day", "Subject"])
        writer.writerows((item["day"], item["subject"]) for item in plans)
    temp.replace(DATA_FILE)


class StudyTimetable:
    def __init__(self, root):
        self.root = root
        root.title("ExamReadyTimer | Study Timetable")
        root.geometry("720x560")
        root.minsize(580, 440)
        root.configure(bg=BG)
        self.plans = load_plans()
        self.build()
        self.refresh()

    def build(self):
        header = tk.Frame(self.root, bg=NAVY, padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(header, text="Study Timetable", bg=NAVY, fg="white",
                 font=("Arial", 22, "bold")).pack(anchor="w")
        tk.Label(header, text="Give every subject a place in your week.",
                 bg=NAVY, fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(4, 0))
        body = tk.Frame(self.root, bg=BG, padx=22, pady=18)
        body.pack(fill="both", expand=True)
        form = tk.LabelFrame(body, text="Add a study plan", bg=BG, fg=NAVY, padx=12, pady=10)
        form.pack(fill="x", pady=(0, 14))
        self.day_var = tk.StringVar(value=DAYS[0])
        self.subject_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.day_var, values=DAYS, state="readonly", width=16).grid(row=0, column=0, padx=(0, 10))
        tk.Entry(form, textvariable=self.subject_var).grid(row=0, column=1, sticky="ew", padx=(0, 10))
        ttk.Button(form, text="Add plan", command=self.add).grid(row=0, column=2)
        form.columnconfigure(1, weight=1)
        self.table = ttk.Treeview(body, columns=("day", "subject"), show="headings", selectmode="browse")
        self.table.heading("day", text="DAY")
        self.table.heading("subject", text="SUBJECT / CHAPTER / TASK")
        self.table.column("day", width=140, anchor="center")
        self.table.column("subject", width=420)
        self.table.pack(fill="both", expand=True)
        controls = tk.Frame(body, bg=BG)
        controls.pack(fill="x", pady=(12, 0))
        ttk.Button(controls, text="Edit selected", command=self.edit).pack(side="left")
        ttk.Button(controls, text="Delete selected", command=self.delete).pack(side="left", padx=8)
        tk.Label(self.root, text="Your weekly plan is saved automatically.",
                 bg=BG, fg=MUTED, font=("Arial", 9)).pack(anchor="w", padx=24, pady=(0, 12))

    def refresh(self):
        self.table.delete(*self.table.get_children())
        order = {day: index for index, day in enumerate(DAYS)}
        self.plans.sort(key=lambda item: order.get(item["day"], 99))
        for index, item in enumerate(self.plans):
            self.table.insert("", "end", iid=str(index), values=(item["day"], item["subject"]))

    def persist(self):
        try:
            save_plans(self.plans)
        except OSError as exc:
            messagebox.showerror("Could not save", str(exc), parent=self.root)
            return False
        return True

    def add(self):
        subject = self.subject_var.get().strip()
        if not subject:
            messagebox.showwarning("Task required", "Enter a subject, chapter or study task.", parent=self.root)
            return
        self.plans.append({"day": self.day_var.get(), "subject": subject})
        if self.persist():
            self.subject_var.set("")
            self.refresh()

    def selected_index(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Select a plan", "Choose a timetable entry first.", parent=self.root)
            return None
        return int(selection[0])

    def edit(self):
        index = self.selected_index()
        if index is None:
            return
        item = self.plans[index]
        subject = simpledialog.askstring("Edit study plan", "Subject / chapter / task:",
                                         initialvalue=item["subject"], parent=self.root)
        if subject is None:
            return
        subject = subject.strip()
        if not subject:
            messagebox.showwarning("Task required", "The study task cannot be empty.", parent=self.root)
            return
        item["subject"] = subject
        if self.persist():
            self.refresh()

    def delete(self):
        index = self.selected_index()
        if index is None:
            return
        if messagebox.askyesno("Delete plan", "Remove this timetable entry?", parent=self.root):
            removed = self.plans.pop(index)
            if not self.persist():
                self.plans.insert(index, removed)
            self.refresh()


def main():
    root = tk.Tk()
    StudyTimetable(root)
    root.mainloop()


if __name__ == "__main__":
    main()
