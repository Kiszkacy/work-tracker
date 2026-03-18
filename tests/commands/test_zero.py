from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.zero import ZeroHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(zero_handler: ZeroHandler):
    assert zero_handler is not None


def test_should_set_minutes_at_work_to_zero_for_active_day(zero_handler: ZeroHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    zero_handler.data.day[date].minutes_at_work = 480

    result: CommandHandlerResult = handle_call(zero_handler, active_date=date)

    assert zero_handler.data.day[date].minutes_at_work == 0
    assert result.error is None


def test_should_set_minutes_at_work_to_zero_for_active_month(zero_handler: ZeroHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    for day in month.days_in_a_month():
        zero_handler.data.day[day].minutes_at_work = 480

    result: CommandHandlerResult = handle_call(zero_handler, active_date=month)

    for day in month.days_in_a_month():
        assert zero_handler.data.day[day].minutes_at_work == 0
    assert result.error is None


def test_should_set_minutes_at_work_to_zero_for_given_days(zero_handler: ZeroHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        zero_handler.data.day[date].minutes_at_work = 480

    result: CommandHandlerResult = handle_call(zero_handler, dates=dates)

    for date in dates:
        assert zero_handler.data.day[date].minutes_at_work == 0
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_set_minutes_at_work_to_zero_for_given_months(zero_handler: ZeroHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        for day in month.days_in_a_month():
            zero_handler.data.day[day].minutes_at_work = 480

    result: CommandHandlerResult = handle_call(zero_handler, dates=months)

    for month in months:
        for day in month.days_in_a_month():
            assert zero_handler.data.day[day].minutes_at_work == 0
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(zero_handler: ZeroHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(zero_handler, arguments=arguments)

    assert result.error is not None
