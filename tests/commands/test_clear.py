import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.clear import ClearHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(clear_handler: ClearHandler):
    assert clear_handler is not None


def test_should_clear_active_day(clear_handler: ClearHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    clear_handler.data.day[date].minutes_at_work = 1 # TODO this theoretically should be enough to check if date was cleared/resetted

    result: CommandHandlerResult = handle_call(clear_handler, active_date=date)

    assert clear_handler.data.day[date].minutes_at_work == 0
    assert result.error is None


def test_should_clear_active_month(clear_handler: ClearHandler, random_date: Date):
    month: Date = random_date.to_month_date()

    for day in month.days_in_a_month():
        clear_handler.data.day[day].minutes_at_work = 1

    result: CommandHandlerResult = handle_call(clear_handler, active_date=month)

    for day in month.days_in_a_month():
        assert clear_handler.data.day[day].minutes_at_work == 0
    assert result.error is None


def test_should_clear_given_days(clear_handler: ClearHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]

    for date in dates:
        clear_handler.data.day[date].minutes_at_work = 1

    result: CommandHandlerResult = handle_call(clear_handler, dates=dates)

    for date in dates:
        assert clear_handler.data.day[date].minutes_at_work == 0
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_clear_given_months(clear_handler: ClearHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]

    for month in months:
        for day in month.days_in_a_month():
            clear_handler.data.day[day].minutes_at_work = 1

    result: CommandHandlerResult = handle_call(clear_handler, dates=months)

    for month in months:
        for day in month.days_in_a_month():
            assert clear_handler.data.day[day].minutes_at_work == 0
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(clear_handler: ClearHandler):
    arguments: list[any] = ["value"]

    result: CommandHandlerResult = handle_call(clear_handler, arguments=arguments)

    assert result.error is not None
