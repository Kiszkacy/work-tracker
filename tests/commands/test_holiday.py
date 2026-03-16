import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.holiday import HolidayHandler
from work_tracker.common import DayType, Date, DayType, Mode


@pytest.mark.order(1)
def test_init(holiday_handler: HolidayHandler):
    assert holiday_handler is not None


def test_should_set_to_holiday_active_day(holiday_handler: HolidayHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    holiday_handler.data.day[date].day_type = DayType.WORKDAY

    result: CommandHandlerResult = handle_call(holiday_handler, active_date=date)

    assert holiday_handler.data.day[date].day_type == DayType.HOLIDAY
    assert result.error is None


def test_should_set_to_holiday_given_days(holiday_handler: HolidayHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        holiday_handler.data.day[date].day_type = DayType.WORKDAY

    result: CommandHandlerResult = handle_call(holiday_handler, dates=dates)

    for date in dates:
        assert holiday_handler.data.day[date].day_type == DayType.HOLIDAY
    assert result.error is None



@pytest.mark.parametrize("random_date", [{"must_be_workday": True}], indirect=True)
def test_should_update_month_target_if_target_was_unchanged(holiday_handler: HolidayHandler, random_date: Date):
    month_date: Date = random_date.to_month_date()
    target_before: int = holiday_handler.data.month[month_date].target_minutes

    result: CommandHandlerResult = handle_call(holiday_handler, active_date=random_date)

    assert result.error is None
    assert holiday_handler.data.month[month_date].target_minutes != target_before


@pytest.mark.parametrize("random_date", [{"must_be_workday": True}], indirect=True)
def test_should_not_update_month_target_if_target_was_changed(holiday_handler: HolidayHandler, random_date: Date):
    month_date: Date = random_date.to_month_date()
    holiday_handler.data.month[month_date].target_minutes += 1
    target_before: int = holiday_handler.data.month[month_date].target_minutes

    result: CommandHandlerResult = handle_call(holiday_handler, active_date=random_date)

    assert result.error is None
    assert holiday_handler.data.month[month_date].target_minutes == target_before

def test_should_return_error_on_invalid_argument_count(holiday_handler: HolidayHandler):
    arguments: list[any] = ["value"]

    result: CommandHandlerResult = handle_call(holiday_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_when_used_in_month_mode(holiday_handler: HolidayHandler, random_date: Date):
    mode: Mode = Mode.Month
    active_date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(holiday_handler, mode=mode, active_date=active_date)

    assert result.error is not None


def test_should_return_error_on_invalid_date(holiday_handler: HolidayHandler, random_date: Date):
    date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(holiday_handler, dates=[date])

    assert result.error is not None