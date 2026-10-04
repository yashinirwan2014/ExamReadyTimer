from datetime import date

print("================================")
print("        EXAMREADY")
print("      EXAM COUNTDOWN")
print("================================")

exam_name = input("Enter exam name: ")
year = int(input("Enter exam year: "))
month = int(input("Enter exam month: "))
day = int(input("Enter exam day: "))

today = date.today()
exam_date = date(year, month, day)

remaining = exam_date - today

if remaining.days > 0:
    print("\nExam:", exam_name)
    print("Days remaining:", remaining.days)
    print("Keep studying! You can do it!")

elif remaining.days == 0:
    print("\nYour exam is TODAY!")

else:
    print("\nThe exam date has already passed.")
