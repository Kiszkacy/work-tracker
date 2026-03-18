import datetime
import lzma
import os
import pickle
import re
from dataclasses import dataclass, field
from enum import Enum, auto

from path import Path

from .common import AppData, get_data_path, get_cache_path, classproperty


@dataclass(frozen=True)
class CheckpointTemplate:
    path: Path
    full_identifier: str
    name: str
    date: str
    persistent: bool


# deprecated classes for unpickling old data - only used during initial load after update
# === v1 start
class _WorkStrategy(Enum):
    Default = auto()
    Quick = auto()


@dataclass
class _WorkSetup:
    default_fte: float = 1.0
    preferred_weekdays: list[int] = field(default_factory=list)
    non_availability_weekdays: list[int] = field(default_factory=list)
    default_remote_work_ratio: float = 0.4
    preferred_remote_weekdays: list[int] = field(default_factory=list)
    preferred_office_day_length_in_minutes: int | None = 480
    preferred_remote_day_length_in_minutes: int | None = 480
    office_day_max_length_in_minutes: int | None = 600
    remote_day_max_length_in_minutes: int | None = 600
    each_weekday_max_length_in_minutes: list[int | None] = field(default_factory=lambda: [None, None, None, None, None])
    strategy: _WorkStrategy = _WorkStrategy.Default


class _CompatibilityUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == 'work_tracker.common':
            if name == 'WorkSetup':
                return _WorkSetup
            elif name == 'WorkStrategy':
                return _WorkStrategy
        return super().find_class(module, name)
# === v1 end


class CheckpointManager:
    _usermade_checkpoint_prefix: str = "user."
    _checkpoint_suffix: str = ".save.checkpoint"

    @classproperty
    def usermade_checkpoint_prefix(cls) -> str:
        return cls._usermade_checkpoint_prefix

    @classproperty
    def checkpoint_suffix(cls) -> str:
        return cls._checkpoint_suffix

    @classmethod
    def load(cls, identifier: str, persistent_checkpoint: bool = True) -> AppData | None: # TODO os exceptions
        if not persistent_checkpoint:
            for checkpoint in cls.temporary_checkpoints():
                base_name: str = checkpoint.full_identifier.removesuffix(f"__{checkpoint.date}") if checkpoint.date != "-" else checkpoint.full_identifier
                if base_name == identifier:
                    identifier = checkpoint.full_identifier

        path: Path = (get_data_path() if persistent_checkpoint else get_cache_path()).joinpath(f"{identifier}{cls._checkpoint_suffix}")
        if not path.exists():
            return None
        with lzma.open(path, "rb") as file:
            data: AppData = _CompatibilityUnpickler(file).load()
        return data

    @classmethod
    def save(cls, identifier: str, data: AppData, persistent_checkpoint: bool = True, add_suffix_timestamp: bool = False, created_by_user: bool = False): # TODO os exceptions
        full_identifier: str = identifier if not add_suffix_timestamp else f"{identifier}__{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        path: Path = (get_data_path() if persistent_checkpoint else get_cache_path()).joinpath(f"{cls._usermade_checkpoint_prefix if created_by_user else ''}{full_identifier}{cls._checkpoint_suffix}")
        with lzma.open(path, "wb") as file:
            pickle.dump(data, file)

    @classmethod
    def load_latest(cls) -> AppData | None: # TODO os exceptions
        checkpoints: list[CheckpointTemplate] = cls.persistent_checkpoints()
        if not checkpoints:
            return None

        newest: CheckpointTemplate = max(checkpoints, key=lambda c: os.path.getctime(c.path)) # TODO this sorting might be unclear for user
        return cls.load(newest.full_identifier)

    @classmethod
    def persistent_checkpoints(cls) -> list[CheckpointTemplate]: # TODO os exceptions
        paths: list[Path] = [get_data_path().joinpath(file) for file in os.listdir(get_data_path()) if file.endswith(cls._checkpoint_suffix) and os.path.isfile(get_data_path().joinpath(file))]
        return [cls._parse_checkpoint(path, persistent=True) for path in paths]

    @classmethod
    def temporary_checkpoints(cls) -> list[CheckpointTemplate]: # TODO os exceptions
        paths: list[Path] = [get_cache_path().joinpath(file) for file in os.listdir(get_cache_path()) if file.endswith(cls._checkpoint_suffix) and os.path.isfile(get_cache_path().joinpath(file))]
        return [cls._parse_checkpoint(path, persistent=False) for path in paths]

    @classmethod
    def checkpoints(cls) -> list[CheckpointTemplate]: # TODO os exceptions
        return cls.temporary_checkpoints() + cls.persistent_checkpoints()

    @classmethod
    def _parse_checkpoint(cls, path: Path, persistent: bool) -> CheckpointTemplate:
        raw_name: str = path.name.removesuffix(cls._checkpoint_suffix)
        match: re.Match = re.match(r"(.+?)__(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$", raw_name)
        if match:
            full_identifier: str = raw_name
            name: str = match.group(1)
            date: str = match.group(2)
        else:
            full_identifier: str = raw_name
            name: str = raw_name
            date: str = "-"
        return CheckpointTemplate(
            path=path,
            full_identifier=full_identifier,
            name=name,
            date=date,
            persistent=persistent
        )

    @staticmethod
    def clear_cache():
        for name in os.listdir(get_cache_path()):
            if not os.path.isfile(get_cache_path().joinpath(name)):
                continue
            os.remove(get_cache_path().joinpath(name))
