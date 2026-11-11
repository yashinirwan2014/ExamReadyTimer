# ExamReadyTimer

ExamReadyTimer is a Python desktop app for keeping study plans and exam dates in one place. I wanted a single window where I could open a countdown, timetable, chapter tracker or study timer without keeping several separate notes.

The app uses **Tkinter** for its windows and buttons, **CSV files** for local study data, and the bundled MoMo Trust Display typeface under its SIL Open Font License. It is designed for students who want a simple offline organiser.

## What is included

- **Exam planner:** add exam dates, subjects and reminder settings, then see how many days are left.
- **Pomodoro timer:** automatic 25-minute focus and 5-minute break cycles with a two-tone completion chime.
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

- [Windows ZIP](https://github.com/yashinirwan2014/ExamReadyTimer/releases/download/v1.1.1/ExamReadyTimer-Windows.zip)
- [Linux ZIP](https://github.com/yashinirwan2014/ExamReadyTimer/releases/download/v1.1.1/ExamReadyTimer-Linux.zip)
- [macOS experimental ZIP](https://github.com/yashinirwan2014/ExamReadyTimer/releases/download/v1.1.1/ExamReadyTimer-macOS.zip) — ad-hoc signed, not Apple-notarized; Gatekeeper may block it.
- [SHA-256 checksums](https://github.com/yashinirwan2014/ExamReadyTimer/releases/download/v1.1.1/SHA256SUMS.txt)

These are portable ZIP packages, not normal installers. Read the `README-FIRST.txt` file inside the ZIP before launching. Keep the files in the extracted folder together.

### Verify a download on Windows

Open PowerShell in the folder containing the downloaded ZIP and run:

```powershell
Get-FileHash .\\ExamReadyTimer-Windows.zip -Algorithm SHA256
```

Compare the displayed hash with the Windows ZIP entry in `SHA256SUMS.txt` on the release page. Use the matching filename for Linux or macOS. A matching hash confirms that the file matches the published release; it does not certify that Windows will consider the app safe or malware-free.

### Windows security warnings

A new, unsigned desktop app can receive a browser download warning or a Microsoft Defender SmartScreen reputation warning. These warnings are not proof that the app is malicious, and a clean scan is not a guarantee of safety. Download only from this repository's official Releases page, verify the checksum, and do not disable Microsoft Defender or bypass a warning if you are unsure. If Microsoft Defender identifies the official build as a false positive, use Microsoft's [file submission portal](https://www.microsoft.com/en-us/wdsi/filesubmission) to submit it for review. Free checksum verification does not replace a trusted code-signing certificate; we are not claiming the app is digitally signed or Microsoft-certified.

## Where the app saves data

The app uses a separate folder in your user account, rather than trying to write into the installation folder.

- Windows: `%LOCALAPPDATA%\ExamReadyTimer`
- Linux: `~/.local/share/ExamReadyTimer` (or `XDG_DATA_HOME`, if set)
- macOS: `~/Library/Application Support/ExamReadyTimer`

The Settings window shows the exact folder and has backup and restore options. Make a backup before moving the app or restoring an older copy.

## Tests and builds

The repository includes automated tests and GitHub Actions workflows. They check Python functions, GUI interactions, data handling, session persistence and build steps. Passing tests are useful, but they do not prove that every feature works on every computer.

The release workflow uses PyInstaller to package the app. The macOS build is not Apple-notarized; a successful GitHub build does not mean Apple has approved it.

## Project background

The app uses Python topics such as variables, lists, dictionaries, conditions, loops, functions, modules, file handling and exception handling. Tkinter provides the graphical interface. A few supporting features use tools beyond the basic Class 12 syllabus; these are explained separately in [STUDENT_GUIDE.md](STUDENT_GUIDE.md).

## Licence and reuse

See [LICENSE](LICENSE) and [COPYRIGHT](COPYRIGHT) for the project's terms. A public repository does not automatically mean that the code is open source.


## Typeface

MoMo Trust Display is bundled under the SIL Open Font License 1.1. Its copyright and licence notice are included in `assets/MOMO-FONT-LICENSE.txt` and each release archive.


## Download integrity and Windows security

Each desktop release includes a `SHA256SUMS.txt` file containing SHA-256 hashes for the three downloadable ZIP archives. Verify the archive you downloaded before extracting it. Checksums detect accidental corruption or changes in transit; they do not scan a file, prove that software is harmless, create SmartScreen reputation, or replace a trusted digital signature.

ExamReadyTimer's Windows executable is currently unsigned. A browser warning or SmartScreen reputation prompt can therefore appear for some users, especially while the download has little reputation. Do not disable antivirus protection to run it. Download from the official repository, verify the checksum, and ask a trusted adult or knowledgeable technician if a security prompt is unclear. If Microsoft Defender incorrectly detects the official release, submit the file through [Microsoft's security intelligence file submission portal](https://www.microsoft.com/en-us/wdsi/filesubmission). The project does not claim Microsoft approval or a malware-free guarantee.
