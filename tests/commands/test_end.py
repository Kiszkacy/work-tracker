from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.end import EndHandler
from work_tracker.command.common import TimeArgument, TimeArgumentType
from work_tracker.common import Date, Mode, Time


@pytest.mark.order(1)
def test_init(end_handler: EndHandler):
    assert end_handler is not None


def test_should_set_work_end_to_given_time_for_active_day(end_handler: EndHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=17 * 60, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(end_handler, active_date=date, arguments=[time_arg])

    assert end_handler.data.day[date].work_end is not None
    assert end_handler.data.day[date].work_end.minutes_since_midnight == 17 * 60
    assert result.error is None


def test_should_set_work_end_to_now_when_no_time_argument_given(end_handler: EndHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(end_handler, active_date=date)

    assert end_handler.data.day[date].work_end is not None
    assert result.error is None


def test_should_calculate_minutes_at_work_when_start_is_set(end_handler: EndHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    start_minutes: int = 8 * 60
    end_minutes: int = 16 * 60
    end_handler.data.day[date].work_start = Time(minutes_since_midnight=start_minutes)
    time_arg: TimeArgument = TimeArgument(minutes=end_minutes, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(end_handler, active_date=date, arguments=[time_arg])

    assert end_handler.data.day[date].minutes_at_work == end_minutes - start_minutes
    assert result.error is None


def test_should_reset_work_start_and_set_zero_minutes_when_end_before_start(end_handler: EndHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    end_handler.data.day[date].work_start = Time(minutes_since_midnight=10 * 60)
    time_arg: TimeArgument = TimeArgument(minutes=8 * 60, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(end_handler, active_date=date, arguments=[time_arg])

    assert end_handler.data.day[date].work_start.minutes_since_midnight == 8 * 60
    assert end_handler.data.day[date].minutes_at_work == 0
    assert result.error is None


def test_should_set_work_end_for_given_days_with_time(end_handler: EndHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    time_arg: TimeArgument = TimeArgument(minutes=18 * 60, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(end_handler, dates=dates, arguments=[time_arg])

    for date in dates:
        assert end_handler.data.day[date].work_end is not None
        assert end_handler.data.day[date].work_end.minutes_since_midnight == 18 * 60
    assert result.error is None


def test_should_set_work_end_for_given_days_without_time(end_handler: EndHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]

    result: CommandHandlerResult = handle_call(end_handler, dates=dates)

    for date in dates:
        assert end_handler.data.day[date].work_end is not None
    assert result.error is None


def test_should_return_error_when_in_month_mode(end_handler: EndHandler, random_date: Date):
    month: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(end_handler, active_date=month, mode=Mode.Month)

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(end_handler: EndHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=17 * 60, type=TimeArgumentType.Overwrite)
    arguments: list[Any] = [time_arg, time_arg]

    result: CommandHandlerResult = handle_call(end_handler, active_date=date, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_date(end_handler: EndHandler, random_date: Date):
    month_date: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(end_handler, dates=[month_date])

    assert result.error is not None
