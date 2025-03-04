from __future__ import annotations

import difflib
from abc import ABC, abstractmethod
from dataclasses import dataclass

from work_tracker.command.command_manager import CommandManager
from work_tracker.command.common import Command
from .common import Date, Mode, classproperty


class VersionCheckError(Exception):
    pass


@dataclass(frozen=True)
class CommandError(ABC):
    command_name: str

    @classproperty
    def message(self) -> str:
        raise NotImplementedError()


@dataclass(frozen=True)
class CommandErrorInvalidArgumentCount(CommandError):
    received_argument_count: int

    @property
    def message(self) -> str:
        expected_counts: list[int] = sorted({len(args) for args in CommandManager.get_command_by_name(self.command_name).valid_argument_types})
        formatted_counts: str = ', '.join(map(str, expected_counts[:-1])) + ((' or ' if len(expected_counts) > 1 else '') + str(expected_counts[-1]))
        return f"invalid amount of arguments, received {self.received_argument_count} while '{self.command_name}' expects {formatted_counts}."


@dataclass(frozen=True)
class CommandErrorInvalidArgumentType(CommandError):
    received_type: str
    expected_type: str

    @property
    def message(self) -> str:
        return f"invalid argument type, received {self.received_type} while {self.expected_type} was expected."


@dataclass(frozen=True)
class CommandErrorInvalidArgumentValue(CommandError):
    received_value: str
    expected_value: str | list[str]

    @property
    def message(self) -> str:
        expected_value: str = self.expected_value if not isinstance(self.expected_value, list) else f"one of ({', '.join(self.expected_value)})"
        return f"invalid argument value, received {self.received_value} expected {expected_value}."


@dataclass(frozen=True)
class CommandErrorInvalidDate(CommandError):
    received_date: Date

    @property
    def message(self) -> str:
        return f"invalid date type, received {self.received_date}."


@dataclass(frozen=True)
class CommandErrorInvalidDateCount(CommandError):
    received_date_count: int
    expected_date_count: int

    @property
    def message(self) -> str:
        return f"invalid date count, received {self.received_date_count} expected {self.expected_date_count}."


@dataclass(frozen=True)
class CommandErrorInvalidMode(CommandError):
    mode: Mode
    supported_modes: set[Mode] = None

    @property
    def message(self) -> str:
        command: Command = CommandManager.get_command_by_name(self.command_name)
        supported_modes: list[Mode] = list(command.supported_modes) if self.supported_modes is None or len(self.supported_modes) == 0 else list(self.supported_modes)
        supported_modes.sort(key=lambda mode: mode.name)

        if len(supported_modes) == 1:
            supported_modes_text: str = f"'{supported_modes[0].name}' mode"
        else:
            supported_modes_text: str = ", ".join(f"'{mode.name}'" for mode in supported_modes[:-1]) + f" and '{supported_modes[-1].name}' modes"

        return f"invalid mode in which command was called, this '{self.command_name}' command execution supports only {supported_modes_text} but currently in '{self.mode.name}' mode."


@dataclass(frozen=True)
class CommandErrorNotImplemented(CommandError):

    @property
    def message(self) -> str:
        return f"command '{self.command_name}' is not yet implemented."


@dataclass(frozen=True)
class CommandErrorCustom(CommandError):
    custom_message: str

    @property
    def message(self) -> str:
        return self.custom_message


@dataclass(frozen=True)
class ParserError(ABC):
    # TODO implement this in the near future
    # raw_text: str
    # error_start_index: int
    # error_end_index: int

    @classproperty
    def message(self) -> str:
        # return f"{self.raw_text}\n{' '*self.error_start_index + '^'*(self.error_end_index-self.error_start_index)}"
        raise NotImplementedError()


@dataclass(frozen=True)
class ParserErrorMultipleDates(ParserError):
    @property
    def message(self) -> str:
        return f"multiple dates were provided without any command. To change the active date, provide only one."


@dataclass(frozen=True)
class ParserErrorInvalidArgumentCount(ParserError):
    command: Command
    received_amount: int

    @property
    def message(self) -> str:
        expected_counts: list[int] = sorted({len(args) for args in self.command.valid_argument_types})
        formatted_counts: str = ', '.join(map(str, expected_counts[:-1])) + ((' or ' if len(expected_counts) > 1 else '') + str(expected_counts[-1]))
        return f"invalid amount of arguments, received {self.received_amount} while command '{self.command.name}' expects {formatted_counts}."


@dataclass(frozen=True)
class ParserErrorInvalidArgumentTypes(ParserError):
    command: Command
    received_types: list[type]

    @property
    def message(self) -> str:
        valid_types: list[str] = [
            self._format_type_list(args) for args in self.command.valid_argument_types
            if len(args) == len(self.received_types)
        ]
        formatted_types: str = ', '.join(valid_types[:-1]) + ((' or ' if len(valid_types) > 1 else '') + str(valid_types[-1]))

        return f"invalid argument types, received {self._format_type_list(self.received_types)} while command '{self.command.name}' expects {formatted_types}."

    @staticmethod
    def _format_type_list(types: list[type]) -> str:
        if len(types) == 1:
            return types[0].__name__
        else:
            return f"({', '.join(type_.__name__ for type_ in types)})"


@dataclass(frozen=True)
class ParserErrorUnknownCommand(ParserError):
    received_name: str

    @property
    def message(self) -> str:
        command_names: list[str] = list([command.name for command in CommandManager.commands])
        closest_matches: list[str] = difflib.get_close_matches(self.received_name, command_names, n=1, cutoff=0.6)

        if len(closest_matches) != 0:
            return f"unknown command '{self.received_name}'. Did you mean '{closest_matches[0]}'?"
        else:
            return f"unknown command '{self.received_name}'."
