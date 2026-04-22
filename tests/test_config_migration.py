from copy import deepcopy
from typing import Any

import pytest

from work_tracker.config import MainConfig, __config_version__

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

CONFIG_V2: dict[str, Any] = {
    "command": {
        "calendar": {
            "absence_background_color": None,
            "absence_foreground_color": "brightblue",
            "dayoff_background_color": None,
            "dayoff_foreground_color": "brightcyan",
            "holiday_background_color": None,
            "holiday_foreground_color": "brightmagenta",
            "office_background_color": None,
            "office_foreground_color": "brightred",
            "office_incomplete_background_color": None,
            "office_incomplete_foreground_color": "red",
            "remote_background_color": None,
            "remote_foreground_color": "brightgreen",
            "remote_incomplete_background_color": None,
            "remote_incomplete_foreground_color": "green",
            "title_color": None,
            "weekend_background_color": None,
            "weekend_foreground_color": "yellow",
        },
        "fte": {
            "default_value": 1.0,
        },
        "help": {
            "command_list_description_padding": 2,
            "command_use_case_bullet_point_symbol": "- ",
            "command_use_case_description_padding": 4,
            "command_use_case_indent_size": 2,
        },
        "rwr": {
            "default_value": 0.4,
        },
        "undo_history_size": 50,
    },
    "input": {
        "autocompletion": {
            "max_popup_width": 80,
        },
        "command_chain_symbol": "&&",
        "date": {
            "multi_start_symbol": "(",
            "multi_end_symbol": ")",
            "normalize": False,
        },
        "history_size": 1000,
        "keyword_prefix": "$",
        "prefix": ">>",
        "sub_prefix": ":",
        "time": {
            "add_prefix": "+",
            "subtract_prefix": "-",
        },
    },
    "output": {
        "frame": {
            "padding": 1,
            "title_footer_right_side_padding": 2,
            "title_left_side_padding": 2,
            "title_padding": 1,
        },
        "max_width": 80,
        "error_color": "brightred",
    },
    "version": 2,
}

CONFIG_V3: dict[str, Any] = {
    "command": {
        "calendar": {
            "absence_background_color": None,
            "absence_foreground_color": "brightblue",
            "dayoff_background_color": None,
            "dayoff_foreground_color": "brightcyan",
            "holiday_background_color": None,
            "holiday_foreground_color": "brightmagenta",
            "office_background_color": None,
            "office_foreground_color": "brightred",
            "office_incomplete_background_color": None,
            "office_incomplete_foreground_color": "red",
            "remote_background_color": None,
            "remote_foreground_color": "brightgreen",
            "remote_incomplete_background_color": None,
            "remote_incomplete_foreground_color": "green",
            "title_color": None,
            "weekend_background_color": None,
            "weekend_foreground_color": "yellow",
        },
        "fte": {
            "default_value": 1.0,
        },
        "help": {
            "command_list_description_padding": 2,
            "command_use_case_bullet_point_symbol": "- ",
            "command_use_case_description_padding": 4,
            "command_use_case_indent_size": 2,
        },
        "rwr": {
            "default_value": 0.4,
        },
        "undo_history_size": 50,
    },
    "input": {
        "autocompletion": {
            "max_popup_width": 80,
        },
        "command_chain_symbol": "&&",
        "date": {
            "multi_start_symbol": "(",
            "multi_end_symbol": ")",
            "normalize": False,
        },
        "history_size": 1000,
        "keyword_prefix": "$",
        "prefix": ">>",
        "sub_prefix": ":",
        "time": {
            "add_prefix": "+",
            "subtract_prefix": "-",
        },
    },
    "output": {
        "frame": {
            "padding": 1,
            "title_footer_right_side_padding": 2,
            "title_left_side_padding": 2,
            "title_padding": 1,
        },
        "max_width": 80,
        "error_color": "brightred",
    },
    "version": 3,
}


def _migrate_v1_to_v2() -> dict[str, Any]:
    raw: dict[str, Any] = deepcopy(CONFIG_V1)
    MainConfig._update_config_data_to_v2(raw)
    return raw


def _migrate_v1_to_v3() -> dict[str, Any]:
    raw: dict[str, Any] = deepcopy(CONFIG_V1)
    MainConfig._update_config_data_to_v2(raw)
    MainConfig._update_config_data_to_v3(raw)
    return raw


def _migrate_v2_to_v3() -> dict[str, Any]:
    raw: dict[str, Any] = deepcopy(CONFIG_V2)
    MainConfig._update_config_data_to_v3(raw)
    return raw


def _migrate_v1_to_v4() -> dict[str, Any]:
    raw: dict[str, Any] = deepcopy(CONFIG_V1)
    MainConfig._update_config_data_to_v2(raw)
    MainConfig._update_config_data_to_v3(raw)
    MainConfig._update_config_data_to_v4(raw)
    return raw


def _migrate_v2_to_v4() -> dict[str, Any]:
    raw: dict[str, Any] = deepcopy(CONFIG_V2)
    MainConfig._update_config_data_to_v3(raw)
    MainConfig._update_config_data_to_v4(raw)
    return raw


def _migrate_v3_to_v4() -> dict[str, Any]:
    raw: dict[str, Any] = deepcopy(CONFIG_V3)
    MainConfig._update_config_data_to_v4(raw)
    return raw


@pytest.fixture
def v1_to_v2() -> dict[str, Any]:
    return _migrate_v1_to_v2()


@pytest.fixture
def v1_to_v3() -> dict[str, Any]:
    return _migrate_v1_to_v3()


@pytest.fixture
def v2_to_v3() -> dict[str, Any]:
    return _migrate_v2_to_v3()


@pytest.fixture
def v1_to_v4() -> dict[str, Any]:
    return _migrate_v1_to_v4()


@pytest.fixture
def v2_to_v4() -> dict[str, Any]:
    return _migrate_v2_to_v4()


@pytest.fixture
def v3_to_v4() -> dict[str, Any]:
    return _migrate_v3_to_v4()


def test_v1_to_v4_produces_valid_config(v1_to_v4: dict[str, Any]):
    config: MainConfig = MainConfig(**v1_to_v4)
    assert config.version == __config_version__


def test_v2_to_v4_produces_valid_config(v2_to_v4: dict[str, Any]):
    config: MainConfig = MainConfig(**v2_to_v4)
    assert config.version == __config_version__


def test_v3_to_v4_bumps_version(v3_to_v4: dict[str, Any]):
    assert v3_to_v4["version"] == __config_version__


def test_v3_to_v4_produces_valid_config(v3_to_v4: dict[str, Any]):
    config: MainConfig = MainConfig(**v3_to_v4)
    assert config.version == __config_version__


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


def test_v2_to_v3_adds_autocompletion_max_popup_width(v2_to_v3: dict[str, Any]):
    assert v2_to_v3["input"]["autocompletion"]["max_popup_width"] == 80


def test_v3_to_v4_adds_color_command(v3_to_v4: dict[str, Any]):
    assert v3_to_v4["input"]["autocompletion"]["color"]["command"] == ""


def test_v3_to_v4_adds_color_abbreviation(v3_to_v4: dict[str, Any]):
    assert v3_to_v4["input"]["autocompletion"]["color"]["abbreviation"] == "fg:ansiwhite bg:ansibrightblack"


def test_v3_to_v4_adds_color_alias(v3_to_v4: dict[str, Any]):
    assert v3_to_v4["input"]["autocompletion"]["color"]["alias"] == "bg:ansiblue"


def test_v3_to_v4_adds_color_macro(v3_to_v4: dict[str, Any]):
    assert v3_to_v4["input"]["autocompletion"]["color"]["macro"] == "bg:ansired"


def test_v3_to_v4_adds_color_keyword(v3_to_v4: dict[str, Any]):
    assert v3_to_v4["input"]["autocompletion"]["color"]["keyword"] == "bg:ansigreen"


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


def test_v3_to_v4_preserves_max_popup_width(v3_to_v4: dict[str, Any]):
    assert v3_to_v4["input"]["autocompletion"]["max_popup_width"] == 80