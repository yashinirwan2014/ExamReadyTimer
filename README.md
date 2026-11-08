# ExamReadyTimer

ExamReadyTimer is a modular, data-driven Python desktop productivity application designed to help students organize exam preparation, manage focus intervals, and track curriculum progress.

Developed originally as a practical execution of CBSE Class 12 Informatics Practices (IP) concepts, this project scales basic programming models into a unified student dashboard.

System Features

∆ Advanced Exam Countdown Engine
* Dynamic Loading: Supports tracking across multiple exam targets.
* Persistent Data Architecture: Stores and modifies milestone target dates using a local CSV layer.
* Temporal Calculations: Computes the number of days remaining until upcoming exams.
* Exam Reminders: Shows a once-per-exam reminder when the configured reminder window begins while the Exam Planner is open. Reminder history is saved locally and included in ZIP backups. The planner must be running for an alert to appear.

∆ Exam Readiness Gap Engine
* Exam-to-syllabus matching: Links an exam to the matching subject in Subject Tracker without guessing when names do not match.
* Workload estimate: Calculates pending chapters multiplied by your chosen average hours per chapter.
* Capacity forecast: Compares estimated preparation hours with the study hours you say are realistically available before the exam.
* Risk signals: Flags exams as At risk, Tight, On track, Syllabus complete, or Link a subject.
* Adjustable assumptions: Change daily study capacity and average chapter effort, then recalculate instantly.
* Transparent estimates: Shows days remaining, pending chapters, hours needed, available capacity, required daily pace and estimated shortfall. These are planning estimates, not predictions of marks or mastery.

∆ Event-Driven Pomodoro Timer
* Custom Intervals: Configurable study blocks, break durations, and session counters.
* Countdown Display: Provides a live timer for focused study sessions.

∆ Relational Study Timetable Planner
* Grid Mapping: Organizes daily objectives, subjects, and specific chapters.
* CSV Data Handling: Reads and writes timetable information using datatimetable.csv.

∆ Syllabus Analytics & Progress Tracker
* Subject Mapping: Includes a broad subject and chapter starter database for different study streams and curricula.
* Chapter Management: Add, edit, rename, delete, and mark chapters as completed or pending.
* Progress Calculation: Displays subject-wise completion totals and progress percentage.
* Automatic Saving: Saves syllabus changes to the local CSV data file.

∆ Progress Analytics
* Progress Calculation: Reads saved syllabus rows and calculates overall and subject-wise completion percentages.
* Visual Feedback: Displays completion totals and native Tkinter progress bars without third-party data or charting libraries.

∆ Distraction-Free Focus Mode
* Minimalist Interface: Provides a focused environment for dedicated study sessions.
* Focus Sessions: Supports targeted focus periods and completion notifications.

∆ Safer Student Data Storage
* Per-User Data Directory: Editable app data is stored in the operating system's user data folder instead of relying on a writable installation folder.
* Upgrade-Safe Seeding: Starter CSV files are copied into the user data folder only when they are not already present.
* Cross-Platform Paths: Uses standard user data locations on Windows, Linux, and macOS.
* Syllabus Protection: The syllabus tracker uses the per-user data directory, helping preserve chapter progress when the application is updated or moved to a protected installation location.

∆ Testing & Release Preparation
* Automated Checks: GitHub Actions workflows validate Python modules and run portable storage tests.
* Cross-Platform Matrix: The package test workflow checks supported Python versions on Windows, Linux and macOS.
* Desktop Packaging: A GitHub Actions release workflow is configured to build downloadable Windows, Linux and macOS desktop bundles.
* Release Status: Builds and tests must pass before a public release is considered ready.

∆ Architecture & Project Structure

The project utilizes a modular architecture, separating application features, data storage, and automated tests:

ExamReadyTimer→

°README.md
∆ Project documentation and architectural overview
°main.py
∆ System entry point
°GUI.py
∆ Central Tkinter dashboard and feature launcher
°countdown.py
∆ Exam date and countdown calculations
°readiness.py
∆ Exam readiness gap analysis linking exam dates, pending chapters and available study capacity
°pomodoro.py
∆ Pomodoro timer logic
°timetable.py
∆ Study timetable operations
°tracker.py
∆ Graphical syllabus tracker and chapter management
°progress.py
∆ Overall and subject-wise progress calculations and visual progress bars
°reminders.py
∆ Testable exam reminder scheduling and persistent reminder history
°focus.py
∆ Focus mode logic and interface
°storage.py
∆ Cross-platform per-user data directory and starter data initialization
°dataorsubjects.csv
∆ Subject and chapter starter data / syllabus progress storage
°dataexams.csv
∆ Exam target configurations
°datatimetable.csv
∆ Student timetable storage
°tests/
∆ Automated tests for storage, timetable rules and exam readiness calculations
°.github/workflows/
∆ Automated application checks, cross-platform tests, and desktop release builds

∆ Technical Setup & Execution

1. Clone or download the repository files to your local workspace.
2. Install Python 3.10 or newer.
3. Use Python 3.10 or newer with Tkinter available. The application uses the Python standard library; no pip packages are required for normal use. On some Linux distributions, install the system Tkinter package (for example, `python3-tk`).

4. Run the application from the project folder:

```bash
python main.py
```

5. Keep the starter CSV files in the project folder when running from source. On first launch, the app initializes the per-user data folder and copies starter files there if they do not already exist.

∆ User Data Locations

* Windows: %LOCALAPPDATA%\\ExamReadyTimer
* Linux: ~/.local/share/ExamReadyTimer (or the location configured by XDG_DATA_HOME)
* macOS: ~/Library/Application Support/ExamReadyTimer

Existing user data is not overwritten by starter files during normal initialization. Back up the user data folder before moving to another computer or manually resetting the application. ZIP backups include exam, timetable, syllabus, and reminder-history files.

∆ Academic Framework: Implementation of Informatics Practices

This project functions as a practical framework applying technical concepts through a working application:

* Data Pipelines: CSV parsing, filtering, and multi-file handling.
* Progress Mathematics: Date calculations, completion ratios, and native Tkinter progress indicators.
* Core Software Principles: Modular Python programming, Tkinter event-driven interfaces, dictionaries, file I/O, and automated testing.
* Cross-Platform Development: GitHub Actions workflows for testing and preparing desktop builds on multiple operating systems.

∆ Copyright & Usage

Copyright (c) 2026 yashinirwan2014. All rights reserved.

ExamReadyTimer is proprietary software. Official, unmodified releases may be
downloaded and used for personal, non-commercial study purposes. Copying,
modifying, republishing, redistributing, or commercially exploiting the
project requires prior written permission from the copyright holder.

See the LICENSE and COPYRIGHT files for the full terms. Access to this public
repository does not mean the project is open source or that reuse is permitted.

