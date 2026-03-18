from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.remote import RemoteHandler
from work_tracker.common import Date, DayType, WorkLocation


@pytest.mark.order(1)
def test_init(remote_handler: RemoteHandler):
    assert remote_handler is not None


def test_should_set_to_remote_active_day(remote_handler: RemoteHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    remote_handler.data.day[date].work_location = WorkLocation.OFFICE

    result: CommandHandlerResult = handle_call(remote_handler, active_date=date)

    assert remote_handler.data.day[date].work_location == WorkLocation.REMOTE
    assert result.error is None


def test_should_set_to_remote_active_month_workdays(remote_handler: RemoteHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    for day in month.days_in_a_month():
        remote_handler.data.day[day].work_location = WorkLocation.OFFICE

    result: CommandHandlerResult = handle_call(remote_handler, active_date=month)

    for day in [day for day in month.days_in_a_month() if remote_handler.data.day[day].day_type == DayType.WORKDAY]:
        assert remote_handler.data.day[day].work_location == WorkLocation.REMOTE
    for day in [day for day in month.days_in_a_month() if remote_handler.data.day[day].day_type != DayType.WORKDAY]:
        assert remote_handler.data.day[day].work_location != WorkLocation.REMOTE
    assert result.error is None


def test_should_set_to_remote_given_days(remote_handler: RemoteHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        remote_handler.data.day[date].work_location = WorkLocation.OFFICE

    result: CommandHandlerResult = handle_call(remote_handler, dates=dates)

    for date in dates:
        assert remote_handler.data.day[date].work_location == WorkLocation.REMOTE
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_set_to_remote_given_months_workdays(remote_handler: RemoteHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        for day in month.days_in_a_month():
            remote_handler.data.day[day].work_location = WorkLocation.OFFICE

    result: CommandHandlerResult = handle_call(remote_handler, dates=months)

    for month in months:
        for day in [day for day in month.days_in_a_month() if remote_handler.data.day[day].day_type == DayType.WORKDAY]:
            assert remote_handler.data.day[day].work_location == WorkLocation.REMOTE
        for day in [day for day in month.days_in_a_month() if remote_handler.data.day[day].day_type != DayType.WORKDAY]:
            assert remote_handler.data.day[day].work_location != WorkLocation.REMOTE
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(remote_handler: RemoteHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(remote_handler, arguments=arguments)

    assert result.error is not None
