import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.deletealias import DeletealiasHandler
from work_tracker.command.alias_manager import AliasManager, AliasTemplate
from work_tracker.common import Date


@pytest.fixture(autouse=True)
def isolate_alias_state(mocker: MockerFixture):
    _ = AliasManager.aliases # lazy-load aliases
    original_aliases: dict = dict(AliasManager._aliases)
    mocker.patch.object(AliasManager, "save_aliases_file") # do not save to file during tests
    yield # run test
    AliasManager._aliases = original_aliases


@pytest.mark.order(1)
def test_init(deletealias_handler: DeletealiasHandler):
    assert deletealias_handler is not None


def test_should_delete_existing_alias(deletealias_handler: DeletealiasHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    AliasManager._aliases["todelete"] = AliasTemplate(
        identifier="todelete",
        raw="todelete | remote",
        replacement_text="remote",
    )

    result: CommandHandlerResult = handle_call(deletealias_handler, active_date=date, arguments=["todelete"])

    assert "todelete" not in AliasManager.aliases
    assert result.error is None


def test_should_output_message_when_alias_not_found(deletealias_handler: DeletealiasHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(deletealias_handler, active_date=date, arguments=["nonexistent"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_no_arguments(deletealias_handler: DeletealiasHandler):
    result: CommandHandlerResult = handle_call(deletealias_handler)

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(deletealias_handler: DeletealiasHandler):
    result: CommandHandlerResult = handle_call(deletealias_handler, arguments=["alias1", "alias2"])

    assert result.error is not None
