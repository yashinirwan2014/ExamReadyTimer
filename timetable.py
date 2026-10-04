print("================================")
print("       EXAMREADY TIMETABLE")
print("================================")

timetable = {}

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

        if day not in timetable:
            timetable[day] = []

        timetable[day].append(subject)

        print("\nStudy plan added! ✓")

    elif choice == "2":

        if len(timetable) == 0:
            print("\nNo study plan added yet.")

        else:

            print("\nYOUR STUDY TIMETABLE")
            print("----------------------------")

            for day in timetable:

                print("\n" + day)

                for i in range(len(timetable[day])):
                    print("Session", i + 1, ":", timetable[day][i])

    elif choice == "3":

        print("\nReturning to ExamReadyTimer...")
        break

    else:

        print("\nInvalid choice. Please try again.")
