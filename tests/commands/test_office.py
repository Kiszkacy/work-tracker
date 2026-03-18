from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.office import OfficeHandler
from work_tracker.common import Date, DayType, WorkLocation


@pytest.mark.order(1)
def test_init(office_handler: OfficeHandler):
    assert office_handler is not None


def test_should_set_to_office_active_day(office_handler: OfficeHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    office_handler.data.day[date].work_location = WorkLocation.REMOTE

    result: CommandHandlerResult = handle_call(office_handler, active_date=date)

    assert office_handler.data.day[date].work_location == WorkLocation.OFFICE
    assert result.error is None


def test_should_set_to_office_active_month_workdays(office_handler: OfficeHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    for day in month.days_in_a_month():
        office_handler.data.day[day].work_location = WorkLocation.REMOTE

    result: CommandHandlerResult = handle_call(office_handler, active_date=month)

    for day in [day for day in month.days_in_a_month() if office_handler.data.day[day].day_type == DayType.WORKDAY]:
        assert office_handler.data.day[day].work_location == WorkLocation.OFFICE
    for day in [day for day in month.days_in_a_month() if office_handler.data.day[day].day_type != DayType.WORKDAY]:
        assert office_handler.data.day[day].work_location != WorkLocation.OFFICE
    assert result.error is None


def test_should_set_to_office_given_days(office_handler: OfficeHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    for date in dates:
        office_handler.data.day[date].work_location = WorkLocation.REMOTE

    result: CommandHandlerResult = handle_call(office_handler, dates=dates)

    for date in dates:
        assert office_handler.data.day[date].work_location == WorkLocation.OFFICE
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_set_to_office_given_months_workdays(office_handler: OfficeHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        for day in month.days_in_a_month():
            office_handler.data.day[day].work_location = WorkLocation.REMOTE

    result: CommandHandlerResult = handle_call(office_handler, dates=months)

    for month in months:
        for day in [day for day in month.days_in_a_month() if office_handler.data.day[day].day_type == DayType.WORKDAY]:
            assert office_handler.data.day[day].work_location == WorkLocation.OFFICE
        for day in [day for day in month.days_in_a_month() if office_handler.data.day[day].day_type != DayType.WORKDAY]:
            assert office_handler.data.day[day].work_location != WorkLocation.OFFICE
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(office_handler: OfficeHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(office_handler, arguments=arguments)

    assert result.error is not None
