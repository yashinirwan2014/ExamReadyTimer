# ExamReadyTimer

ExamReadyTimer is a modular, data-driven Python desktop productivity application designed to help students organize exam preparation, manage focus intervals, and track curriculum progress.

Developed originally as a practical execution of CBSE Class 12 Informatics Practices (IP) concepts, this project scales basic programming models into a unified student dashboard.

System Features

∆ Advanced Exam Countdown Engine
* Dynamic Loading: Supports tracking across multiple exam targets.
* Persistent Data Architecture: Stores and modifies milestone target dates using a local CSV layer.
* Temporal Calculations: Computes the number of days remaining until upcoming exams.

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

∆ Data Analytics Visualization Suite (Pandas & Matplotlib)
* Data Integration: Uses Pandas to load and process study tracking data.
* Statistical Rendering: Displays study progress through Matplotlib charts.

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
* Cross-Platform Matrix: The package test workflow checks supported Python versions on Windows and Linux.
* Desktop Packaging: A GitHub Actions release workflow is configured to build downloadable Windows and Linux desktop bundles when a version tag is published.
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
°pomodoro.py
∆ Pomodoro timer logic
°timetable.py
∆ Study timetable operations
°tracker.py
∆ Graphical syllabus tracker and chapter management
°progress.py
∆ Pandas data processing and progress visualizations
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
∆ Automated tests for application data storage
°.github/workflows/
∆ Automated application checks, cross-platform tests, and desktop release builds

∆ Technical Setup & Execution

1. Clone or download the repository files to your local workspace.
2. Install Python 3.10 or newer.
3. Install the required Python libraries:

```bash
python -m pip install pandas matplotlib
```

4. Run the application from the project folder:

```bash
python main.py
```

5. Keep the starter CSV files in the project folder when running from source. On first launch, the app initializes the per-user data folder and copies starter files there if they do not already exist.

∆ User Data Locations

* Windows: %LOCALAPPDATA%\\ExamReadyTimer
* Linux: ~/.local/share/ExamReadyTimer (or the location configured by XDG_DATA_HOME)
* macOS: ~/Library/Application Support/ExamReadyTimer

Existing user data is not overwritten by starter files during normal initialization. Back up the user data folder before moving to another computer or manually resetting the application.

∆ Academic Framework: Implementation of Informatics Practices

This project functions as a practical framework applying technical concepts through a working application:

* Data Pipelines: Pandas DataFrames, CSV parsing, filtering, and multi-file handling.
* Mathematical Graphics: Matplotlib data visualization, bar charts, plot configurations, and dynamic scaling.
* Core Software Principles: Modular Python programming, Tkinter event-driven interfaces, dictionaries, file I/O, and automated testing.
* Cross-Platform Development: GitHub Actions workflows for testing and preparing desktop builds on multiple operating systems.

