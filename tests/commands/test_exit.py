import pytest

from tests.conftest import handle_call
from work_tracker.command.commands.exit import ExitHandler
from work_tracker.common import Date, Mode


@pytest.mark.order(1)
def test_init(exit_handler: ExitHandler):
    assert exit_handler is not None


def test_should_exit_app_in_today_mode(exit_handler: ExitHandler, mocker):
    mock_exit = mocker.patch("sys.exit")
    mocker.patch("work_tracker.command.commands.exit.CheckpointManager.save")

    _ = handle_call(exit_handler, mode=Mode.Today)

    mock_exit.assert_called_once()


def test_should_change_to_today_if_not_in_today_mode(exit_handler: ExitHandler, random_date: Date, mocker):
    mock_exit = mocker.patch("sys.exit")
    date: Date = random_date.to_day_date()
        
    result = handle_call(exit_handler, active_date=date, mode=Mode.Day)

    mock_exit.assert_not_called()
    assert result.change_active_date == Date.today()
    assert result.error is None
