from datetime import date

print("================================")
print("        EXAMREADY")
print("      EXAM COUNTDOWN")
print("================================")

while True:

    print("\nCOUNTDOWN MENU")
    print("----------------------------")
    print("1. Add exam")
    print("2. View exam countdowns")
    print("3. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":

        exam_name = input("\nEnter exam name: ")
        year = int(input("Enter exam year: "))
        month = int(input("Enter exam month: "))
        day = int(input("Enter exam day: "))

        file = open("dataexams.csv", "a")

        file.write(
            exam_name + "," +
            str(year) + "," +
            str(month) + "," +
            str(day) + "\n"
        )

        file.close()

        print("\nExam saved successfully! ✓")

    elif choice == "2":

        file = open("dataexams.csv", "r")

        header = file.readline()

        found = False

        print("\nYOUR EXAMS")
        print("----------------------------")

        for line in file:

            data = line.strip().split(",")

            exam_name = data[0]
            year = int(data[1])
            month = int(data[2])
            day = int(data[3])

            today = date.today()
            exam_date = date(year, month, day)

            remaining = exam_date - today

            print("\nExam:", exam_name)

            if remaining.days > 0:
                print("Days remaining:", remaining.days)

            elif remaining.days == 0:
                print("🎯 EXAM IS TODAY!")

            else:
                print("Exam date has passed.")

            found = True

        file.close()

        if found == False:
            print("No exams added yet.")

    elif choice == "3":

        print("\nReturning to ExamReadyTimer...")
        break

    else:

        print("\nInvalid choice. Please try again.")
