from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.done import DoneHandler
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(done_handler: DoneHandler):
    assert done_handler is not None


def test_should_set_minutes_at_work_to_target_for_active_day(done_handler: DoneHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    done_handler.data.day[date].target_minutes = 480
    done_handler.data.day[date].minutes_at_work = 0

    result: CommandHandlerResult = handle_call(done_handler, active_date=date)

    assert done_handler.data.day[date].minutes_at_work == 480
    assert result.error is None


def test_should_set_minutes_at_work_to_target_for_active_month(done_handler: DoneHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    for day in month.days_in_a_month():
        done_handler.data.day[day].target_minutes = 480
        done_handler.data.day[day].minutes_at_work = 0

    result: CommandHandlerResult = handle_call(done_handler, active_date=month)

    for day in month.days_in_a_month():
        assert done_handler.data.day[day].minutes_at_work == done_handler.data.day[day].target_minutes
    assert result.error is None


def test_should_set_minutes_at_work_to_target_for_given_days(done_handler: DoneHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        done_handler.data.day[date].target_minutes = 480
        done_handler.data.day[date].minutes_at_work = 0

    result: CommandHandlerResult = handle_call(done_handler, dates=dates)

    for date in dates:
        assert done_handler.data.day[date].minutes_at_work == 480
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_set_minutes_at_work_to_target_for_given_months(done_handler: DoneHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        for day in month.days_in_a_month():
            done_handler.data.day[day].target_minutes = 480
            done_handler.data.day[day].minutes_at_work = 0

    result: CommandHandlerResult = handle_call(done_handler, dates=months)

    for month in months:
        for day in month.days_in_a_month():
            assert done_handler.data.day[day].minutes_at_work == done_handler.data.day[day].target_minutes
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(done_handler: DoneHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(done_handler, arguments=arguments)

    assert result.error is not None
