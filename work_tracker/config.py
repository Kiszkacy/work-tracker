from __future__ import annotations

from typing import Any

import yaml
from path import Path
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
    # v2
    remote_incomplete_background_color: str | None
    remote_incomplete_foreground_color: str | None
    office_incomplete_background_color: str | None
    office_incomplete_foreground_color: str | None
    absence_foreground_color: str | None
    absence_background_color: str | None


class FteCommandConfig(BaseModel): # v2
    default_value: float


class HelpCommandConfig(BaseModel):
    command_list_description_padding: int
    command_use_case_indent_size: int
    command_use_case_description_padding: int
    command_use_case_bullet_point_symbol: str


class RwrCommandConfig(BaseModel): # v2
    default_value: float


class CommandConfig(BaseModel):
    undo_history_size: int
    calendar: CalendarCommandConfig
    help: HelpCommandConfig
    # v2
    fte: FteCommandConfig
    rwr: RwrCommandConfig


class InputDateConfig(BaseModel):
    multi_start_symbol: str
    multi_end_symbol: str
    normalize: bool


class InputTimeConfig(BaseModel):
    add_prefix: str
    subtract_prefix: str


class InputConfig(BaseModel):
    command_chain_symbol: str
    prefix: str
    sub_prefix: str
    # v2
    keyword_prefix: str
    history_size: int
    date: InputDateConfig
    time: InputTimeConfig


class FrameConfig(BaseModel):
    padding: int
    title_padding: int
    title_left_side_padding: int
    title_footer_right_side_padding: int


class OutputConfig(BaseModel):
    max_width: int
    frame: FrameConfig
    # v2
    error_color: str


__config_version__: int = 2


class MainConfig(BaseModel):
    version: int = __config_version__
    command: CommandConfig
    input: InputConfig
    output: OutputConfig

    @staticmethod
    def _is_latest_config_version(raw_data: dict[str, Any]) -> bool:
        return raw_data.get("version") == __config_version__

    @staticmethod
    def _update_config_data_to_v2(raw_data: dict[str, Any]):
        raw_data["input"]["history_size"] = raw_data["input"].get("history_size", 1000)
        raw_data["input"]["keyword_prefix"] = raw_data.pop("keyword_prefix", "$")
        raw_data["input"].setdefault("date", {})
        raw_data["input"]["date"]["multi_start_symbol"] = raw_data.pop("multi_start_symbol", "(")
        raw_data["input"]["date"]["multi_end_symbol"] = raw_data.pop("multi_end_symbol", ")")
        raw_data["input"]["date"]["normalize"] = raw_data.pop("normalize", False)
        raw_data["input"].setdefault("time", {})
        raw_data["input"]["time"]["add_prefix"] = raw_data.pop("add_prefix", "+")
        raw_data["input"]["time"]["subtract_prefix"] = raw_data.pop("subtract_prefix", "-")

        raw_data["command"]["calendar"]["absence_background_color"] = raw_data["command"]["calendar"].get("absence_background_color", None)
        raw_data["command"]["calendar"]["absence_foreground_color"] = raw_data["command"]["calendar"].get("absence_foreground_color", "brightblue")
        raw_data["command"]["calendar"]["office_incomplete_background_color"] = raw_data["command"]["calendar"].get("office_incomplete_background_color", None)
        raw_data["command"]["calendar"]["office_incomplete_foreground_color"] = raw_data["command"]["calendar"].get("office_incomplete_foreground_color", "red")
        raw_data["command"]["calendar"]["remote_incomplete_background_color"] = raw_data["command"]["calendar"].get("remote_incomplete_background_color", None)
        raw_data["command"]["calendar"]["remote_incomplete_foreground_color"] = raw_data["command"]["calendar"].get("remote_incomplete_foreground_color", "green")

        raw_data["command"].setdefault("fte", {})
        raw_data["command"]["fte"]["default_value"] = raw_data["command"]["fte"].get("default_value", 1.0)
        raw_data["command"].setdefault("rwr", {})
        raw_data["command"]["rwr"]["default_value"] = raw_data["command"]["rwr"].get("default_value", 0.4)

        raw_data["output"]["error_color"] = raw_data["output"].get("error_color", "brightred")

        raw_data["version"] = 2

    @classmethod
    def _update_config_data_to_latest_version(cls, raw_data: dict[str, Any]):
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
            raw_data: dict[str, Any] = yaml.safe_load("".join(file))

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

