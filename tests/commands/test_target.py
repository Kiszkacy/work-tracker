from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.target import TargetHandler
from work_tracker.command.common import TimeArgument, TimeArgumentType
from work_tracker.common import Date, Mode


@pytest.mark.order(1)
def test_init(target_handler: TargetHandler):
    assert target_handler is not None


def test_should_output_day_target_for_active_day(target_handler: TargetHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    target_handler.data.day[date].target_minutes = 480

    result: CommandHandlerResult = handle_call(target_handler, active_date=date)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_month_target_for_active_month(target_handler: TargetHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    target_handler.data.month[month].target_minutes = 9600

    result: CommandHandlerResult = handle_call(target_handler, active_date=month)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_office_target_for_active_month(target_handler: TargetHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    target_handler.data.month[month].target_minutes = 9600
    target_handler.data.month[month].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(target_handler, active_date=month, mode=Mode.Month, arguments=["office"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_remote_target_for_active_month(target_handler: TargetHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    target_handler.data.month[month].target_minutes = 9600
    target_handler.data.month[month].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(target_handler, active_date=month, mode=Mode.Month, arguments=["remote"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_change_day_target_for_active_day(target_handler: TargetHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=360, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(target_handler, active_date=date, arguments=[time_arg])

    assert target_handler.data.day[date].target_minutes == 360
    assert result.error is None


def test_should_change_month_target_for_active_month(target_handler: TargetHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    time_arg: TimeArgument = TimeArgument(minutes=9000, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(target_handler, active_date=month, arguments=[time_arg])

    assert target_handler.data.month[month].target_minutes == 9000
    assert result.error is None


def test_should_output_day_target_for_given_days(target_handler: TargetHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        target_handler.data.day[date].target_minutes = 480

    result: CommandHandlerResult = handle_call(target_handler, dates=dates)

    for _ in dates:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_change_day_target_for_given_days(target_handler: TargetHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    time_arg: TimeArgument = TimeArgument(minutes=300, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(target_handler, dates=dates, arguments=[time_arg])

    for date in dates:
        assert target_handler.data.day[date].target_minutes == 300
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_change_month_target_for_given_months(target_handler: TargetHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    time_arg: TimeArgument = TimeArgument(minutes=8000, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(target_handler, dates=months, arguments=[time_arg])

    for month in months:
        assert target_handler.data.month[month].target_minutes == 8000
    assert result.error is None


def test_should_set_day_target_to_current_minutes_at_work(target_handler: TargetHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    target_handler.data.day[date].minutes_at_work = 270

    result: CommandHandlerResult = handle_call(target_handler, active_date=date, arguments=["current"])

    assert target_handler.data.day[date].target_minutes == 270
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(target_handler: TargetHandler):
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)
    arguments: list[Any] = [time_arg, time_arg]

    result: CommandHandlerResult = handle_call(target_handler, arguments=arguments)

    assert result.error is not None


def test_should_return_error_on_invalid_argument_value(target_handler: TargetHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(target_handler, active_date=date, mode=Mode.Month, arguments=["badvalue"])

    assert result.error is not None
