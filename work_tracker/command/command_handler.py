from abc import ABC, abstractmethod
from dataclasses import dataclass

from work_tracker.command.command_parser import CommandParser
from work_tracker.command.common import CommandArgument, AdditionalInputArgument, CommandQuery
from work_tracker.error import CommandError
from work_tracker.common import AppData, Date, ReadonlyAppState
from work_tracker.config import Config
from work_tracker.text.input_output_handler import InputOutputHandler


@dataclass(frozen=True)
class CommandHandlerResult:
    undoable: bool
    error: CommandError | None = None
    change_active_date: Date | None = None
    change_state_by: int | None = None
    execute_after: list[CommandQuery] | None = None


class CommandHandler(ABC):
    def __init__(self, work_data: AppData, io: InputOutputHandler):
        self.data: AppData = work_data
        self.io: InputOutputHandler = io

    @property
    def command_name(self) -> str:
        return self.__class__.__name__.split("Handler")[0].lower()

    @abstractmethod
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        raise NotImplementedError()

    def get_additional_input(self, custom_autocomplete: list[str] = None) -> list[AdditionalInputArgument]:
        text: str = self.io.input(f"{Config.data.input.sub_prefix} ", show_autocomplete=custom_autocomplete is not None, custom_autocomplete=custom_autocomplete)
        return CommandParser.parse_arguments(text)
