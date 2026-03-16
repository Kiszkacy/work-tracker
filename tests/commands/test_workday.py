from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.workday import WorkdayHandler
from work_tracker.common import Date, DayType, Mode


@pytest.mark.order(1)
def test_init(workday_handler: WorkdayHandler):
    assert workday_handler is not None


def test_should_set_to_workday_active_day(workday_handler: WorkdayHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    workday_handler.data.day[date].day_type = DayType.HOLIDAY

    result: CommandHandlerResult = handle_call(workday_handler, active_date=date)

    assert workday_handler.data.day[date].day_type == DayType.WORKDAY
    assert result.error is None


def test_should_set_to_workday_given_days(workday_handler: WorkdayHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        workday_handler.data.day[date].day_type = DayType.HOLIDAY

    result: CommandHandlerResult = handle_call(workday_handler, dates=dates)

    for date in dates:
        assert workday_handler.data.day[date].day_type == DayType.WORKDAY
    assert result.error is None


@pytest.mark.parametrize("random_date", [{"must_be_holiday": True}], indirect=True)
def test_should_update_month_target_if_target_was_unchanged(workday_handler: WorkdayHandler, random_date: Date):
    month_date: Date = random_date.to_month_date()
    target_before: int = workday_handler.data.month[month_date].target_minutes

    result: CommandHandlerResult = handle_call(workday_handler, active_date=random_date)

    assert result.error is None
    assert workday_handler.data.month[month_date].target_minutes > target_before


@pytest.mark.parametrize("random_date", [{"must_be_holiday": True}], indirect=True)
def test_should_not_update_month_target_if_target_was_changed(workday_handler: WorkdayHandler, random_date: Date):
    month_date: Date = random_date.to_month_date()
    workday_handler.data.month[month_date].target_minutes += 1
    target_before: int = workday_handler.data.month[month_date].target_minutes

    result: CommandHandlerResult = handle_call(workday_handler, active_date=random_date)

    assert result.error is None
    assert workday_handler.data.month[month_date].target_minutes == target_before


def test_should_return_error_on_invalid_argument_count(workday_handler: WorkdayHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(workday_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_when_used_in_month_mode(workday_handler: WorkdayHandler, random_date: Date):
    mode: Mode = Mode.Month
    active_date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(workday_handler, mode=mode, active_date=active_date)

    assert result.error is not None


def test_should_return_error_on_invalid_date(workday_handler: WorkdayHandler, random_date: Date):
    date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(workday_handler, dates=[date])

    assert result.error is not None
