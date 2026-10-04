import time

print("================================")
print("       EXAMREADY POMODORO")
print("================================")

study_time = int(input("Enter study time in minutes: "))
break_time = int(input("Enter break time in minutes: "))
sessions = int(input("How many sessions? "))

for session in range(1, sessions + 1):

    print("\n============================")
    print("Session", session)
    print("Study time started!")
    print("============================")

    seconds = study_time * 60

    while seconds > 0:

        minutes = seconds // 60
        remaining_seconds = seconds % 60

        print(
            "\rTime left:",
            minutes,
            "min",
            remaining_seconds,
            "sec",
            end=""
        )

        time.sleep(1)
        seconds = seconds - 1

    print("\nStudy session completed! ✓")

    if session < sessions:

        print("\nBreak time started!")

        seconds = break_time * 60

        while seconds > 0:

            minutes = seconds // 60
            remaining_seconds = seconds % 60

            print(
                "\rBreak left:",
                minutes,
                "min",
                remaining_seconds,
                "sec",
                end=""
            )

            time.sleep(1)
            seconds = seconds - 1

        print("\nBreak completed! ✓")

print("\n================================")
print("   ALL SESSIONS COMPLETED! 🎉")
print("================================")
print("Great work! Keep going!")
