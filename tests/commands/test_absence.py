import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.absence import AbsenceHandler
from work_tracker.common import AttendanceType, Date, DayType


@pytest.mark.order(1)
def test_init(absence_handler: AbsenceHandler):
    assert absence_handler is not None


def test_should_set_to_absence_active_day(absence_handler: AbsenceHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    absence_handler.data.day[date].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(absence_handler, active_date=date)

    assert absence_handler.data.day[date].attendance_type == AttendanceType.ABSENCE
    assert result.error is None


def test_should_set_to_absence_active_month_workdays(absence_handler: AbsenceHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    for day in month.days_in_a_month():
        absence_handler.data.day[day].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(absence_handler, active_date=month)

    for day in [day for day in month.days_in_a_month() if absence_handler.data.day[day].day_type == DayType.WORKDAY]:
        assert absence_handler.data.day[day].attendance_type == AttendanceType.ABSENCE
    for day in [day for day in month.days_in_a_month() if absence_handler.data.day[day].day_type != DayType.WORKDAY]:
        assert absence_handler.data.day[day].attendance_type != AttendanceType.ABSENCE
    assert result.error is None


def test_should_set_to_absence_given_days(absence_handler: AbsenceHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        absence_handler.data.day[date].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(absence_handler, dates=dates)

    for date in dates:
        assert absence_handler.data.day[date].attendance_type == AttendanceType.ABSENCE
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_set_to_absence_given_months_workdays(absence_handler: AbsenceHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        for day in month.days_in_a_month():
            absence_handler.data.day[day].attendance_type = AttendanceType.PRESENT

    result: CommandHandlerResult = handle_call(absence_handler, dates=months)

    for month in months:
        for day in [day for day in month.days_in_a_month() if absence_handler.data.day[day].day_type == DayType.WORKDAY]:
            assert absence_handler.data.day[day].attendance_type == AttendanceType.ABSENCE
        for day in [day for day in month.days_in_a_month() if absence_handler.data.day[day].day_type != DayType.WORKDAY]:
            assert absence_handler.data.day[day].attendance_type != AttendanceType.ABSENCE
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(absence_handler: AbsenceHandler):
    arguments: list[any] = ["value"]

    result: CommandHandlerResult = handle_call(absence_handler, arguments=arguments)

    assert result.error is not None