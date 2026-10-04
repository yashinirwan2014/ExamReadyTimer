print("================================")
print("       EXAMREADY TIMETABLE")
print("================================")

timetable = {
    "Monday": ["Physics", "Maths", "Chemistry"],
    "Tuesday": ["Maths", "Chemistry", "Physics"],
    "Wednesday": ["Chemistry", "Physics", "Maths"],
    "Thursday": ["Maths", "Physics", "Chemistry"],
    "Friday": ["Physics", "Chemistry", "Maths"]
}

day = input("\nEnter the day: ").capitalize()

if day in timetable:
    print("\nYour timetable for", day)
    print("----------------------------")

    for i in range(len(timetable[day])):
        print("Session", i + 1, ":", timetable[day][i])

else:
    print("\nNo timetable found for this day.")
