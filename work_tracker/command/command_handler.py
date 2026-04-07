from abc import ABC, abstractmethod
from dataclasses import dataclass

from prompt_toolkit.completion import Completion
from work_tracker.command.command_parser import CommandParser
from work_tracker.command.common import CommandArgument, AdditionalInputArgument, CommandQuery, CompletionHint, CompletionCandidate
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

    @classmethod
    @abstractmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        raise NotImplementedError()
    
    @abstractmethod
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        raise NotImplementedError()

    @staticmethod
    def get_fitting_completions(candidates: list[CompletionCandidate], last_word: str) -> list[Completion | CompletionCandidate]:
        result: list[Completion | CompletionCandidate] = []
        for item in candidates:
            if isinstance(item.value, CompletionHint):
                result.append(item)
            elif isinstance(item.value, str) and item.value.lower().startswith(last_word.lower()):
                result.append(Completion(item.value, start_position=-len(last_word), display_meta=item.meta or ""))
        return result

    def enter_subcommand_mode(self):
        self.io.enter_subcommand_mode(self.command_name)

    def exit_subcommand_mode(self):
        self.io.exit_subcommand_mode()

    def get_additional_input(self, custom_autocomplete: list[str] = None) -> list[AdditionalInputArgument]:
        if not self.io.in_subcommand_mode:
            raise RuntimeError("Cannot get additional input when not in subcommand mode.")
        
        text: str = self.io.input(f"{Config.data.input.sub_prefix} ", custom_autocomplete=custom_autocomplete)
        return CommandParser.parse_arguments(text)
