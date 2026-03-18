from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.common import Date


@pytest.mark.order(1)
def test_init(internal_date_handler):
    assert internal_date_handler is not None


def test_should_change_active_date_to_given_day(internal_date_handler, random_date: Date):
    day: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[day])

    assert result.change_active_date is not None
    assert result.change_active_date.is_day_date()
    assert result.error is None


def test_should_change_active_date_to_given_month(internal_date_handler, random_date: Date):
    month: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[month])

    assert result.change_active_date is not None
    assert result.change_active_date.is_month_date()
    assert result.error is None


def test_should_preserve_day_value_of_given_date(internal_date_handler, random_date: Date):
    day: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[day])

    assert result.change_active_date.day == day.day
    assert result.error is None


def test_should_preserve_month_value_of_given_month_date(internal_date_handler, random_date: Date):
    month: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[month])

    assert result.change_active_date.month == month.month
    assert result.error is None


def test_should_fill_partial_day_with_active_date(internal_date_handler, random_date: Date):
    active: Date = random_date.to_day_date()
    partial_day: Date = Date(day=1)

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[partial_day], active_date=active)

    assert result.change_active_date is not None
    assert result.change_active_date.day == 1
    assert result.change_active_date.month == active.month
    assert result.change_active_date.year == active.year
    assert result.error is None


def test_should_fill_partial_month_with_active_date(internal_date_handler, random_date: Date):
    active: Date = random_date.to_day_date()
    partial_month: Date = Date(month=active.month)

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[partial_month], active_date=active)

    assert result.change_active_date is not None
    assert result.change_active_date.day is None
    assert result.change_active_date.month == active.month
    assert result.change_active_date.year == active.year
    assert result.error is None


def test_should_return_error_when_no_dates_given(internal_date_handler):
    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[])

    assert result.error is not None


def test_should_return_error_when_too_many_dates_given(internal_date_handler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=dates)

    assert result.error is not None


def test_should_return_error_on_invalid_argument_count(internal_date_handler, random_date: Date):
    day: Date = random_date.to_day_date()
    arguments: list[Any] = ["extra"]

    result: CommandHandlerResult = handle_call(internal_date_handler, dates=[day], arguments=arguments)

    assert result.error is not None
