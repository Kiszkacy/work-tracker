
import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.minutes import MinutesHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(minutes_handler: MinutesHandler):
    assert minutes_handler is not None


def test_should_output_minutes_per_day_for_active_date(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    minutes_handler.data.month[date.to_month_date()].target_minutes = 9600

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=[10])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_output_minutes_per_day_for_given_months(minutes_handler: MinutesHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        minutes_handler.data.month[month].target_minutes = 9600

    result: CommandHandlerResult = handle_call(minutes_handler, dates=months, arguments=[10])

    for _ in months:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_office_minutes_per_day(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    minutes_handler.data.month[date.to_month_date()].target_minutes = 9600
    minutes_handler.data.month[date.to_month_date()].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=["office", 10])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_remote_minutes_per_day(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    minutes_handler.data.month[date.to_month_date()].target_minutes = 9600
    minutes_handler.data.month[date.to_month_date()].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=["remote", 10])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_clean_minutes_excluding_already_filled_dates(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    minutes_handler.data.month[date.to_month_date()].target_minutes = 9600

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=[10, "clean"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_office_clean_minutes(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    minutes_handler.data.month[date.to_month_date()].target_minutes = 9600
    minutes_handler.data.month[date.to_month_date()].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=["office", 10, "clean"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_invalid_argument_count_zero(minutes_handler: MinutesHandler):
    result: CommandHandlerResult = handle_call(minutes_handler)

    assert result.error is not None


def test_should_return_error_on_nonpositive_days(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=[0])

    assert result.error is not None


def test_should_return_error_on_negative_days(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=[-5])

    assert result.error is not None


def test_should_return_error_on_invalid_location_argument(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=["invalid", 10])

    assert result.error is not None


def test_should_return_error_on_invalid_clean_argument(minutes_handler: MinutesHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(minutes_handler, active_date=date, arguments=[10, "invalid"])

    assert result.error is not None
