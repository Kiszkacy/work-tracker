import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.macro import MacroHandler
from work_tracker.command.macro_manager import MacroManager, MacroTemplate
from work_tracker.common import Date


@pytest.fixture(autouse=True)
def isolate_macro_state(mocker: MockerFixture):
    _ = MacroManager.macros # lazy-load macros
    original_macros: dict = dict(MacroManager._macros)
    mocker.patch.object(MacroManager, "save_macros_file") # do not save to file during tests
    yield # run test
    MacroManager._macros = original_macros


@pytest.mark.order(1)
def test_init(macro_handler: MacroHandler):
    assert macro_handler is not None


def test_should_output_macro_list(macro_handler: MacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(macro_handler, active_date=date)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_specific_macro(macro_handler: MacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["mymacro"] = MacroTemplate(
        identifier="mymacro",
        raw="mymacro | remote",
        command_text="remote",
        arguments=[],
        default_argument_values=[],
    )

    result: CommandHandlerResult = handle_call(macro_handler, active_date=date, arguments=["mymacro"])

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "mymacro" in output
    assert result.error is None


def test_should_output_message_for_nonexistent_macro(macro_handler: MacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(macro_handler, active_date=date, arguments=["nonexistentmacro"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_create_new_macro_without_arguments(macro_handler: MacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(macro_handler, active_date=date, arguments=["mymacro", "remote"])

    assert "mymacro" in MacroManager.macros
    assert MacroManager.macros["mymacro"].command_text == "remote"
    assert result.error is None


def test_should_create_new_macro_with_arguments(macro_handler: MacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(
        macro_handler, active_date=date,
        arguments=["mymacro", "<day>", "remote"]
    )

    assert "mymacro" in MacroManager.macros
    assert "day" in MacroManager.macros["mymacro"].arguments
    assert result.error is None


def test_should_update_existing_macro(macro_handler: MacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["mymacro"] = MacroTemplate(
        identifier="mymacro",
        raw="mymacro | remote",
        command_text="remote",
        arguments=[],
        default_argument_values=[],
    )

    result: CommandHandlerResult = handle_call(macro_handler, active_date=date, arguments=["mymacro", "office"])

    assert MacroManager.macros["mymacro"].command_text == "office"
    assert result.error is None


def test_should_return_error_on_invalid_date_count(macro_handler: MacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(macro_handler, dates=[date])

    assert result.error is not None
