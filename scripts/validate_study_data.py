"""Cross-platform validation for ExamReadyTimer starter CSV data."""
import csv
from pathlib import Path

SCHEMAS = {
    "dataexams.csv": {"Exam", "Year", "Month", "Day"},
    "datatimetable.csv": {"Day", "Subject"},
    "dataorsubjects.csv": {"Subject", "Chapter", "Status"},
}


def validate_csv(path: Path, required: set[str]) -> int:
    if not path.is_file():
        raise SystemExit(f"Missing required data file: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or [])
        missing = required - fields
        if missing:
            raise SystemExit(f"{path}: missing required columns: {', '.join(sorted(missing))}")
        rows = list(reader)
    for number, row in enumerate(rows, start=2):
        if any(value is None for value in row.values()):
            raise SystemExit(f"{path}: malformed row at line {number}")
    return len(rows)


def main() -> None:
    total = 0
    for filename, required in SCHEMAS.items():
        count = validate_csv(Path(filename), required)
        total += count
        print(f"✓ {filename}: {count} data rows; required columns present")
    print(f"CSV validation passed ({total} total rows).")


if __name__ == "__main__":
    main()
