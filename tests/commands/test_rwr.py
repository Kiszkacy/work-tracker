from fractions import Fraction
from typing import Any

import pytest

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.rwr import RwrHandler
from work_tracker.common import Date, Mode


@pytest.mark.order(1)
def test_init(rwr_handler: RwrHandler):
    assert rwr_handler is not None


def test_should_output_rwr_for_active_date(rwr_handler: RwrHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    rwr_handler.data.month[date.to_month_date()].remote_work_ratio = 0.4

    result: CommandHandlerResult = handle_call(rwr_handler, active_date=date)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert Fraction(0.4).limit_denominator().__str__() in output
    assert result.error is None


def test_should_output_office_only_when_rwr_is_zero(rwr_handler: RwrHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    rwr_handler.data.month[date.to_month_date()].remote_work_ratio = 0.0

    result: CommandHandlerResult = handle_call(rwr_handler, active_date=date)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "office only" in output
    assert result.error is None


def test_should_output_remote_only_when_rwr_is_one(rwr_handler: RwrHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    rwr_handler.data.month[date.to_month_date()].remote_work_ratio = 1.0

    result: CommandHandlerResult = handle_call(rwr_handler, active_date=date)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "remote only" in output
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_output_rwr_for_given_months(rwr_handler: RwrHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    for month in months:
        rwr_handler.data.month[month].remote_work_ratio = 0.5

    result: CommandHandlerResult = handle_call(rwr_handler, dates=months)

    for _ in months:
        assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_change_rwr_for_active_date_in_today_mode(rwr_handler: RwrHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    new_rwr: float = 0.6

    result: CommandHandlerResult = handle_call(rwr_handler, active_date=date, mode=Mode.Today, arguments=[new_rwr])

    assert rwr_handler.data.month[date.to_month_date()].remote_work_ratio == new_rwr
    assert result.error is None


def test_should_change_rwr_for_active_date_in_month_mode(rwr_handler: RwrHandler, random_date: Date):
    month: Date = random_date.to_month_date()
    new_rwr: float = 0.5

    result: CommandHandlerResult = handle_call(rwr_handler, active_date=month, mode=Mode.Month, arguments=[new_rwr])

    assert rwr_handler.data.month[month].remote_work_ratio == new_rwr
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_change_rwr_for_given_months(rwr_handler: RwrHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    new_rwr: float = 0.3

    result: CommandHandlerResult = handle_call(rwr_handler, dates=months, arguments=[new_rwr])

    for month in months:
        assert rwr_handler.data.month[month].remote_work_ratio == new_rwr
    assert result.error is None


def test_should_return_error_on_too_many_arguments(rwr_handler: RwrHandler):
    arguments: list[Any] = [0.4, 0.5]

    result: CommandHandlerResult = handle_call(rwr_handler, arguments=arguments)

    assert result.error is not None
