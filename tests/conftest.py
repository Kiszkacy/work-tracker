import datetime
import random
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from work_tracker.command.command_handler import CommandHandler, CommandHandlerResult
from work_tracker.command.command_history import CommandHistoryEntry
from work_tracker.command.commands.clear import ClearHandler
from work_tracker.command.commands.fte import FteHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import AppData, Date, Mode, ReadonlyAppState, classproperty
from work_tracker.text.input_output_handler import InputOutputHandler


class TestInputOutput:
    _text: str = ""
    _input_queue: list[str] = [] # TODO change to proper queue structure
    _output_queue: list[str] = []

    @classmethod
    def reset_text(cls):
        cls._text = ""

    @classproperty
    def text(cls) -> str:
        return cls._text

    @classmethod
    def write(cls, text: str):
        cls._text += text

    @classmethod
    def output(cls, text: str):
        cls.write(text)
        cls._output_queue.append(cls._text)
        cls.reset_text()

    @classmethod
    def append_input(cls, text: str):
        cls._input_queue.append(text)

    @classmethod
    def get_input(cls) -> str | None:
        if len(cls._input_queue) == 0:
            return None
        return cls._input_queue.pop(0)

    @classmethod
    def get_output(cls) -> str | None:
        if len(cls._output_queue) == 0:
            return None
        return cls._output_queue.pop(0)


def mock_io(mocker: MockerFixture) -> InputOutputHandler:
    io_mock: MagicMock = mocker.patch("work_tracker.text.input_output_handler.InputOutputHandler", autospec=True)

    def mock_output(text: str = "", end: str = "\n", *args, **kwargs):
        TestInputOutput.output(f"{text}{end}")

    def mock_write(text: str = "", end: str = "\n", *args, **kwargs):
        TestInputOutput.write(f"{text}{end}")

    io_mock.output.side_effect = mock_output
    io_mock.write.side_effect = mock_write

    return io_mock


def mock_data(mocker: MockerFixture) -> AppData:
    return mocker.patch("work_tracker.common.WorkData", autospec=True)


def sample_data() -> AppData:
    return AppData(
        country_code="PL"
    )


def generate_date() -> Date:
    start_date: datetime.date = datetime.date(1952, 1, 1)
    end_date: datetime.date = datetime.date(2049, 12, 31)
    day_offset: int = random.randint(0, (end_date - start_date).days)
    return Date.from_datetime(start_date + datetime.timedelta(days=day_offset))


def handle_call(
    handler: CommandHandler,
    dates: list[Date] = None,
    arguments: list[CommandArgument] = None,
    active_date: Date = None,
    mode: Mode = None,
    states: list[CommandHistoryEntry] = None,
    current_state_index: int = None
) -> CommandHandlerResult:
    dates = dates or []
    arguments = arguments or []
    if active_date is None and mode is None:
        active_date = generate_date().to_day_date()
        mode = Mode.Today
    elif active_date is not None and mode is None:
        if active_date.is_day_date():
            mode = Mode.Day
        elif active_date.is_month_date():
            mode = Mode.Month
    elif active_date is None and mode is not None:
        match mode:
            case Mode.Today | Mode.Day:
                active_date = generate_date().to_day_date()
            case Mode.Month:
                active_date = generate_date().to_month_date()
    states = states or []
    current_state_index = current_state_index or 0

    result: CommandHandlerResult = handler.handle(
        dates=dates,
        date_count=len(dates),
        arguments=arguments,
        argument_count=len(arguments),
        state=ReadonlyAppState(
            active_date=active_date,
            mode=mode,
            states=tuple(states),
            current_state_index=current_state_index
        )
    )

    return result


@pytest.fixture(scope="function")
def random_date() -> Date:
    return generate_date()


@pytest.fixture(scope="function")
def random_dates(request) -> list[Date]:
    params: dict[str, any]
    if not hasattr(request, "param"):
        params = {}
    else:
        params = request.param if isinstance(request.param, dict) else {}
    count: int = params.get("count", 5) # default count = 5
    unique_month_data: bool = params.get("unique_month_data", False)

    dates: list[Date] = []
    seen_month_years: set[tuple[int, int]] = set()
    for _ in range(count):
        while True:
            date: Date = generate_date()
            if unique_month_data:
                month_year: tuple[int, int] = (date.year, date.month)
                if month_year in seen_month_years:
                    continue
                seen_month_years.add(month_year)
            elif date in dates:
                continue
            break

        dates.append(date)

    return dates


@pytest.fixture(scope="function")
def clear_handler(mocker: MockerFixture) -> ClearHandler:
    return ClearHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


@pytest.fixture(scope="function")
def fte_handler(mocker: MockerFixture) -> FteHandler:
    return FteHandler(
        work_data=sample_data(),
        io=mock_io(mocker)
    )


