from datetime import date

import pytest

from readiness import analyze_readiness, load_exam_data, load_syllabus_data


def test_readiness_calculates_capacity_shortfall_and_required_pace():
    exams = [{"name": "Biology", "subject": "Biology", "date": date(2026, 11, 18), "priority": "High"}]
    subjects = {"Biology": {"total": 10, "completed": 6, "pending": 4}}
    result = analyze_readiness(exams, subjects, daily_hours=2, chapter_hours=1.5,
                              today=date(2026, 11, 8))[0]
    assert result["days_left"] == 10
    assert result["required_hours"] == 6
    assert result["available_hours"] == 20
    assert result["daily_required"] == 0.6
    assert result["gap_hours"] == 0
    assert result["status"] == "On track"


def test_readiness_flags_capacity_gap_and_uses_case_insensitive_subject_match():
    exams = [{"name": "Maths", "subject": "MATHEMATICS", "date": date(2026, 11, 10), "priority": "High"}]
    subjects = {"Mathematics": {"total": 20, "completed": 2, "pending": 18}}
    result = analyze_readiness(exams, subjects, daily_hours=2, chapter_hours=2,
                              today=date(2026, 11, 8))[0]
    assert result["required_hours"] == 36
    assert result["available_hours"] == 4
    assert result["gap_hours"] == 32
    assert result["status"] == "At risk"


def test_readiness_does_not_guess_when_exam_subject_is_not_linked():
    exams = [{"name": "Physics paper", "subject": "Physics", "date": date(2026, 11, 9)}]
    result = analyze_readiness(exams, {"Chemistry": {"total": 4, "completed": 1, "pending": 3}},
                               today=date(2026, 11, 8))[0]
    assert result["pending"] is None
    assert result["status"] == "Link a subject"


def test_readiness_ignores_past_exams_and_marks_completed_syllabus():
    exams = [
        {"name": "Past", "subject": "History", "date": date(2026, 11, 7)},
        {"name": "History", "subject": "History", "date": date(2026, 11, 8)},
    ]
    result = analyze_readiness(exams, {"History": {"total": 5, "completed": 5, "pending": 0}},
                               today=date(2026, 11, 8))
    assert len(result) == 1
    assert result[0]["status"] == "Syllabus complete"
    assert result[0]["days_left"] == 0


@pytest.mark.parametrize("daily,chapter", [(0, 1.5), (2, 0), (-1, 1)])
def test_readiness_rejects_non_positive_planning_assumptions(daily, chapter):
    with pytest.raises(ValueError):
        analyze_readiness([], {}, daily_hours=daily, chapter_hours=chapter)


def test_loaders_read_existing_csv_schemas(tmp_path):
    exams = tmp_path / "exams.csv"
    exams.write_text("Exam,Year,Month,Day,Subject,Priority\nPhysics,2026,11,18,Physics,High\nBad,row\n",
                     encoding="utf-8")
    syllabus = tmp_path / "subjects.csv"
    syllabus.write_text("Subject,Chapter,Status\nPhysics,Optics,Pending\nPhysics,Mechanics,Completed\nPhysics,Full subject syllabus,Pending\n",
                        encoding="utf-8")
    assert load_exam_data(exams)[0]["subject"] == "Physics"
    assert load_syllabus_data(syllabus)["Physics"] == {"total": 2, "completed": 1, "pending": 1}


@pytest.mark.parametrize("daily,chapter", [
    (float("nan"), 1.5),
    (float("inf"), 1.5),
    (2, float("-inf")),
])
def test_readiness_rejects_non_finite_planning_assumptions(daily, chapter):
    with pytest.raises(ValueError, match="finite"):
        analyze_readiness([], {}, daily_hours=daily, chapter_hours=chapter)
