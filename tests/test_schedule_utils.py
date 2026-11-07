import pytest

from schedule_utils import duration_minutes, times_overlap


def test_duration_minutes():
    assert duration_minutes("09:00", "10:30") == 90


@pytest.mark.parametrize("start,end", [("10:00", "10:00"), ("11:00", "10:00"), ("25:00", "26:00")])
def test_duration_rejects_invalid_or_reversed_ranges(start, end):
    with pytest.raises(ValueError):
        duration_minutes(start, end)


def test_time_overlap_detects_intersection_but_allows_adjacent_blocks():
    assert times_overlap("09:00", "10:00", "09:45", "10:30")
    assert not times_overlap("09:00", "10:00", "10:00", "11:00")
