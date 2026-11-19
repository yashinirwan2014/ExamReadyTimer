# ExamReadyTimer

ExamReadyTimer is a desktop study organiser made with Python and Tkinter. I built it to keep exam dates, study plans, chapter progress and study sessions together in one place.

The app is intended for students who want a simple organiser that can work without an internet connection.

## Features

* **Exam planner:** Add exam dates and subjects, then check how many days remain.
* **Pomodoro timer:** Use focus and break cycles.
* **Timetable:** Save a weekly study plan.
* **Chapter tracker:** Add chapters and mark them as complete or pending.
* **Progress view:** Check completed chapters and subject progress.
* **Focus timer:** Track a study period. It does not block websites or other apps.
* **Study sessions:** Record time spent on a subject or chapter.
* **Revision list:** Keep topics that need another review.
* **Backup and restore:** Save local app data in a ZIP file and restore it later.

The progress figures are based on the information entered by the user. They do not predict exam marks or guarantee that a topic has been learned.

## Built with

* Python
* Tkinter
* CSV files for local data
* Python standard library

The project also includes a bundled MoMo Trust Display typeface. Its licence is included in the repository.

## Run the app from source

You need Python 3.10 or newer with Tkinter available. The app does not need extra pip packages for normal use. Some Linux systems provide Tkinter as a separate package.

1. Download or clone this repository.
2. Open a terminal in the project folder.
3. Run:

```bash
python main.py
```

Keep the starter CSV files with the project. On the first launch, the app copies them to its data folder if they are not already present.

## Desktop downloads

Visit the [GitHub Releases page](https://github.com/yashinirwan2014/ExamReadyTimer/releases) to see the available desktop downloads and release notes.

The downloads are portable ZIP files rather than regular installers. Read the `README-FIRST.txt` file inside the ZIP and keep the files in the extracted folder together.

### Check a downloaded file

Each release may include a `SHA256SUMS.txt` file. If it is included, compare the checksum of your downloaded ZIP with the matching entry in that file.

On Windows, open PowerShell in the folder containing the ZIP and run:

```powershell
Get-FileHash .\ExamReadyTimer-Windows.zip -Algorithm SHA256
```

A matching checksum confirms that the downloaded file matches the published file. It does not prove that the app is harmless or replace antivirus software.

### Windows security notice

The Windows app is not digitally signed. A browser warning or Microsoft Defender SmartScreen warning may appear. Download the app only from this repository. Do not turn off antivirus protection to run it. If a security warning is unclear, ask a trusted adult or a knowledgeable technician for help.

## Where data is saved

The app saves its data in a folder inside the user account.

* Windows: `%LOCALAPPDATA%\ExamReadyTimer`
* Linux: `~/.local/share/ExamReadyTimer` or the folder set by `XDG_DATA_HOME`
* macOS: `~/Library/Application Support/ExamReadyTimer`

The Settings window shows the data folder and provides backup and restore options. Make a backup before restoring an older copy.

## Project files

The main program starts from `main.py`. The dashboard is built in `GUI.py`, while other Python files handle individual parts of the app.

For a simple explanation of the code and the Python concepts used, read [STUDENT_GUIDE.md](STUDENT_GUIDE.md).

## Tests and builds

The repository includes automated tests and GitHub Actions workflows. The tests check Python functions, data handling and selected application features. A passing test run is useful, but it cannot guarantee that the app will behave identically on every computer.

The desktop packages are built with PyInstaller. The macOS package is not Apple notarised.

## Class 12 Informatics Practices concepts

The project uses Python concepts such as variables, data types, lists, dictionaries, conditions, loops, functions, modules, file handling and exception handling. Tkinter is used to create the desktop interface.

Some parts of the project use tools beyond the basic Class 12 syllabus. The student guide explains these separately.

## Licence and font

Read [LICENSE](LICENSE) and [COPYRIGHT](COPYRIGHT) for the project terms. A public repository does not automatically mean that all files can be reused freely.

The MoMo Trust Display typeface is provided under the SIL Open Font License 1.1. Its licence notice is in `assets/MOMO-FONT-LICENSE.txt` and is also included with the desktop release files.
