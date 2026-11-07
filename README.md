# ExamReadyTimer

ExamReadyTimer is a modular, data-driven Python desktop productivity application designed to help students organize exam preparation, manage focus intervals, plan study time, and track syllabus progress.

## Features

- **Exam Countdown:** Track important exam dates and milestones.
- **Pomodoro Timer:** Configure focused study and break intervals.
- **Study Timetable:** Organize daily study sessions and chapters.
- **Editable Syllabus Tracker:** View subject-wise progress; add subjects and chapters/units/topics; rename or delete entries; toggle completion between Pending and Completed. Changes are saved locally in `dataorsubjects.csv`.
- **Progress Analytics:** Review study progress using the app's analytics module.
- **Focus Mode:** Use a distraction-reduced focus window.

## Using the syllabus tracker

Open **Subject Tracker** from the ExamReady dashboard. The tracker starts with the available subject list. Many curriculum entries are intentionally supplied as **Full subject syllabus** placeholders rather than claiming to contain every board's official chapter list.

To personalize a subject:
1. Choose **Add chapter / unit / topic**.
2. Select the subject and type a chapter, unit, practical, or topic name.
3. Repeat to build the complete syllabus you want to follow.
4. Use **Mark chapter completed / pending** to update progress.
5. Use **Edit chapter / topic name** or **Delete chapter / topic** to maintain your list.

You can also add a completely new subject. The first real chapter you add automatically replaces that subject's generic **Full subject syllabus** placeholder. All edits are saved to `dataorsubjects.csv` beside the application, so keep that file with the app and make a backup before manually editing it.

## Run from source

1. Install Python 3.
2. Install the dependencies listed in `requirements.txt`, if present.
3. Keep the Python scripts and CSV data files together.
4. Run `python GUI.py` (or the repository's documented entry point).

## Data files

- `dataorsubjects.csv` — subject, chapter/topic, and completion status.
- `dataexams.csv` — exam dates and targets.
- `datatimetable.csv` — study timetable entries.

The syllabus CSV keeps a simple three-column format: `Subject,Chapter,Status`.
