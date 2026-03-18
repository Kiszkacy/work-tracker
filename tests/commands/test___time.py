import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.common import TimeArgument, TimeArgumentType
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(internal_time_handler):
    assert internal_time_handler is not None


def test_should_overwrite_minutes_at_work_for_active_day(internal_time_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    internal_time_handler.data.day[date].minutes_at_work = 100
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=date, arguments=[time_arg])

    assert internal_time_handler.data.day[date].minutes_at_work == 480
    assert result.error is None


def test_should_add_to_minutes_at_work_for_active_day(internal_time_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    internal_time_handler.data.day[date].minutes_at_work = 100
    time_arg: TimeArgument = TimeArgument(minutes=60, type=TimeArgumentType.Add)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=date, arguments=[time_arg])

    assert internal_time_handler.data.day[date].minutes_at_work == 160
    assert result.error is None


def test_should_subtract_from_minutes_at_work_for_active_day(internal_time_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    internal_time_handler.data.day[date].minutes_at_work = 200
    time_arg: TimeArgument = TimeArgument(minutes=60, type=TimeArgumentType.Subtract)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=date, arguments=[time_arg])

    assert internal_time_handler.data.day[date].minutes_at_work == 140
    assert result.error is None


def test_should_update_day_target_when_minutes_exceed_target(internal_time_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    internal_time_handler.data.day[date].target_minutes = 480
    internal_time_handler.data.day[date].minutes_at_work = 0
    time_arg: TimeArgument = TimeArgument(minutes=600, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=date, arguments=[time_arg])

    assert internal_time_handler.data.day[date].minutes_at_work == 600
    assert internal_time_handler.data.day[date].target_minutes == 600
    assert result.error is None


def test_should_keep_day_target_tracking_minutes_when_they_were_equal(internal_time_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    internal_time_handler.data.day[date].target_minutes = 480
    internal_time_handler.data.day[date].minutes_at_work = 480
    time_arg: TimeArgument = TimeArgument(minutes=300, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=date, arguments=[time_arg])

    assert internal_time_handler.data.day[date].minutes_at_work == 300
    assert internal_time_handler.data.day[date].target_minutes == 300
    assert result.error is None


def test_should_not_update_day_target_when_below_target(internal_time_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    internal_time_handler.data.day[date].target_minutes = 480
    internal_time_handler.data.day[date].minutes_at_work = 0
    time_arg: TimeArgument = TimeArgument(minutes=300, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=date, arguments=[time_arg])

    assert internal_time_handler.data.day[date].minutes_at_work == 300
    assert internal_time_handler.data.day[date].target_minutes == 480
    assert result.error is None


def test_should_update_month_target_minutes(internal_time_handler, random_date: Date):
    month: Date = random_date.to_month_date()
    internal_time_handler.data.month[month].target_minutes = 9600
    time_arg: TimeArgument = TimeArgument(minutes=4800, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=month, arguments=[time_arg])

    assert internal_time_handler.data.month[month].target_minutes == 4800
    assert result.error is None


def test_should_add_to_month_target_minutes(internal_time_handler, random_date: Date):
    month: Date = random_date.to_month_date()
    internal_time_handler.data.month[month].target_minutes = 9600
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Add)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=month, arguments=[time_arg])

    assert internal_time_handler.data.month[month].target_minutes == 10080
    assert result.error is None


def test_should_subtract_from_month_target_minutes(internal_time_handler, random_date: Date):
    month: Date = random_date.to_month_date()
    internal_time_handler.data.month[month].target_minutes = 9600
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Subtract)

    result: CommandHandlerResult = handle_call(internal_time_handler, active_date=month, arguments=[time_arg])

    assert internal_time_handler.data.month[month].target_minutes == 9120
    assert result.error is None


def test_should_overwrite_minutes_for_given_days(internal_time_handler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        internal_time_handler.data.day[date].minutes_at_work = 0
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, dates=dates, arguments=[time_arg])

    for date in dates:
        assert internal_time_handler.data.day[date].minutes_at_work == 480
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_overwrite_target_for_given_months(internal_time_handler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        internal_time_handler.data.month[month].target_minutes = 9600
    time_arg: TimeArgument = TimeArgument(minutes=4800, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, dates=months, arguments=[time_arg])

    for month in months:
        assert internal_time_handler.data.month[month].target_minutes == 4800
    assert result.error is None


def test_should_return_error_on_no_arguments(internal_time_handler):
    result: CommandHandlerResult = handle_call(internal_time_handler)

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(internal_time_handler):
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_time_handler, arguments=[time_arg, time_arg])

    assert result.error is not None
