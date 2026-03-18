from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.info import InfoHandler
from work_tracker.common import Date, AttendanceType, WorkLocation


@pytest.mark.order(1)
def test_init(info_handler: InfoHandler):
    assert info_handler is not None


def test_should_output_info_for_active_day(info_handler: InfoHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(info_handler, active_date=date)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_info_for_active_month(info_handler: InfoHandler, random_date: Date):
    month: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(info_handler, active_date=month)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_info_for_given_days(info_handler: InfoHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]

    result: CommandHandlerResult = handle_call(info_handler, dates=dates)

    for _ in dates:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_output_info_for_given_months(info_handler: InfoHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]

    result: CommandHandlerResult = handle_call(info_handler, dates=months)

    for _ in months:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_attendance_type_in_day_info(info_handler: InfoHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    info_handler.data.day[date].attendance_type = AttendanceType.ABSENCE

    result: CommandHandlerResult = handle_call(info_handler, active_date=date)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "absence" in output
    assert result.error is None


def test_should_output_work_location_in_day_info(info_handler: InfoHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    info_handler.data.day[date].work_location = WorkLocation.REMOTE

    result: CommandHandlerResult = handle_call(info_handler, active_date=date)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "remote" in output
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(info_handler: InfoHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(info_handler, arguments=arguments)

    assert result.error is not None
