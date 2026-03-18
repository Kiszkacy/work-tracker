from typing import Any

import pytest

from work_tracker.config import MainConfig


CONFIG_V1: dict[str, Any] = {
    "command": {
        "calendar": {
            "dayoff_background_color": None,
            "dayoff_foreground_color": "brightmagenta",
            "holiday_background_color": None,
            "holiday_foreground_color": "brightgreen",
            "office_background_color": None,
            "office_foreground_color": "brightred",
            "remote_background_color": None,
            "remote_foreground_color": "brightblue",
            "title_color": None,
            "weekend_background_color": None,
            "weekend_foreground_color": "yellow",
        },
        "help": {
            "command_list_description_padding": 2,
            "command_use_case_bullet_point_symbol": "- ",
            "command_use_case_description_padding": 4,
            "command_use_case_indent_size": 2,
        },
        "undo_history_size": 50,
    },
    "input": {
        "command_chain_symbol": "&&",
        "prefix": ">>",
        "sub_prefix": ":",
    },
    "output": {
        "frame": {
            "padding": 1,
            "title_footer_right_side_padding": 2,
            "title_left_side_padding": 2,
            "title_padding": 1,
        },
        "max_width": 80,
    },
    "version": 1,
}


def _migrate_v1_to_v2() -> dict[str, Any]:
    raw: dict[str, Any] = {k: v for k, v in CONFIG_V1.items()}
    raw["command"] = {k: v for k, v in CONFIG_V1["command"].items()}
    raw["command"]["calendar"] = dict(CONFIG_V1["command"]["calendar"])
    raw["command"]["help"] = dict(CONFIG_V1["command"]["help"])
    raw["input"] = dict(CONFIG_V1["input"])
    raw["output"] = {k: v for k, v in CONFIG_V1["output"].items()}
    raw["output"]["frame"] = dict(CONFIG_V1["output"]["frame"])
    MainConfig._update_config_data_to_latest_version(raw)
    return raw


@pytest.fixture
def v1_to_v2() -> dict[str, Any]:
    return _migrate_v1_to_v2()


def test_v1_to_v2_bumps_version(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["version"] == 2


def test_v1_to_v2_produces_valid_config(v1_to_v2: dict[str, Any]):
    config: MainConfig = MainConfig(**v1_to_v2)
    assert config.version == 2


# --- input ---

def test_v1_to_v2_adds_keyword_prefix(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["keyword_prefix"] == "$"


def test_v1_to_v2_adds_history_size(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["history_size"] == 1000


def test_v1_to_v2_adds_date_multi_start_symbol(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["date"]["multi_start_symbol"] == "("


def test_v1_to_v2_adds_date_multi_end_symbol(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["date"]["multi_end_symbol"] == ")"


def test_v1_to_v2_adds_date_normalize(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["date"]["normalize"] is False


def test_v1_to_v2_adds_time_add_prefix(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["time"]["add_prefix"] == "+"


def test_v1_to_v2_adds_time_subtract_prefix(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["time"]["subtract_prefix"] == "-"


# --- command ---

def test_v1_to_v2_adds_fte_default_value(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["fte"]["default_value"] == 1.0


def test_v1_to_v2_adds_rwr_default_value(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["rwr"]["default_value"] == 0.4


def test_v1_to_v2_adds_calendar_absence_foreground_color(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["calendar"]["absence_foreground_color"] == "brightblue"


def test_v1_to_v2_adds_calendar_absence_background_color(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["calendar"]["absence_background_color"] is None


def test_v1_to_v2_adds_calendar_office_incomplete_foreground_color(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["calendar"]["office_incomplete_foreground_color"] == "red"


def test_v1_to_v2_adds_calendar_office_incomplete_background_color(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["calendar"]["office_incomplete_background_color"] is None


def test_v1_to_v2_adds_calendar_remote_incomplete_foreground_color(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["calendar"]["remote_incomplete_foreground_color"] == "green"


def test_v1_to_v2_adds_calendar_remote_incomplete_background_color(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["calendar"]["remote_incomplete_background_color"] is None


# --- output ---

def test_v1_to_v2_adds_error_color(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["output"]["error_color"] == "brightred"


# --- preserves existing values ---

def test_v1_to_v2_preserves_existing_calendar_colors(v1_to_v2: dict[str, Any]):
    cal = v1_to_v2["command"]["calendar"]
    assert cal["dayoff_foreground_color"] == "brightmagenta"
    assert cal["holiday_foreground_color"] == "brightgreen"
    assert cal["office_foreground_color"] == "brightred"
    assert cal["remote_foreground_color"] == "brightblue"
    assert cal["weekend_foreground_color"] == "yellow"


def test_v1_to_v2_preserves_undo_history_size(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["command"]["undo_history_size"] == 50


def test_v1_to_v2_preserves_output_max_width(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["output"]["max_width"] == 80


def test_v1_to_v2_preserves_input_prefix(v1_to_v2: dict[str, Any]):
    assert v1_to_v2["input"]["prefix"] == ">>"
    assert v1_to_v2["input"]["sub_prefix"] == ":"
    assert v1_to_v2["input"]["command_chain_symbol"] == "&&"
