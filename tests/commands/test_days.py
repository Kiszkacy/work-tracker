import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.days import DaysHandler
from work_tracker.command.common import TimeArgument, TimeArgumentType
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(days_handler: DaysHandler):
    assert days_handler is not None


def test_should_output_days_count_for_active_date(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)
    days_handler.data.month[date.to_month_date()].target_minutes = 9600

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=[time_arg])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_output_days_count_for_given_months(days_handler: DaysHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)
    for month in months:
        days_handler.data.month[month].target_minutes = 9600

    result: CommandHandlerResult = handle_call(days_handler, dates=months, arguments=[time_arg])

    for _ in months:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_office_days_count(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)
    days_handler.data.month[date.to_month_date()].target_minutes = 9600
    days_handler.data.month[date.to_month_date()].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=["office", time_arg])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_remote_days_count(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)
    days_handler.data.month[date.to_month_date()].target_minutes = 9600
    days_handler.data.month[date.to_month_date()].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=["remote", time_arg])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_clean_days_count_excluding_filled_dates(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)
    days_handler.data.month[date.to_month_date()].target_minutes = 9600

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=[time_arg, "clean"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_office_clean_days_count(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)
    days_handler.data.month[date.to_month_date()].target_minutes = 9600
    days_handler.data.month[date.to_month_date()].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=["office", time_arg, "clean"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_no_arguments(days_handler: DaysHandler):
    result: CommandHandlerResult = handle_call(days_handler)

    assert result.error is not None


def test_should_return_error_on_zero_minutes(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    zero_time_arg: TimeArgument = TimeArgument(minutes=0, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=[zero_time_arg])

    assert result.error is not None


def test_should_return_error_on_invalid_location_argument(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=["invalid", time_arg])

    assert result.error is not None


def test_should_return_error_on_invalid_clean_argument(days_handler: DaysHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(days_handler, active_date=date, arguments=[time_arg, "invalid"])

    assert result.error is not None
