print("================================")
print("       EXAMREADY POMODORO")
print("================================")

study_time = int(input("Enter study time in minutes: "))
break_time = int(input("Enter break time in minutes: "))

sessions = int(input("How many study sessions? "))

print("\nYour Pomodoro Plan")
print("----------------------------")

for session in range(1, sessions + 1):
    print("\nSession", session)
    print("Study for", study_time, "minutes")
    print("Then take a", break_time, "minute break")

print("\nGood luck with your studies!")
