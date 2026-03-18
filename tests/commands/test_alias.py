import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.alias import AliasHandler
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
def test_init(alias_handler: AliasHandler):
    assert alias_handler is not None


def test_should_output_alias_list(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(alias_handler, active_date=date)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_specific_alias(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    test_alias: AliasTemplate = AliasTemplate(
        identifier="testalias",
        raw="testalias | remote",
        replacement_text="remote",
    )
    AliasManager._aliases["testalias"] = test_alias

    result: CommandHandlerResult = handle_call(alias_handler, active_date=date, arguments=["testalias"])

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "testalias" in output
    assert result.error is None


def test_should_output_message_for_nonexistent_alias(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(alias_handler, active_date=date, arguments=["nonexistentalias"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_create_new_alias(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(alias_handler, active_date=date, arguments=["myalias", "remote"])

    assert "myalias" in AliasManager.aliases
    assert AliasManager.aliases["myalias"].replacement_text == "remote"
    assert result.error is None


def test_should_update_existing_alias(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    AliasManager._aliases["myalias"] = AliasTemplate(
        identifier="myalias",
        raw="myalias | office",
        replacement_text="office",
    )

    result: CommandHandlerResult = handle_call(alias_handler, active_date=date, arguments=["myalias", "remote"])

    assert AliasManager.aliases["myalias"].replacement_text == "remote"
    assert result.error is None


def test_should_reject_reserved_identifier_alias(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(alias_handler, active_date=date, arguments=["alias", "remote"])

    assert "alias" not in AliasManager.aliases
    assert result.error is None


def test_should_reject_reserved_identifier_deletealias(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(alias_handler, active_date=date, arguments=["deletealias", "remote"])

    assert "deletealias" not in AliasManager.aliases
    assert result.error is None


def test_should_return_error_on_invalid_date_count(alias_handler: AliasHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(alias_handler, dates=[date])

    assert result.error is not None
