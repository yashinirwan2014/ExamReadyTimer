# ExamReadyTimer

ExamReadyTimer is a Python desktop app for keeping study plans and exam dates in one place. I wanted a single window where I could open a countdown, timetable, chapter tracker or study timer without keeping several separate notes.

The app uses **Tkinter** for its windows and buttons, and **CSV files** for saving information on the computer. It is designed for students who want a simple offline organiser.

## What is included

- **Exam planner:** add exam dates, subjects and reminder settings, then see how many days are left.
- **Pomodoro timer:** set study and break intervals.
- **Timetable:** keep a weekly plan of study blocks.
- **Subject tracker:** add chapters and mark them complete or pending.
- **Progress view:** see completed chapters and subject-wise progress.
- **Focus timer:** run a dedicated study timer. It does not block websites or other applications.
- **Study sessions:** record time spent on a subject and chapter, and review basic totals.
- **Revision list:** keep track of topics due for another review.
- **Backup and restore:** save the app's local data in a ZIP file and restore it later.

Some of the planning features use simple estimates based on the information entered. They do not predict marks, guarantee syllabus completion or measure how well a topic has been learned.

## Screens and files

The project is split into Python files so each window has its own job. The main entry point is `main.py`, and `GUI.py` builds the dashboard. The other files handle individual features and data storage.

For a plain-language explanation of the code, including which parts use Class 12 Python concepts and which parts are extra, see [STUDENT_GUIDE.md](STUDENT_GUIDE.md).

## Run from source

You need Python 3.10 or newer with Tkinter available. The app uses the Python standard library for normal use; no pip packages are required to run it. Some Linux installations package Tkinter separately (often as `python3-tk`).

1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Run:

   ```bash
   python main.py
   ```

Keep the starter CSV files with the project when running from source. On first launch, the app copies them into its user data folder if they are not already there.

## Download the desktop app

The published downloads and release notes are on the [GitHub Releases page](https://github.com/yashinirwan2014/ExamReadyTimer/releases).

- [Windows ZIP](https://github.com/yashinirwan2014/ExamReadyTimer/releases/download/v1.3.0/ExamReadyTimer-Windows.zip)
- [Linux ZIP](https://github.com/yashinirwan2014/ExamReadyTimer/releases/download/v1.3.0/ExamReadyTimer-Linux.zip)
- macOS: no verified public download is currently offered. The older package should not be used while its launch and security behaviour is being checked.

These are portable ZIP packages, not normal installers. Read the `README-FIRST.txt` file inside the ZIP before launching. Keep the files in the extracted folder together.

## Where the app saves data

The app uses a separate folder in your user account, rather than trying to write into the installation folder.

- Windows: `%LOCALAPPDATA%\ExamReadyTimer`
- Linux: `~/.local/share/ExamReadyTimer` (or `XDG_DATA_HOME`, if set)
- macOS: `~/Library/Application Support/ExamReadyTimer`

The Settings window shows the exact folder and has backup and restore options. Make a backup before moving the app or restoring an older copy.

## Tests and builds

The repository includes automated tests and GitHub Actions workflows. They check selected Python functions, data handling and build steps. Passing tests are useful, but they do not prove that every feature works on every computer.

The release workflow uses PyInstaller to package the app. The macOS build is not Apple-notarized; a successful GitHub build does not mean Apple has approved it.

## Project background

The app uses Python topics such as variables, lists, dictionaries, conditions, loops, functions, modules, file handling and exception handling. Tkinter provides the graphical interface. A few supporting features use tools beyond the basic Class 12 syllabus; these are explained separately in [STUDENT_GUIDE.md](STUDENT_GUIDE.md).

## Licence and reuse

See [LICENSE](LICENSE) and [COPYRIGHT](COPYRIGHT) for the project's terms. A public repository does not automatically mean that the code is open source.
