from dataclasses import dataclass
from pathlib import Path

from work_tracker.common import get_data_path, classproperty


@dataclass(frozen=True)
class AliasTemplate:
    identifier: str
    raw: str
    replacement_text: str


__alias_version__: int = 1


class AliasManager:
    _aliases: dict[str, AliasTemplate] = {}
    _initialized: bool = False

    @classproperty
    def aliases(cls) -> dict[str, AliasTemplate]:
        cls._check_initialization()
        return cls._aliases # TODO deepcopy

    @classproperty
    def iterable_aliases(cls) -> list[AliasTemplate]:
        cls._check_initialization()
        return list(cls._aliases.values())

    @classmethod
    def _check_initialization(cls):
        if not cls._initialized:
            if not cls._is_latest_alias_version():
                cls._update_aliases_to_latest_version()
            cls._aliases = cls._initialize_aliases()
            cls._initialized = True

    @classmethod
    def _is_latest_alias_version(cls) -> bool:
        alias_path: Path = get_data_path().joinpath("aliases.txt")
        with alias_path.open("r", encoding="utf-8") as file:
            version: int = int(next(file))

        return version == __alias_version__

    @classmethod
    def _update_aliases_to_latest_version(cls):
        # just like data, update to target version step by step: A -> A+1 -> A+2 -> ... -> B
        # remember to save the file, after update !
        pass

    @classmethod
    def _initialize_aliases(cls) -> dict[str, AliasTemplate]:
        alias_path: Path = get_data_path().joinpath("aliases.txt")

        aliases: dict[str, AliasTemplate] = {}
        with alias_path.open("r", encoding="utf-8") as file:
            next(file) # skip first line with version number
            lines: list[str] = file.readlines()
            for line in lines:
                line = line.strip()
                if line is None or len(line) == 0:
                    continue

                parts: list[str] = line.split("|", 1)
                if len(parts) != 2:
                    raise Exception() # TODO

                identifier: str = parts[0].strip()
                replacement_text: str = parts[1].strip()

                aliases[identifier] = AliasTemplate(
                    identifier=identifier,
                    raw=line,
                    replacement_text=replacement_text,
                )

        return aliases

    @classmethod
    def update_alias(cls, alias: AliasTemplate):
        cls._check_initialization()
        cls._aliases[alias.identifier] = alias

    @classmethod
    def remove_alias(cls, alias: AliasTemplate):
        cls._check_initialization()
        cls._aliases.pop(alias.identifier)

    @classmethod
    def save_aliases_file(cls):
        alias_path: Path = get_data_path().joinpath("aliases.txt")
        with alias_path.open("w", encoding="utf-8") as file:
            file.write(f"{__alias_version__}\n")
            for alias in cls.iterable_aliases:
                file.write(f"{alias.raw}\n")
