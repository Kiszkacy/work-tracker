import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.present import PresentHandler
from work_tracker.common import AttendanceType, Date, DayType


@pytest.mark.order(1)
def test_init(present_handler: PresentHandler):
    assert present_handler is not None


def test_should_set_to_present_active_day(present_handler: PresentHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    present_handler.data.day[date].attendance_type = AttendanceType.DAYOFF

    result: CommandHandlerResult = handle_call(present_handler, active_date=date)

    assert present_handler.data.day[date].attendance_type == AttendanceType.PRESENT
    assert result.error is None


def test_should_set_to_present_active_month_workdays(present_handler: PresentHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    for day in month.days_in_a_month():
        present_handler.data.day[day].attendance_type = AttendanceType.DAYOFF

    result: CommandHandlerResult = handle_call(present_handler, active_date=month)

    for day in [day for day in month.days_in_a_month() if present_handler.data.day[day].day_type == DayType.WORKDAY]:
        assert present_handler.data.day[day].attendance_type == AttendanceType.PRESENT
    for day in [day for day in month.days_in_a_month() if present_handler.data.day[day].day_type != DayType.WORKDAY]:
        assert present_handler.data.day[day].attendance_type != AttendanceType.PRESENT
    assert result.error is None


def test_should_set_to_present_given_days(present_handler: PresentHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        present_handler.data.day[date].attendance_type = AttendanceType.DAYOFF

    result: CommandHandlerResult = handle_call(present_handler, dates=dates)

    for date in dates:
        assert present_handler.data.day[date].attendance_type == AttendanceType.PRESENT
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_set_to_present_given_months_workdays(present_handler: PresentHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        for day in month.days_in_a_month():
            present_handler.data.day[day].attendance_type = AttendanceType.DAYOFF

    result: CommandHandlerResult = handle_call(present_handler, dates=months)

    for month in months:
        for day in [day for day in month.days_in_a_month() if present_handler.data.day[day].day_type == DayType.WORKDAY]:
            assert present_handler.data.day[day].attendance_type == AttendanceType.PRESENT
        for day in [day for day in month.days_in_a_month() if present_handler.data.day[day].day_type != DayType.WORKDAY]:
            assert present_handler.data.day[day].attendance_type != AttendanceType.PRESENT
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(present_handler: PresentHandler):
    arguments: list[any] = ["value"]

    result: CommandHandlerResult = handle_call(present_handler, arguments=arguments)

    assert result.error is not None
