import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.common import TimeArgument, TimeArgumentType
from work_tracker.command.macro_manager import MacroManager, MacroTemplate
from work_tracker.common import Date


@pytest.fixture(autouse=True)
def isolate_macro_state(mocker: MockerFixture):
    _ = MacroManager.macros  # ensure manager is initialized before test
    original_macros: dict = dict(MacroManager._macros)
    mocker.patch.object(MacroManager, "save_macros_file")  # do not save to file during tests
    yield  # run test
    MacroManager._macros = original_macros


@pytest.mark.order(1)
def test_init(internal_macro_handler):
    assert internal_macro_handler is not None


def test_should_expand_no_argument_macro_and_return_execute_after_queries(internal_macro_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["mymacro"] = MacroTemplate(
        identifier="mymacro",
        raw="mymacro | remote",
        command_text="remote",
        arguments=[],
        default_argument_values=[],
    )

    result: CommandHandlerResult = handle_call(internal_macro_handler, active_date=date, arguments=["mymacro"])

    assert result.execute_after is not None
    assert len(result.execute_after) > 0
    assert result.error is None


def test_should_substitute_required_argument_into_macro(internal_macro_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["mymacro"] = MacroTemplate(
        identifier="mymacro",
        raw="mymacro <arg> | <arg>",
        command_text="<arg>",
        arguments=["arg"],
        default_argument_values=[None],
    )

    result: CommandHandlerResult = handle_call(internal_macro_handler, active_date=date, arguments=["mymacro", "remote"])

    assert result.execute_after is not None
    assert len(result.execute_after) > 0
    assert result.error is None


def test_should_use_default_argument_when_not_provided(internal_macro_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["mymacro"] = MacroTemplate(
        identifier="mymacro",
        raw="mymacro <arg=remote> | <arg>",
        command_text="<arg>",
        arguments=["arg"],
        default_argument_values=["remote"],
    )

    result: CommandHandlerResult = handle_call(internal_macro_handler, active_date=date, arguments=["mymacro"])

    assert result.execute_after is not None
    assert len(result.execute_after) > 0
    assert result.error is None


def test_should_override_default_argument_when_provided(internal_macro_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["mymacro"] = MacroTemplate(
        identifier="mymacro",
        raw="mymacro <arg=remote> | <arg>",
        command_text="<arg>",
        arguments=["arg"],
        default_argument_values=["remote"],
    )

    result: CommandHandlerResult = handle_call(internal_macro_handler, active_date=date, arguments=["mymacro", "office"])

    assert result.execute_after is not None
    assert len(result.execute_after) > 0
    assert result.error is None


def test_should_substitute_time_argument_into_macro(internal_macro_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["workmacro"] = MacroTemplate(
        identifier="workmacro",
        raw="workmacro <time> | <time>",
        command_text="<time>",
        arguments=["time"],
        default_argument_values=[None],
    )
    time_arg: TimeArgument = TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)

    result: CommandHandlerResult = handle_call(internal_macro_handler, active_date=date, arguments=["workmacro", time_arg])

    assert result.execute_after is not None
    assert len(result.execute_after) > 0
    assert result.error is None


def test_should_return_error_on_no_arguments(internal_macro_handler):
    result: CommandHandlerResult = handle_call(internal_macro_handler, arguments=[])

    assert result.error is not None


def test_should_return_error_when_too_many_arguments_provided(internal_macro_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["noargsmacro"] = MacroTemplate(
        identifier="noargsmacro",
        raw="noargsmacro | remote",
        command_text="remote",
        arguments=[],
        default_argument_values=[],
    )

    result: CommandHandlerResult = handle_call(internal_macro_handler, active_date=date, arguments=["noargsmacro", "extra"])

    assert result.error is not None


def test_should_return_error_when_required_argument_is_missing(internal_macro_handler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["requiredmacro"] = MacroTemplate(
        identifier="requiredmacro",
        raw="requiredmacro <arg> | <arg>",
        command_text="<arg>",
        arguments=["arg"],
        default_argument_values=[None],  # required, no default
    )

    result: CommandHandlerResult = handle_call(internal_macro_handler, active_date=date, arguments=["requiredmacro"])

    assert result.error is not None


def test_should_forward_explicit_dates_to_execute_after_queries(internal_macro_handler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]
    MacroManager._macros["mymacro"] = MacroTemplate(
        identifier="mymacro",
        raw="mymacro | remote",
        command_text="remote",
        arguments=[],
        default_argument_values=[],
    )

    result: CommandHandlerResult = handle_call(internal_macro_handler, dates=dates, arguments=["mymacro"])

    assert result.execute_after is not None
    assert len(result.execute_after) > 0
    assert result.execute_after[0].dates == dates
    assert result.error is None
