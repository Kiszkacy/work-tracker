import pytest
from pytest_mock import MockerFixture

from tests.conftest import handle_call, TestInputOutput
from work_tracker.checkpoint_manager import CheckpointManager, CheckpointTemplate
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.checkpoint import CheckpointHandler
from work_tracker.common import Date
from path import Path


@pytest.fixture()
def fake_checkpoint() -> CheckpointTemplate:
    return CheckpointTemplate(
        path=Path("."),
        full_identifier="user.test-checkpoint__2026-03-18_11-00-00",
        name="user.test-checkpoint",
        date="2026-03-18_11-00-00",
        persistent=True,
    )


@pytest.mark.order(1)
def test_init(checkpoint_handler: CheckpointHandler):
    assert checkpoint_handler is not None


def test_should_output_no_checkpoints_message_when_empty(checkpoint_handler: CheckpointHandler, mocker: MockerFixture, random_date: Date):
    date: Date = random_date.to_day_date()
    mocker.patch.object(CheckpointManager, "checkpoints", return_value=[])

    result: CommandHandlerResult = handle_call(checkpoint_handler, active_date=date)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert result.error is None


def test_should_output_checkpoint_list_when_checkpoints_exist(
    checkpoint_handler: CheckpointHandler,
    mocker: MockerFixture,
    random_date: Date,
    fake_checkpoint: CheckpointTemplate,
):
    date: Date = random_date.to_day_date()
    mocker.patch.object(CheckpointManager, "checkpoints", return_value=[fake_checkpoint])
    mocker.patch("os.path.getctime", return_value=0.0)

    result: CommandHandlerResult = handle_call(checkpoint_handler, active_date=date)

    output: str = TestInputOutput.get_output()
    assert output is not None
    assert "test-checkpoint" in output
    assert result.error is None


def test_should_create_temporary_checkpoint(checkpoint_handler: CheckpointHandler, mocker: MockerFixture, random_date: Date):
    date: Date = random_date.to_day_date()
    mock_save = mocker.patch.object(CheckpointManager, "save")

    result: CommandHandlerResult = handle_call(checkpoint_handler, active_date=date, arguments=["mycheckpoint"])

    mock_save.assert_called_once()
    assert result.error is None


def test_should_create_permanent_checkpoint(checkpoint_handler: CheckpointHandler, mocker: MockerFixture, random_date: Date):
    date: Date = random_date.to_day_date()
    mock_save = mocker.patch.object(CheckpointManager, "save")

    result: CommandHandlerResult = handle_call(checkpoint_handler, active_date=date, arguments=["mycheckpoint", "permanent"])

    mock_save.assert_called_once()
    _, kwargs = mock_save.call_args
    assert kwargs.get("persistent_checkpoint") is True
    assert result.error is None


def test_should_return_error_on_invalid_permanent_argument(checkpoint_handler: CheckpointHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(checkpoint_handler, active_date=date, arguments=["mycheckpoint", "invalidargument"])

    assert result.error is not None


def test_should_return_error_on_too_many_arguments(checkpoint_handler: CheckpointHandler):
    result: CommandHandlerResult = handle_call(checkpoint_handler, arguments=["test-checkpoint", "permanent", "extra"])

    assert result.error is not None


def test_should_return_error_on_invalid_date_count(checkpoint_handler: CheckpointHandler, random_date: Date):
    date: Date = random_date.to_day_date()

    result: CommandHandlerResult = handle_call(checkpoint_handler, dates=[date])

    assert result.error is not None
