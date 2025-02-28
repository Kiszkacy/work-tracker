from __future__ import annotations

import yaml
from pydantic import BaseModel

from work_tracker.common import get_data_path, classproperty


class CalendarCommandConfig(BaseModel):
    title_color: str | None
    weekend_foreground_color: str | None
    weekend_background_color: str | None
    holiday_foreground_color: str | None
    holiday_background_color: str | None
    office_foreground_color: str | None
    office_background_color: str | None
    remote_foreground_color: str | None
    remote_background_color: str | None
    dayoff_foreground_color: str | None
    dayoff_background_color: str | None


class HelpCommandConfig(BaseModel):
    command_list_description_padding: int
    command_use_case_indent_size: int
    command_use_case_description_padding: int
    command_use_case_bullet_point_symbol: str


class CommandConfig(BaseModel):
    undo_history_size: int
    calendar: CalendarCommandConfig
    help: HelpCommandConfig


class InputConfig(BaseModel):
    command_chain_symbol: str
    prefix: str
    sub_prefix: str


class FrameConfig(BaseModel):
    padding: int
    title_padding: int
    title_left_side_padding: int
    title_footer_right_side_padding: int


class OutputConfig(BaseModel):
    max_width: int
    frame: FrameConfig


__config_version__: int = 1


class MainConfig(BaseModel):
    version: int = __config_version__
    command: CommandConfig
    input: InputConfig
    output: OutputConfig

    @classmethod
    def load(cls) -> MainConfig:
        with open(get_data_path().joinpath("config.yaml"), "r") as file:
            raw_data: dict[str, any] = yaml.safe_load("".join(file))

        if not cls._is_latest_config_version(raw_data):
            cls._update_config_data_to_latest_version(raw_data)

        return MainConfig(**raw_data)

    @staticmethod
    def _is_latest_config_version(raw_data: dict[str, any]) -> bool:
        return raw_data.get("version") == __config_version__

    @staticmethod
    def _update_config_data_to_latest_version(raw_data: dict[str, any]) -> dict[str, any]:
        # just like data, update to target version step by step: A -> A+1 -> A+2 -> ... -> B
        # remember to save the file, after update !
        pass


class Config:
    _data: MainConfig = None

    @classmethod
    def ready(cls) -> bool:
        return cls.data is not None

    @classproperty
    def data(cls) -> MainConfig:
        if cls._data is None:
            cls._data = MainConfig.load()
        return cls._data

    @classmethod
    def save(cls):
        with open(get_data_path().joinpath("config.yaml"), "w") as file:
            file.write(yaml.safe_dump(cls.data.dict(), indent=4))
