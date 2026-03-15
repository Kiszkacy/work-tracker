import datetime
import lzma
import os
import pickle
from dataclasses import dataclass, field
from enum import Enum, auto

from path import Path

from .common import AppData, get_data_path, get_cache_path


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
    @classmethod
    def load(cls, identifier: str, manual_checkpoint: bool = False) -> AppData | None: # TODO os exceptions
        if manual_checkpoint:
            for checkpoint_path in cls.all_manual_checkpoints():
                name, date = checkpoint_path.name.removesuffix('.save.checkpoint').split("__") # TODO hardcoded '.save.checkpoint'
                if name == identifier:
                    identifier = f"{name}__{date}"

        path: Path = (get_data_path() if not manual_checkpoint else get_cache_path()).joinpath(f"{identifier}.save.checkpoint")
        if not path.exists():
            return None
        with lzma.open(path, "rb") as file:
            data: AppData = _CompatibilityUnpickler(file).load()
        return data

    @staticmethod
    def save(identifier: str, data: AppData, manual_checkpoint: bool = False): # TODO os exceptions
        full_identifier: str = identifier if not manual_checkpoint else f"{identifier}__{datetime.datetime.now().strftime('%H-%M-%S')}"
        path: Path = (get_data_path() if not manual_checkpoint else get_cache_path()).joinpath(f"{full_identifier}.save.checkpoint")
        with lzma.open(path, "wb") as file:
            pickle.dump(data, file)

    @classmethod
    def load_latest(cls) -> AppData | None: # TODO os exceptions
        files: list[Path] = cls.all_automatic_checkpoints()
        if not files:
            return None

        newest_file: str = max(files, key=os.path.getctime) # TODO this sorting might be unclear for user
        return cls.load(os.path.basename(newest_file.rstrip(".save.checkpoint")))

    @staticmethod
    def all_automatic_checkpoints() -> list[Path]: # TODO os exceptions
        return [get_data_path().joinpath(file) for file in os.listdir(get_data_path()) if file.endswith(".save.checkpoint") and os.path.isfile(get_data_path().joinpath(file))]

    @staticmethod
    def all_manual_checkpoints() -> list[Path]: # TODO os exceptions
        return [get_cache_path().joinpath(file) for file in os.listdir(get_cache_path()) if file.endswith(".save.checkpoint") and os.path.isfile(get_cache_path().joinpath(file))]

    @staticmethod
    def clear_cache():
        for name in os.listdir(get_cache_path()):
            if not os.path.isfile(get_cache_path().joinpath(name)):
                continue
            os.remove(get_cache_path().joinpath(name))
