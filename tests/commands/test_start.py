from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.start import StartHandler
from work_tracker.command.common import TimeArgument, TimeArgumentType
from work_tracker.common import Date, Mode, Time


@pytest.mark.order(1)
def test_init(start_handler: StartHandler):
    assert start_handler is not None


def test_should_set_work_start_to_given_time_for_active_day(start_handler: StartHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=9 * 60, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(start_handler, active_date=date, arguments=[time_arg])

    assert start_handler.data.day[date].work_start is not None
    assert start_handler.data.day[date].work_start.minutes_since_midnight == 9 * 60
    assert result.error is None


def test_should_set_work_start_to_now_when_no_time_argument_given(start_handler: StartHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(start_handler, active_date=date)

    assert start_handler.data.day[date].work_start is not None
    assert result.error is None


def test_should_calculate_minutes_at_work_when_end_is_set(start_handler: StartHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    start_minutes: int = 8 * 60
    end_minutes: int = 16 * 60
    start_handler.data.day[date].work_end = Time(minutes_since_midnight=end_minutes)
    time_arg: TimeArgument = TimeArgument(minutes=start_minutes, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(start_handler, active_date=date, arguments=[time_arg])

    assert start_handler.data.day[date].minutes_at_work == end_minutes - start_minutes
    assert result.error is None


def test_should_reset_work_start_and_set_zero_minutes_when_start_after_end(start_handler: StartHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    start_handler.data.day[date].work_end = Time(minutes_since_midnight=8 * 60)
    time_arg: TimeArgument = TimeArgument(minutes=10 * 60, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(start_handler, active_date=date, arguments=[time_arg])

    assert start_handler.data.day[date].work_end.minutes_since_midnight == 10 * 60
    assert start_handler.data.day[date].minutes_at_work == 0
    assert result.error is None


def test_should_set_work_start_for_given_days_with_time(start_handler: StartHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    time_arg: TimeArgument = TimeArgument(minutes=9 * 60, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(start_handler, dates=dates, arguments=[time_arg])

    for date in dates:
        assert start_handler.data.day[date].work_start is not None
        assert start_handler.data.day[date].work_start.minutes_since_midnight == 9 * 60
    assert result.error is None


def test_should_set_work_start_for_given_days_without_time(start_handler: StartHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]

    result: CommandHandlerResult = handle_call(start_handler, dates=dates)

    for date in dates:
        assert start_handler.data.day[date].work_start is not None
    assert result.error is None


def test_should_return_error_when_in_month_mode(start_handler: StartHandler, random_date: Date):
    month: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(start_handler, active_date=month, mode=Mode.Month)

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(start_handler: StartHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=9 * 60, type=TimeArgumentType.Overwrite)
    arguments: list[Any] = [time_arg, time_arg]

    result: CommandHandlerResult = handle_call(start_handler, active_date=date, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date(start_handler: StartHandler, random_date: Date):
    month_date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(start_handler, dates=[month_date])

    assert result.error is not None
