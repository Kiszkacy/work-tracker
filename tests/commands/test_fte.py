from fractions import Fraction

import pytest

from tests.conftest import handle_call, mock_io, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.fte import FteHandler
from work_tracker.common import Date, Mode


@pytest.mark.order(1)
def test_init(fte_handler: FteHandler):
    assert fte_handler is not None


def test_should_output_active_date_month_fte(fte_handler: FteHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    starting_fte: float = 0.5
    fte_handler.data.month[date.to_month_date()].fte = starting_fte

    result: CommandHandlerResult = handle_call(fte_handler, active_date=date)

    assert fte_handler.data.month[date.to_month_date()].fte == starting_fte
    assert TestInputOutput.get_output().strip() == Fraction(starting_fte).limit_denominator().__str__()
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_output_given_months_fte(fte_handler: FteHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    fte_list: list[float] = [0.8, 0.6, 0.5, 0.4, 0.2]
    for month, fte in zip(months, fte_list):
        fte_handler.data.month[month].fte = fte

    result: CommandHandlerResult = handle_call(fte_handler, dates=months)

    for month, fte in zip(months, fte_list):
        assert fte_handler.data.month[month].fte == fte
        assert TestInputOutput.get_output().strip() == Fraction(fte).limit_denominator().__str__()
    assert result.error is None


def test_should_update_active_date_month_fte(fte_handler: FteHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    starting_fte: float = 0.5
    target_fte: float = 0.8
    fte_handler.data.month[date.to_month_date()].fte = starting_fte

    result: CommandHandlerResult = handle_call(fte_handler, arguments=[target_fte], active_date=date, mode=Mode.Today)

    assert fte_handler.data.month[date.to_month_date()].fte == target_fte
    assert TestInputOutput.get_output() is None
    assert result.error is None


@pytest.mark.parametrize("random_dates", [{"unique_month_data": True}], indirect=True)
def test_should_update_given_months_fte(fte_handler: FteHandler, random_dates: list[Date]):
    months: list[Date] = [date.to_month_date() for date in random_dates]
    starting_fte_list: list[float] = [0.8, 0.6, 0.5, 0.4, 0.2]
    target_fte: float = 0.5
    for month, fte in zip(months, starting_fte_list):
        fte_handler.data.month[month].fte = fte

    result: CommandHandlerResult = handle_call(fte_handler, dates=months, arguments=[target_fte])

    for month in months:
        assert fte_handler.data.month[month].fte == target_fte
        assert TestInputOutput.get_output() is None
    assert result.error is None


def test_should_return_error_on_invalid_argument_count(fte_handler: FteHandler):
    arguments: list[any] = ["value", "value"]

    result: CommandHandlerResult = handle_call(fte_handler, arguments=arguments)

    assert result.error is not None
