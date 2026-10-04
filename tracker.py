print("================================")
print("       EXAMREADY TRACKER")
print("================================")

file = open("dataorsubjects.csv", "r")

header = file.readline()

subjects = {}

for line in file:
    data = line.strip().split(",")

    subject = data[0]
    chapter = data[1]
    status = data[2]

    if subject not in subjects:
        subjects[subject] = []

    subjects[subject].append([chapter, status])

file.close()

for subject in subjects:

    print("\n" + subject)
    print("----------------------------")

    completed = 0
    total = len(subjects[subject])

    for chapter in subjects[subject]:

        name = chapter[0]
        status = chapter[1]

        if status == "Completed":
            print("[✓]", name)
            completed = completed + 1
        else:
            print("[ ]", name)

    percentage = (completed / total) * 100

    print("\nProgress:", round(percentage, 1), "%")
