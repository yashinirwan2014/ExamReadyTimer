print("================================")
print("       EXAMREADY TRACKER")
print("================================")

while True:

    file = open("dataorsubjects.csv", "r")
    header = file.readline()

    subjects = {}

    for line in file:
        data = line.strip().split(",")

        subject = data[0]
        chapter = data[1]
        status = data[2]

        if subject not in subjects:
            subjects[subject] = []

        subjects[subject].append([chapter, status])

    file.close()

    print("\nTRACKER MENU")
    print("----------------------------")
    print("1. View Progress")
    print("2. Mark Chapter Completed")
    print("3. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":

        for subject in subjects:

            print("\n" + subject)
            print("----------------------------")

            completed = 0
            total = len(subjects[subject])

            for chapter in subjects[subject]:

                name = chapter[0]
                status = chapter[1]

                if status == "Completed":
                    print("[✓]", name)
                    completed = completed + 1
                else:
                    print("[ ]", name)

            percentage = (completed / total) * 100

            print("Progress:", round(percentage, 1), "%")

    elif choice == "2":

        print("\nSubjects:")
        print("1. Physics")
        print("2. Chemistry")
        print("3. Mathematics")

        subject_choice = input("Select subject: ")

        if subject_choice == "1":
            subject = "Physics"

        elif subject_choice == "2":
            subject = "Chemistry"

        elif subject_choice == "3":
            subject = "Mathematics"

        else:
            print("Invalid subject.")
            continue

        print("\nChapters:")

        for i in range(len(subjects[subject])):
            print(i + 1, ".", subjects[subject][i][0])

        chapter_choice = int(input("\nEnter chapter number: "))

        if 1 <= chapter_choice <= len(subjects[subject]):

            subjects[subject][chapter_choice - 1][1] = "Completed"

            file = open("dataorsubjects.csv", "w")

            file.write(header)

            for sub in subjects:

                for chapter in subjects[sub]:

                    file.write(
                        sub + "," +
                        chapter[0] + "," +
                        chapter[1] + "\n"
                    )

            file.close()

            print("\nChapter marked as completed! ✓")

        else:
            print("Invalid chapter number.")

    elif choice == "3":

        print("\nReturning to ExamReady...")
        break

    else:

        print("\nInvalid choice. Please try again.")
