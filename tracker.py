import csv

DATA_FILE = "dataorsubjects.csv"


def load_subjects():
    subjects = {}
    with open(DATA_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            subject = row["Subject"]
            subjects.setdefault(subject, []).append({
                "chapter": row["Chapter"],
                "status": row["Status"]
            })
    return subjects


def save_subjects(subjects):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Subject", "Chapter", "Status"])
        for subject, chapters in subjects.items():
            for item in chapters:
                writer.writerow([subject, item["chapter"], item["status"]])


print("================================")
print("       EXAMREADY TRACKER")
print("================================")

while True:
    subjects = load_subjects()
    subject_names = list(subjects.keys())

    print("\nTRACKER MENU")
    print("----------------------------")
    print("1. View Progress")
    print("2. Mark Chapter / Subject Completed")
    print("3. Exit")

    choice = input("\nEnter your choice: ").strip()

    if choice == "1":
        for subject, chapters in subjects.items():
            completed = sum(item["status"] == "Completed" for item in chapters)
            total = len(chapters)
            percentage = (completed / total * 100) if total else 0

            print("\n" + subject)
            print("----------------------------")
            for item in chapters:
                mark = "[✓]" if item["status"] == "Completed" else "[ ]"
                print(mark, item["chapter"])
            print("Progress:", round(percentage, 1), "%")

    elif choice == "2":
        print("\nAvailable subjects:")
        for index, subject in enumerate(subject_names, start=1):
            print(f"{index}. {subject}")

        try:
            subject_choice = int(input("\nSelect subject number: "))
            if not 1 <= subject_choice <= len(subject_names):
                print("Invalid subject number.")
                continue
        except ValueError:
            print("Please enter a valid number.")
            continue

        subject = subject_names[subject_choice - 1]
        chapters = subjects[subject]

        print("\nTopics / syllabus items:")
        for index, item in enumerate(chapters, start=1):
            print(f"{index}. {item['chapter']} [{item['status']}]")

        try:
            chapter_choice = int(input("\nEnter item number to mark completed: "))
            if not 1 <= chapter_choice <= len(chapters):
                print("Invalid item number.")
                continue
        except ValueError:
            print("Please enter a valid number.")
            continue

        chapters[chapter_choice - 1]["status"] = "Completed"
        save_subjects(subjects)
        print("\nProgress saved! ✓")

    elif choice == "3":
        print("\nReturning to ExamReady...")
        break

    else:
        print("\nInvalid choice. Please try again.")
