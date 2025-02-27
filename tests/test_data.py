import datetime
import random

import pytest

from work_tracker.common import Date


pytestmark = pytest.mark.order(0) # run tests in this file before any other tests


def _create_date_with(defined_day: bool = False, defined_month: bool = False, defined_year: bool = False) -> Date:
    return Date(
        day=random.randint(1, 28) if defined_day else None,
        month=random.randint(1, 12) if defined_month else None,
        year=random.randint(2000, 2025) if defined_year else None,
    )


def test_today():
    expected_today: datetime.date = datetime.datetime.today()
    today: Date = Date.today()
    assert today.day == expected_today.day
    assert today.month == expected_today.month
    assert today.year == expected_today.year


def test_day_count_in_a_month():
    date: Date = Date(month=1, year=2024)
    assert date.day_count_in_a_month() == 31

    # leap year
    date = Date(month=2, year=2024)
    assert date.day_count_in_a_month() == 29

    # non leap year
    date = Date(month=2, year=2023)
    assert date.day_count_in_a_month() == 28


def test_is_day_only_date():
    date = _create_date_with(defined_day=True)
    assert date.is_day_only_date() is True

    date = _create_date_with(defined_month=True)
    assert date.is_day_only_date() is False

    date = _create_date_with(defined_year=True)
    assert date.is_day_only_date() is False

    date = _create_date_with(defined_day=True, defined_month=True)
    assert date.is_day_only_date() is False

    date = _create_date_with(defined_day=True, defined_year=True)
    assert date.is_day_only_date() is False

    date = _create_date_with(defined_month=True, defined_year=True)
    assert date.is_day_only_date() is False

    date = _create_date_with(defined_day=True, defined_month=True, defined_year=True)
    assert date.is_day_only_date() is False

    date = _create_date_with()
    assert date.is_day_only_date() is False


def test_is_month_only_date():
    date = _create_date_with(defined_day=True)
    assert date.is_month_only_date() is False

    date = _create_date_with(defined_month=True)
    assert date.is_month_only_date() is True

    date = _create_date_with(defined_year=True)
    assert date.is_month_only_date() is False

    date = _create_date_with(defined_day=True, defined_month=True)
    assert date.is_month_only_date() is False

    date = _create_date_with(defined_day=True, defined_year=True)
    assert date.is_month_only_date() is False

    date = _create_date_with(defined_month=True, defined_year=True)
    assert date.is_month_only_date() is False

    date = _create_date_with(defined_day=True, defined_month=True, defined_year=True)
    assert date.is_month_only_date() is False

    date = _create_date_with()
    assert date.is_month_only_date() is False


def test_is_year_only_date():
    date = _create_date_with(defined_day=True)
    assert date.is_year_only_date() is False

    date = _create_date_with(defined_month=True)
    assert date.is_year_only_date() is False

    date = _create_date_with(defined_year=True)
    assert date.is_year_only_date() is True

    date = _create_date_with(defined_day=True, defined_month=True)
    assert date.is_year_only_date() is False

    date = _create_date_with(defined_day=True, defined_year=True)
    assert date.is_year_only_date() is False

    date = _create_date_with(defined_month=True, defined_year=True)
    assert date.is_year_only_date() is False

    date = _create_date_with(defined_day=True, defined_month=True, defined_year=True)
    assert date.is_year_only_date() is False

    date = _create_date_with()
    assert date.is_year_only_date() is False


def test_is_day_date():
    date = _create_date_with(defined_day=True)
    assert date.is_day_date() is True

    date = _create_date_with(defined_month=True)
    assert date.is_day_date() is False

    date = _create_date_with(defined_year=True)
    assert date.is_day_date() is False

    date = _create_date_with(defined_day=True, defined_month=True)
    assert date.is_day_date() is True

    date = _create_date_with(defined_day=True, defined_year=True)
    assert date.is_day_date() is True

    date = _create_date_with(defined_month=True, defined_year=True)
    assert date.is_day_date() is False

    date = _create_date_with(defined_day=True, defined_month=True, defined_year=True)
    assert date.is_day_date() is True

    date = _create_date_with()
    assert date.is_day_date() is False


def test_is_month_date():
    date = _create_date_with(defined_day=True)
    assert date.is_month_date() is False

    date = _create_date_with(defined_month=True)
    assert date.is_month_date() is True

    date: Date = _create_date_with(defined_year=True)
    assert date.is_month_date() is False

    date = _create_date_with(defined_day=True, defined_month=True)
    assert date.is_month_date() is False

    date = _create_date_with(defined_day=True, defined_year=True)
    assert date.is_month_date() is False

    date = _create_date_with(defined_month=True, defined_year=True)
    assert date.is_month_date() is True

    date = _create_date_with(defined_day=True, defined_month=True, defined_year=True)
    assert date.is_month_date() is False

    date = _create_date_with()
    assert date.is_month_date() is False


def test_is_year_date():
    date = _create_date_with(defined_day=True)
    assert date.is_year_date() is False

    date = _create_date_with(defined_month=True)
    assert date.is_year_date() is False

    date: Date = _create_date_with(defined_year=True)
    assert date.is_year_date() is True

    date = _create_date_with(defined_day=True, defined_month=True)
    assert date.is_year_date() is False

    date = _create_date_with(defined_day=True, defined_year=True)
    assert date.is_year_date() is False

    date = _create_date_with(defined_month=True, defined_year=True)
    assert date.is_year_date() is False

    date = _create_date_with(defined_day=True, defined_month=True, defined_year=True)
    assert date.is_year_date() is False

    date = _create_date_with()
    assert date.is_year_date() is False
