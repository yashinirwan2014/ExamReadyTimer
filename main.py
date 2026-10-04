print("======================================")
print("             EXAMREADY")
print("     STUDY • FOCUS • PREPARE")
print("======================================")

while True:

    print("\nMAIN MENU")
    print("----------------------------")
    print("1. Exam Countdown")
    print("2. Pomodoro Planner")
    print("3. Timetable")
    print("4. Subject Tracker")
    print("5. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        print("\nOpening Exam Countdown...")
        exec(open("countdown.py").read())

    elif choice == "2":
        print("\nOpening Pomodoro...")
        exec(open("pomodoro.py").read())

    elif choice == "3":
        print("\nOpening Timetable...")
        exec(open("timetable.py").read())

    elif choice == "4":
        print("\nOpening Subject and Chapter Tracker...")
        exec(open("tracker.py").read())

    elif choice == "5":
        print("\nThank you for using ExamReadyTimer!")
        break

    else:
        print("\nInvalid choice. Please try again.")
