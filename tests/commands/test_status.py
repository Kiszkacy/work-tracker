from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.status import StatusHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(status_handler: StatusHandler):
    assert status_handler is not None


def test_should_output_status_for_active_day(status_handler: StatusHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    status_handler.data.day[date].minutes_at_work = 240
    status_handler.data.day[date].target_minutes = 480

    result: CommandHandlerResult = handle_call(status_handler, active_date=date)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_status_for_active_month(status_handler: StatusHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    status_handler.data.month[month].target_minutes = 9600
    status_handler.data.month[month].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(status_handler, active_date=month)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_status_for_given_days(status_handler: StatusHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        status_handler.data.day[date].minutes_at_work = 120
        status_handler.data.day[date].target_minutes = 480

    result: CommandHandlerResult = handle_call(status_handler, dates=dates)

    for _ in dates:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_output_status_for_given_months(status_handler: StatusHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        status_handler.data.month[month].target_minutes = 9600
        status_handler.data.month[month].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(status_handler, dates=months)

    for _ in months:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(status_handler: StatusHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(status_handler, arguments=arguments)

    assert result.error is not None
