import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.deletemacro import DeletemacroHandler
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
def test_init(deletemacro_handler: DeletemacroHandler):
    assert deletemacro_handler is not None


def test_should_delete_existing_macro(deletemacro_handler: DeletemacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    MacroManager._macros["todelete"] = MacroTemplate(
        identifier="todelete",
        raw="todelete | remote",
        command_text="remote",
        arguments=[],
        default_argument_values=[],
    )

    result: CommandHandlerResult = handle_call(deletemacro_handler, active_date=date, arguments=["todelete"])

    assert "todelete" not in MacroManager.macros
    assert result.error is None


def test_should_output_message_when_macro_not_found(deletemacro_handler: DeletemacroHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(deletemacro_handler, active_date=date, arguments=["nonexistent"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_no_arguments(deletemacro_handler: DeletemacroHandler):
    result: CommandHandlerResult = handle_call(deletemacro_handler)

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(deletemacro_handler: DeletemacroHandler):
    result: CommandHandlerResult = handle_call(deletemacro_handler, arguments=["macro1", "macro2"])

    assert result.error is not None
