import csv
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from storage import initialize_user_data

PLACEHOLDER = "Full subject syllabus"
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
DATA_DIR = initialize_user_data(app_dir=APP_DIR)
DATA_FILE = DATA_DIR / "dataorsubjects.csv"


def load_subjects():
    subjects = {}
    if not DATA_FILE.exists():
        return subjects
    with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            subject = (row.get("Subject") or "").strip()
            chapter = (row.get("Chapter") or "").strip()
            status = (row.get("Status") or "Pending").strip().title()
            if subject and chapter:
                if status not in {"Pending", "Completed"}:
                    status = "Pending"
                subjects.setdefault(subject, []).append({"chapter": chapter, "status": status})
    return subjects


def save_subjects(subjects):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = DATA_FILE.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Subject", "Chapter", "Status"])
        for subject, chapters in subjects.items():
            for item in chapters:
                writer.writerow([subject, item["chapter"], item["status"]])
    temporary.replace(DATA_FILE)


class SyllabusTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("ExamReadyTimer | Syllabus Tracker")
        self.root.geometry("900x620")
        self.root.minsize(720, 500)
        self.root.configure(bg="#F3F5FB")
        self.subjects = load_subjects()
        self.selected_subject = None
        self._build_ui()
        self.refresh_subjects()

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("TButton", font=("Arial", 10), padding=7)
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), padding=8)

        header = tk.Frame(self.root, bg="#25316D", padx=22, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="Your syllabus, your pace.", bg="#25316D",
                 fg="white", font=("Arial", 21, "bold")).pack(anchor="w")
        tk.Label(header, text="Add chapters, tick them off, and watch your progress grow.",
                 bg="#25316D", fg="#DDE4FF", font=("Arial", 10)).pack(anchor="w", pady=(5, 0))

        body = tk.Frame(self.root, bg="#F3F5FB", padx=18, pady=16)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg="#F3F5FB", width=260)
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)
        tk.Label(left, text="SUBJECTS", bg="#F3F5FB", fg="#25316D",
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Label(left, text="CURRICULUM", bg="#F3F5FB", fg="#68708A",
                 font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 4))
        self.curriculum_var = tk.StringVar(value="All curricula")
        self.curriculum_combo = ttk.Combobox(left, textvariable=self.curriculum_var,
                                             state="readonly", width=25)
        self.curriculum_combo.pack(fill="x", pady=(0, 9))
        self.curriculum_combo.bind("<<ComboboxSelected>>",
                                   lambda _event: self.refresh_subjects(keep=self.selected_subject))
        tk.Label(left, text="FIND SUBJECT", bg="#F3F5FB", fg="#68708A",
                 font=("Arial", 8, "bold")).pack(anchor="w", pady=(0, 4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(left, textvariable=self.search_var)
        search_entry.pack(fill="x", pady=(0, 8))
        self.search_var.trace_add("write", lambda *_args: self.refresh_subjects(keep=self.selected_subject))
        self.subject_list = tk.Listbox(left, font=("Arial", 10), relief="flat",
                                       bg="white", fg="#30364F",
                                       selectbackground="#DDE4FF",
                                       selectforeground="#25316D",
                                       activestyle="none", exportselection=False)
        self.subject_list.pack(fill="both", expand=True)
        self.subject_list.bind("<<ListboxSelect>>", self.on_subject_select)
        ttk.Button(left, text="+ Add subject", command=self.add_subject).pack(fill="x", pady=(10, 4))
        ttk.Button(left, text="Rename subject", command=self.rename_subject).pack(fill="x", pady=4)
        ttk.Button(left, text="Delete subject", command=self.delete_subject).pack(fill="x", pady=4)

        right = tk.Frame(body, bg="#F3F5FB")
        right.pack(side="left", fill="both", expand=True)
        self.subject_heading = tk.Label(right, text="Choose a subject", bg="#F3F5FB",
                                        fg="#25316D", font=("Arial", 16, "bold"))
        self.subject_heading.pack(anchor="w")
        self.progress_label = tk.Label(right, text="Select a subject to view its syllabus.",
                                        bg="#F3F5FB", fg="#68708A", font=("Arial", 10))
        self.progress_label.pack(anchor="w", pady=(4, 8))
        self.progress = ttk.Progressbar(right, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(0, 12))

        columns = ("status", "chapter")
        self.chapter_table = ttk.Treeview(right, columns=columns, show="headings", selectmode="browse")
        self.chapter_table.heading("status", text="STATUS")
        self.chapter_table.heading("chapter", text="CHAPTER / UNIT / TOPIC")
        self.chapter_table.column("status", width=115, anchor="center", stretch=False)
        self.chapter_table.column("chapter", width=430, anchor="w")
        self.chapter_table.pack(fill="both", expand=True)
        self.chapter_table.bind("<Double-1>", lambda _event: self.toggle_status())

        controls = tk.Frame(right, bg="#F3F5FB")
        controls.pack(fill="x", pady=(12, 0))
        ttk.Button(controls, text="+ Add chapter", command=self.add_chapter).pack(side="left", padx=(0, 6))
        ttk.Button(controls, text="Edit", command=self.edit_chapter).pack(side="left", padx=6)
        ttk.Button(controls, text="Delete", command=self.delete_chapter).pack(side="left", padx=6)
        ttk.Button(controls, text="Mark complete / pending", command=self.toggle_status,
                   style="Accent.TButton").pack(side="right")

        tk.Label(self.root, text="Changes are saved automatically on this device.",
                 bg="#F3F5FB", fg="#68708A", font=("Arial", 9)).pack(anchor="w", padx=22, pady=(0, 10))

    def persist(self):
        try:
            save_subjects(self.subjects)
        except OSError as exc:
            messagebox.showerror("Could not save", f"Your changes could not be saved:\n{exc}")
            return False
        return True

    def refresh_subjects(self, keep=None):
        names = list(self.subjects)
        self.subject_list.delete(0, tk.END)
        for name in names:
            self.subject_list.insert(tk.END, name)
        if keep in names:
            index = names.index(keep)
        elif names:
            index = 0
        else:
            index = None
        if index is None:
            self.selected_subject = None
            self.subject_heading.config(text="Choose a subject")
            self.progress_label.config(text="Add a subject to start building your syllabus.")
            self.progress["value"] = 0
            self.chapter_table.delete(*self.chapter_table.get_children())
        else:
            self.subject_list.selection_set(index)
            self.subject_list.activate(index)
            self.show_subject(names[index])

    def on_subject_select(self, _event=None):
        selection = self.subject_list.curselection()
        if selection:
            self.show_subject(self.subject_list.get(selection[0]))

    def show_subject(self, subject):
        self.selected_subject = subject
        self.subject_heading.config(text=subject)
        self.chapter_table.delete(*self.chapter_table.get_children())
        chapters = [item for item in self.subjects.get(subject, [])
                    if item["chapter"].casefold() != PLACEHOLDER.casefold()]
        done = sum(item["status"] == "Completed" for item in chapters)
        total = len(chapters)
        percent = done / total * 100 if total else 0
        self.progress["value"] = percent
        self.progress_label.config(
            text=f"{done} of {total} chapters completed  •  {percent:.0f}%"
            if total else "No chapters entered yet — add your first chapter below."
        )
        if not chapters:
            self.chapter_table.insert("", "end", values=("—", "No chapters yet (add one below)"), tags=("empty",))
        else:
            for item in chapters:
                self.chapter_table.insert("", "end",
                                          values=("✓ Completed" if item["status"] == "Completed" else "○ Pending",
                                                  item["chapter"]))

    def _real_chapters(self):
        if not self.selected_subject:
            messagebox.showinfo("Choose a subject", "Select a subject first.")
            return None
        return [item for item in self.subjects[self.selected_subject]
                if item["chapter"].casefold() != PLACEHOLDER.casefold()]

    def add_subject(self):
        name = simpledialog.askstring("Add subject", "Enter a subject name:", parent=self.root)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Subject required", "Please enter a subject name.")
        elif any(existing.casefold() == name.casefold() for existing in self.subjects):
            messagebox.showwarning("Already exists", "That subject is already in your list.")
        else:
            self.subjects[name] = [{"chapter": PLACEHOLDER, "status": "Pending"}]
            if self.persist():
                self.refresh_subjects(name)

    def rename_subject(self):
        if not self.selected_subject:
            messagebox.showinfo("Choose a subject", "Select a subject to rename.")
            return
        old = self.selected_subject
        name = simpledialog.askstring("Rename subject", "New subject name:",
                                      initialvalue=old, parent=self.root)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Name required", "Subject name cannot be empty.")
        elif name.casefold() != old.casefold() and any(n.casefold() == name.casefold() for n in self.subjects):
            messagebox.showwarning("Already exists", "A subject with that name already exists.")
        else:
            rebuilt = {}
            for key, value in self.subjects.items():
                rebuilt[name if key == old else key] = value
            self.subjects = rebuilt
            if self.persist():
                self.refresh_subjects(name)

    def delete_subject(self):
        if not self.selected_subject:
            messagebox.showinfo("Choose a subject", "Select a subject to delete.")
            return
        subject = self.selected_subject
        if messagebox.askyesno("Delete subject", f"Delete '{subject}' and all its chapters?"):
            del self.subjects[subject]
            if self.persist():
                self.refresh_subjects()

    def add_chapter(self):
        chapters = self._real_chapters()
        if chapters is None:
            return
        name = simpledialog.askstring("Add chapter", "Chapter / unit / topic name:", parent=self.root)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Name required", "Chapter name cannot be empty.")
            return
        if any(item["chapter"].casefold() == name.casefold() for item in chapters):
            messagebox.showwarning("Already exists", "That chapter is already listed.")
            return
        current = self.subjects[self.selected_subject]
        current[:] = [item for item in current if item["chapter"].casefold() != PLACEHOLDER.casefold()]
        current.append({"chapter": name, "status": "Pending"})
        if self.persist():
            self.show_subject(self.selected_subject)

    def _selected_chapter(self):
        chapters = self._real_chapters()
        if chapters is None:
            return None
        selection = self.chapter_table.selection()
        if not selection:
            messagebox.showinfo("Choose a chapter", "Select a chapter from the list first.")
            return None
        values = self.chapter_table.item(selection[0], "values")
        if not values or values[1].startswith("No chapters yet"):
            return None
        return next((item for item in chapters if item["chapter"] == values[1]), None)

    def edit_chapter(self):
        item = self._selected_chapter()
        if item is None:
            return
        name = simpledialog.askstring("Edit chapter", "Chapter / unit / topic name:",
                                      initialvalue=item["chapter"], parent=self.root)
        if name is None:
            return
        name = name.strip()
        chapters = self._real_chapters()
        if not name:
            messagebox.showwarning("Name required", "Chapter name cannot be empty.")
        elif any(other is not item and other["chapter"].casefold() == name.casefold() for other in chapters):
            messagebox.showwarning("Already exists", "That chapter is already listed.")
        else:
            item["chapter"] = name
            if self.persist():
                self.show_subject(self.selected_subject)

    def delete_chapter(self):
        item = self._selected_chapter()
        if item is None:
            return
        if messagebox.askyesno("Delete chapter", f"Delete '{item['chapter']}'?"):
            self.subjects[self.selected_subject].remove(item)
            if not self.subjects[self.selected_subject]:
                self.subjects[self.selected_subject].append({"chapter": PLACEHOLDER, "status": "Pending"})
            if self.persist():
                self.show_subject(self.selected_subject)

    def toggle_status(self):
        item = self._selected_chapter()
        if item is None:
            return
        item["status"] = "Pending" if item["status"] == "Completed" else "Completed"
        if self.persist():
            self.show_subject(self.selected_subject)


def main():
    root = tk.Tk()
    SyllabusTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
