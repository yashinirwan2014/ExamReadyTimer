import csv
from pathlib import Path

DATA_FILE = Path(__file__).resolve().with_name("dataorsubjects.csv")
PLACEHOLDER = "Full subject syllabus"


def load_subjects():
    """Load subjects and their editable chapter rows from the CSV file."""
    subjects = {}
    if not DATA_FILE.exists():
        return subjects

    with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        for row in reader:
            subject = (row.get("Subject") or "").strip()
            chapter = (row.get("Chapter") or "").strip()
            status = (row.get("Status") or "Pending").strip().title()
            if not subject or not chapter:
                continue
            if status not in {"Pending", "Completed"}:
                status = "Pending"
            subjects.setdefault(subject, []).append({
                "chapter": chapter,
                "status": status
            })
    return subjects


def save_subjects(subjects):
    """Save all subjects without changing the existing three-column CSV format."""
    with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Subject", "Chapter", "Status"])
        for subject, chapters in subjects.items():
            for item in chapters:
                writer.writerow([subject, item["chapter"], item["status"]])


def choose_subject(subjects):
    names = list(subjects)
    if not names:
        print("\nNo subjects found. Add a subject first.")
        return None
    print("\nAVAILABLE SUBJECTS")
    for index, name in enumerate(names, start=1):
        print(f"{index}. {name}")
    try:
        choice = int(input("\nSelect subject number: ").strip())
        if 1 <= choice <= len(names):
            return names[choice - 1]
    except ValueError:
        pass
    print("Please enter a valid subject number.")
    return None


def add_subject(subjects):
    name = input("\nEnter the subject name: ").strip()
    if not name:
        print("Subject name cannot be empty.")
    elif name in subjects:
        print("That subject already exists.")
    else:
        subjects[name] = []
        save_subjects(subjects)
        print(f"Added '{name}'. Now add its chapters/topics.")


def add_chapter(subjects):
    subject = choose_subject(subjects)
    if subject is None:
        return
    chapter = input("Enter chapter / unit / topic name: ").strip()
    if not chapter:
        print("Chapter name cannot be empty.")
        return

    # Replace the generic syllabus placeholder the first time a real chapter is added.
    subjects[subject] = [
        item for item in subjects[subject]
        if item["chapter"].casefold() != PLACEHOLDER.casefold()
    ]
    if any(item["chapter"].casefold() == chapter.casefold()
           for item in subjects[subject]):
        print("That chapter/topic is already listed for this subject.")
        return
    subjects[subject].append({"chapter": chapter, "status": "Pending"})
    save_subjects(subjects)
    print("Chapter/topic added and saved!")


def view_progress(subjects):
    if not subjects:
        print("\nNo subjects yet. Use 'Add a subject' to get started.")
        return
    print("\nSYLLABUS PROGRESS")
    print("=" * 54)
    overall_done = overall_total = 0
    for subject, chapters in subjects.items():
        real_items = [item for item in chapters
                      if item["chapter"].casefold() != PLACEHOLDER.casefold()]
        if not real_items:
            print(f"\n{subject}\n  No chapters entered yet — use 'Add chapter/topic'.")
            continue
        completed = sum(item["status"] == "Completed" for item in real_items)
        total = len(real_items)
        overall_done += completed
        overall_total += total
        percent = completed / total * 100
        print(f"\n{subject} — {completed}/{total} completed ({percent:.1f}%)")
        for item in real_items:
            mark = "[✓]" if item["status"] == "Completed" else "[ ]"
            print(f"  {mark} {item['chapter']}")
    if overall_total:
        print("\n" + "-" * 54)
        print(f"OVERALL: {overall_done}/{overall_total} chapters/topics "
              f"({overall_done / overall_total * 100:.1f}%)")


def update_chapter(subjects, action):
    subject = choose_subject(subjects)
    if subject is None:
        return
    chapters = [item for item in subjects[subject]
                if item["chapter"].casefold() != PLACEHOLDER.casefold()]
    if not chapters:
        print("No chapters entered for this subject yet. Add one first.")
        return
    print(f"\nCHAPTERS IN {subject}")
    for index, item in enumerate(chapters, start=1):
        print(f"{index}. [{item['status']}] {item['chapter']}")
    try:
        choice = int(input("\nSelect chapter number: ").strip())
        if not 1 <= choice <= len(chapters):
            raise ValueError
    except ValueError:
        print("Please enter a valid chapter number.")
        return

    item = chapters[choice - 1]
    if action == "status":
        item["status"] = "Pending" if item["status"] == "Completed" else "Completed"
        print(f"Marked '{item['chapter']}' as {item['status']}.")
    elif action == "edit":
        revised = input("Enter the revised chapter/topic name: ").strip()
        if not revised:
            print("Name cannot be empty.")
            return
        if any(other is not item and other["chapter"].casefold() == revised.casefold()
               for other in chapters):
            print("That chapter/topic already exists.")
            return
        item["chapter"] = revised
        print("Chapter/topic renamed.")
    elif action == "delete":
        confirm = input(f"Delete '{item['chapter']}'? Type yes to confirm: ").strip().lower()
        if confirm == "yes":
            subjects[subject].remove(item)
            print("Chapter/topic deleted.")
        else:
            print("Deletion cancelled.")
    save_subjects(subjects)
    print("Changes saved to dataorsubjects.csv.")


def main():
    print("=" * 38)
    print("       EXAMREADY SYLLABUS TRACKER")
    print("=" * 38)
    while True:
        subjects = load_subjects()
        print("\nTRACKER MENU")
        print("-" * 38)
        print("1. View syllabus and progress")
        print("2. Add a subject")
        print("3. Add chapter / unit / topic")
        print("4. Mark chapter completed / pending")
        print("5. Edit chapter / topic name")
        print("6. Delete chapter / topic")
        print("7. Exit")
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            view_progress(subjects)
        elif choice == "2":
            add_subject(subjects)
        elif choice == "3":
            add_chapter(subjects)
        elif choice == "4":
            update_chapter(subjects, "status")
        elif choice == "5":
            update_chapter(subjects, "edit")
        elif choice == "6":
            update_chapter(subjects, "delete")
        elif choice == "7":
            print("\nYour syllabus progress is saved. Happy studying!")
            break
        else:
            print("Invalid choice. Please select 1–7.")


if __name__ == "__main__":
    main()
