import datetime
import lzma
import os
import pickle

from path import Path

from .common import AppData, get_data_path, get_cache_path


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
            data: AppData = pickle.load(file)
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
