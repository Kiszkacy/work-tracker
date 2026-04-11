from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.calendar import CalendarHandler
from work_tracker.common import Mode, Date


@pytest.mark.order(1)
def test_init(calendar_handler: CalendarHandler):
    assert calendar_handler is not None


def test_should_output_calendar(calendar_handler: CalendarHandler):
    result: CommandHandlerResult = handle_call(calendar_handler)

    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(calendar_handler: CalendarHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(calendar_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date(calendar_handler: CalendarHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(calendar_handler, dates=[date])

    assert result.error is not None


def test_should_work_on_valid_date(calendar_handler: CalendarHandler, random_date: Date):
    date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(calendar_handler, dates=[date])

    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_work_with_many_valid_dates(calendar_handler: CalendarHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_month_date() for date in random_dates]

    result: CommandHandlerResult = handle_call(calendar_handler, dates=dates)
    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


def test_should_work_in_today_mode(calendar_handler: CalendarHandler):
    mode: Mode = Mode.Today

    result: CommandHandlerResult = handle_call(calendar_handler, mode=mode)

    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


def test_should_work_in_day_mode(calendar_handler: CalendarHandler, random_date: Date):
    mode: Mode = Mode.Day
    active_date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(calendar_handler, mode=mode, active_date=active_date)

    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


def test_should_work_in_month_mode(calendar_handler: CalendarHandler, random_date: Date):
    mode: Mode = Mode.Month
    active_date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(calendar_handler, mode=mode, active_date=active_date)

    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


def test_should_output_legend(calendar_handler: CalendarHandler):
    result: CommandHandlerResult = handle_call(calendar_handler, arguments=["legend"])

    assert TestInputOutput.get_output().strip() is not None
    assert result.error is None


def test_should_return_error_on_extra_argument(calendar_handler: CalendarHandler):
    result: CommandHandlerResult = handle_call(calendar_handler, arguments=["legend", "extra"])

    assert result.error is not None


def test_should_return_error_on_unknown_argument(calendar_handler: CalendarHandler):
    result: CommandHandlerResult = handle_call(calendar_handler, arguments=["unknown"])

    assert result.error is not None
