import time

print("================================")
print("        EXAMREADY FOCUS")
print("================================")

minutes = int(input("\nEnter focus time in minutes: "))

print("\nFocus Mode started!")
print("Keep distractions away. 📚")

seconds = minutes * 60

while seconds > 0:

    minutes_left = seconds // 60
    seconds_left = seconds % 60

    print(
        "\rTime left:",
        minutes_left,
        "min",
        seconds_left,
        "sec",
        end=""
    )

    time.sleep(1)
    seconds = seconds - 1

print("\n\n🎯 Focus session completed!")
print("Great job! Take a short break.")
