import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call, TestInputOutput
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.config import ConfigHandler
from work_tracker.config import Config, MainConfig
from work_tracker.common import Date


@pytest.fixture(autouse=True)
def isolate_config_state(mocker: MockerFixture):
    _ = Config.data # lazy-load config
    original_config: MainConfig = Config._data.model_copy()
    mocker.patch.object(Config, "save") # do not save to file during tests
    yield # run test
    Config._data = original_config


@pytest.mark.order(1)
def test_init(config_handler: ConfigHandler):
    assert config_handler is not None


def test_should_output_all_config_fields(config_handler: ConfigHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(config_handler, active_date=date)

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_output_specific_config_field(config_handler: ConfigHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(config_handler, active_date=date, arguments=["output.max_width"])

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert str(Config.data.output.max_width) in output
    assert result.error is None


def test_should_output_message_for_nonexistent_field(config_handler: ConfigHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(config_handler, active_date=date, arguments=["nonexistent.field"])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_update_config_field(config_handler: ConfigHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    original_value: int = Config.data.output.max_width
    new_value: int = original_value + 10

    result: CommandHandlerResult = handle_call(config_handler, active_date=date, arguments=["output.max_width", new_value])

    assert Config.data.output.max_width == new_value
    assert result.error is None


def test_should_not_update_version_field(config_handler: ConfigHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(config_handler, active_date=date, arguments=["version", 999])

    assert TestInputOutput.get_output() is not None
    assert result.error is None


def test_should_return_error_on_too_many_arguments(config_handler: ConfigHandler):
    result: CommandHandlerResult = handle_call(config_handler, arguments=["field", "value", "extra"])

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(config_handler: ConfigHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(config_handler, dates=[date])

    assert result.error is not None
