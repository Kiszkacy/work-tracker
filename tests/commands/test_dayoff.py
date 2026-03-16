from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.dayoff import DayoffHandler
from work_tracker.common import AttendanceType, Date, DayType


@pytest.mark.order(1)
def test_init(dayoff_handler: DayoffHandler):
    assert dayoff_handler is not None


def test_should_set_to_dayoff_active_day(dayoff_handler: DayoffHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    dayoff_handler.data.day[date].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(dayoff_handler, active_date=date)

    assert dayoff_handler.data.day[date].attendance_type == AttendanceType.DAYOFF
    assert result.error is None


def test_should_set_to_dayoff_active_month_workdays(dayoff_handler: DayoffHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    for day in month.days_in_a_month():
        dayoff_handler.data.day[day].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(dayoff_handler, active_date=month)

    for day in [day for day in month.days_in_a_month() if dayoff_handler.data.day[day].day_type == DayType.WORKDAY]:
        assert dayoff_handler.data.day[day].attendance_type == AttendanceType.DAYOFF
    for day in [day for day in month.days_in_a_month() if dayoff_handler.data.day[day].day_type != DayType.WORKDAY]:
        assert dayoff_handler.data.day[day].attendance_type != AttendanceType.DAYOFF
    assert result.error is None


def test_should_set_to_dayoff_given_days(dayoff_handler: DayoffHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        dayoff_handler.data.day[date].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(dayoff_handler, dates=dates)

    for date in dates:
        assert dayoff_handler.data.day[date].attendance_type == AttendanceType.DAYOFF
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_set_to_dayoff_given_months_workdays(dayoff_handler: DayoffHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        for day in month.days_in_a_month():
            dayoff_handler.data.day[day].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(dayoff_handler, dates=months)

    for month in months:
        for day in [day for day in month.days_in_a_month() if dayoff_handler.data.day[day].day_type == DayType.WORKDAY]:
            assert dayoff_handler.data.day[day].attendance_type == AttendanceType.DAYOFF
        for day in [day for day in month.days_in_a_month() if dayoff_handler.data.day[day].day_type != DayType.WORKDAY]:
            assert dayoff_handler.data.day[day].attendance_type != AttendanceType.DAYOFF
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(dayoff_handler: DayoffHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(dayoff_handler, arguments=arguments)

    assert result.error is not None
