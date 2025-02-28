import re
from dataclasses import dataclass
from pathlib import Path

from work_tracker.common import get_data_path, classproperty


@dataclass(frozen=True)
class MacroTemplate:
    identifier: str
    raw: str
    command_text: str
    arguments: list[str]
    default_argument_values: list[str]


__macro_version__: int = 1


class MacroManager:
    _macros: dict[str, MacroTemplate] = {}
    _initialized: bool = False

    @classproperty
    def macros(cls) -> dict[str, MacroTemplate]:
        cls._check_initialization()
        return cls._macros # TODO deepcopy

    @classproperty
    def iterable_macros(cls) -> list[MacroTemplate]:
        cls._check_initialization()
        return list(cls._macros.values())

    @classmethod
    def _check_initialization(cls):
        if not cls._initialized:
            if not cls._is_latest_macro_version():
                cls._update_macros_to_latest_version()
            cls._macros = cls._initialize_macros()
            cls._initialized = True

    @classmethod
    def _is_latest_macro_version(cls) -> bool:
        macro_path: Path = get_data_path().joinpath("macros.txt")
        with macro_path.open("r", encoding="utf-8") as file:
            version: int = int(next(file))

        return version == __macro_version__

    @classmethod
    def _update_macros_to_latest_version(cls):
        # just like data, update to target version step by step: A -> A+1 -> A+2 -> ... -> B
        # remember to save the file, after update !
        pass

    @classmethod
    def _initialize_macros(cls) -> dict[str, MacroTemplate]:
        macro_path: Path = get_data_path().joinpath("macros.txt")

        macros: dict[str, MacroTemplate] = {}
        with macro_path.open("r", encoding="utf-8") as file:
            next(file) # skip first line with version number
            lines: list[str] = file.readlines()
            for line in lines:
                line = line.strip()
                if line is None or len(line) == 0:
                    continue

                parts: list[str] = line.split()
                identifier: str = parts[0]

                arguments_text, command_text = line.split("|", 1)
                arguments: list[str] = arguments_text.split()[1:]
                command_text = command_text.strip()

                if not all(re.match(r"^<[^<>]+>$", argument) for argument in arguments):
                    raise Exception() # TODO

                default_values: list[any] = []
                parsed_arguments: list[str] = []
                for argument in arguments:
                    if "=" in argument:
                        name, value = argument[1:-1].split("=", 1)
                        default_values.append(value)
                        parsed_arguments.append(f"{name}")
                    else:
                        default_values.append(None)
                        parsed_arguments.append(argument[1:-1])

                macros[identifier] = MacroTemplate(
                    identifier=identifier,
                    raw=line,
                    command_text=command_text,
                    arguments=parsed_arguments,
                    default_argument_values=default_values,
                )

        return macros

    @classmethod
    def update_macro(cls, macro: MacroTemplate):
        cls._check_initialization()
        cls._macros[macro.identifier] = macro

    @classmethod
    def remove_macro(cls, macro: MacroTemplate):
        cls._check_initialization()
        cls._macros.pop(macro.identifier)

    @classmethod
    def save_macros_file(cls):
        macro_path: Path = get_data_path().joinpath("macros.txt")
        with macro_path.open("w", encoding="utf-8") as file:
            file.write(f"{__macro_version__}\n")
            for macro in cls.iterable_macros:
                file.write(f"{macro.raw}\n")
