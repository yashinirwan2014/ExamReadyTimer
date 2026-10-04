import pandas as pd
import matplotlib.pyplot as plt

print("================================")
print("      EXAMREADY ANALYTICS")
print("================================")

data = pd.read_csv("dataorsubjects.csv")

progress = {}

for subject in data["Subject"].unique():

    subject_data = data[data["Subject"] == subject]

    total = len(subject_data)

    completed = len(
        subject_data[subject_data["Status"] == "Completed"]
    )

    percentage = (completed / total) * 100

    progress[subject] = round(percentage, 1)

print("\nSUBJECT PROGRESS")
print("----------------------------")

for subject in progress:
    print(subject, ":", progress[subject], "%")

subjects = list(progress.keys())
percentages = list(progress.values())

plt.bar(subjects, percentages)

plt.title("ExamReady - Subject Progress")
plt.xlabel("Subjects")
plt.ylabel("Completion (%)")

plt.ylim(0, 100)

plt.show()
