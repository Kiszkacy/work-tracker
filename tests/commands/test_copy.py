from typing import Any

import pytest

from tests.conftest import handle_call
from work_tracker.command.clipboard import Clipboard
from work_tracker.command.command_handler import CommandHandlerResult
from work_tracker.command.commands.copy import CopyHandler
from work_tracker.common import Date, Mode, WorkLocation, Time


@pytest.mark.order(1)
def test_init(copy_handler: CopyHandler):
    assert copy_handler is not None


def test_should_copy_active_day_data_to_clipboard(copy_handler: CopyHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    copy_handler.data.day[date].minutes_at_work = 420
    copy_handler.data.day[date].target_minutes = 480
    copy_handler.data.day[date].work_location = WorkLocation.REMOTE
    copy_handler.data.day[date].work_start = Time(minutes_since_midnight=8*60)
    copy_handler.data.day[date].work_end = Time(minutes_since_midnight=15*60)

    result: CommandHandlerResult = handle_call(copy_handler, active_date=date)

    assert result.error is None
    assert Clipboard.has(Clipboard.COPY_PASTE_KEY)
    clip = Clipboard.get(Clipboard.COPY_PASTE_KEY)
    assert clip.minutes_at_work == 420
    assert clip.target_minutes == 480
    assert clip.work_location == WorkLocation.REMOTE
    assert clip.work_start.minutes_since_midnight == 8*60
    assert clip.work_end.minutes_since_midnight == 15*60


def test_should_copy_explicit_day_date_to_clipboard(copy_handler: CopyHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    copy_handler.data.day[date].minutes_at_work = 300

    result: CommandHandlerResult = handle_call(copy_handler, dates=[date])

    assert result.error is None
    assert Clipboard.get(Clipboard.COPY_PASTE_KEY).minutes_at_work == 300


def test_clipboard_copy_is_a_snapshot_not_a_reference(copy_handler: CopyHandler, random_date: Date):
    date: Date = random_date.to_day_date()
    copy_handler.data.day[date].minutes_at_work = 100

    handle_call(copy_handler, active_date=date)
    copy_handler.data.day[date].minutes_at_work = 999

    assert Clipboard.get(Clipboard.COPY_PASTE_KEY).minutes_at_work == 100


def test_should_return_error_when_mode_is_month_and_no_date_given(copy_handler: CopyHandler, random_date: Date):
    month: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(copy_handler, active_date=month, mode=Mode.Month)

    assert result.error is not None
    assert not Clipboard.has(Clipboard.COPY_PASTE_KEY)


def test_should_return_error_when_date_is_a_month_date(copy_handler: CopyHandler, random_date: Date):
    month: Date = random_date.to_month_date()

    result: CommandHandlerResult = handle_call(copy_handler, dates=[month])

    assert result.error is not None


def test_should_return_error_when_more_than_one_date_given(copy_handler: CopyHandler, random_dates: list[Date]):
    dates: list[Date] = [date.to_day_date() for date in random_dates]

    result: CommandHandlerResult = handle_call(copy_handler, dates=dates)

    assert result.error is not None


def test_should_return_error_on_invalid_argument_count(copy_handler: CopyHandler):
    arguments: list[Any] = ["value"]

    result: CommandHandlerResult = handle_call(copy_handler, arguments=arguments)

    assert result.error is not None
