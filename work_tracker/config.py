from __future__ import annotations

from path import Path
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
    # v2
    input_history_size: int
    multi_date_start_symbol: str
    multi_date_end_symbol: str
    time_add_prefix: str
    time_subtract_prefix: str
    keyword_prefix: str


class FrameConfig(BaseModel):
    padding: int
    title_padding: int
    title_left_side_padding: int
    title_footer_right_side_padding: int


class OutputConfig(BaseModel):
    max_width: int
    frame: FrameConfig


__config_version__: int = 2


class MainConfig(BaseModel):
    version: int = __config_version__
    command: CommandConfig
    input: InputConfig
    output: OutputConfig

    @staticmethod
    def _is_latest_config_version(raw_data: dict[str, any]) -> bool:
        return raw_data.get("version") == __config_version__

    @staticmethod
    def _update_config_data_to_v2(raw_data: dict[str, any]):
        raw_data["input"]["input_history_size"] = raw_data["input"].get("input_history_size", 1000)
        raw_data["input"]["multi_date_start_symbol"] = raw_data.pop("multi_date_start_symbol", "(")
        raw_data["input"]["multi_date_end_symbol"] = raw_data.pop("multi_date_end_symbol", ")")
        raw_data["input"]["time_add_prefix"] = raw_data.pop("time_add_prefix", "+")
        raw_data["input"]["time_subtract_prefix"] = raw_data.pop("time_subtract_prefix", "-")
        raw_data["input"]["keyword_prefix"] = raw_data.pop("keyword_prefix", "$")
        
        raw_data["version"] = 2
        
    @classmethod
    def _update_config_data_to_latest_version(cls, raw_data: dict[str, any]):
        # just like data, update to target version step by step: A -> A+1 -> A+2 -> ... -> B
        current_version: int = raw_data.get("version", 1)

        if current_version == 1:
            cls._update_config_data_to_v2(raw_data)
            current_version = 2


class Config:
    _data: MainConfig = None

    @classmethod
    def ready(cls) -> bool:
        return cls.data is not None

    @classproperty
    def data(cls) -> MainConfig:
        if cls._data is None:
            cls._load()
        return cls._data

    @classproperty
    def config_path(cls) -> Path:
        return get_data_path().joinpath("config.yaml")

    @classmethod
    def _load(cls):
        with open(cls.config_path, "r") as file:
            raw_data: dict[str, any] = yaml.safe_load("".join(file))

        was_updated: bool = False
        if not MainConfig._is_latest_config_version(raw_data):
            with open(get_data_path().joinpath("config.yaml.backup"), "w") as file:
                file.write(yaml.safe_dump(raw_data, indent=4))
            
            MainConfig._update_config_data_to_latest_version(raw_data)
            was_updated = True

        cls._data = MainConfig(**raw_data)
        if was_updated:
            cls.save()

    @classmethod
    def save(cls):
        with open(cls.config_path, "w") as file:
            file.write(yaml.safe_dump(cls.data.model_dump(), indent=4))

