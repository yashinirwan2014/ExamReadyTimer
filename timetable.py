print("================================")
print("       EXAMREADY TIMETABLE")
print("================================")

while True:

    print("\nTIMETABLE MENU")
    print("----------------------------")
    print("1. Add study plan")
    print("2. View study plan")
    print("3. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":

        day = input("\nEnter the day: ").capitalize()
        subject = input("Enter the subject/chapter: ")

        file = open("datatimetable.csv", "a")

        file.write(day + "," + subject + "\n")

        file.close()

        print("\nStudy plan saved! ✓")

    elif choice == "2":

        file = open("datatimetable.csv", "r")

        header = file.readline()

        print("\nYOUR STUDY TIMETABLE")
        print("----------------------------")

        found = False

        for line in file:

            data = line.strip().split(",")

            day = data[0]
            subject = data[1]

            print(day, ":", subject)

            found = True

        file.close()

        if found == False:
            print("No study plans added yet.")

    elif choice == "3":

        print("\nReturning to ExamReadyTimer...")
        break

    else:

        print("\nInvalid choice. Please try again.")
