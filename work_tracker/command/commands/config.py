from typing import Any

import yaml
from prompt_toolkit.completion import Completion
from pydantic import BaseModel, TypeAdapter

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, CompletionCandidate
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.config import Config
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount
from work_tracker.text.common import Color


class ConfigHandler(CommandHandler):
    _MISSING = object()

    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        def leaf_keys(d: dict, prefix: str = "") -> list[str]: # TODO: ugly layered function
            return [key for k, v in d.items() for key in (leaf_keys(v, f"{prefix}.{k}" if prefix else k) if isinstance(v, dict) else [f"{prefix}.{k}" if prefix else k])]

        if len(typed_words) == 0:
            keys: list[str] = [key for key in leaf_keys(Config.data.model_dump()) if key != "version"]
            return cls.get_fitting_completions([CompletionCandidate(k) for k in keys], last_word)
        if len(typed_words) == 1:
            dict_: dict[str, Any] | Any = Config.data.model_dump()
            for key in typed_words[0].split("."):
                dict_ = dict_.get(key) if isinstance(dict_, dict) else None
            if not isinstance(dict_, dict):
                return cls.get_fitting_completions([CompletionCandidate(str(dict_), "current value")], last_word)
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            yamllike_text: str = yaml.dump(Config.data.model_dump(), default_flow_style=False, sort_keys=False)
            text_with_lines: list[str] = []
            for line in yamllike_text.splitlines():
                text_with_lines.append(f"| {line}")

            self.io.output("\n".join(text_with_lines))
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            value: Any = self._get_printable_nested_config_value(arguments[0])
            if value is self._MISSING:
                self.io.output(f"The field {Color.Brightblue.value}{arguments[0]}{Color.Reset.value} could not be found in the config.")
            else:
                self.io.output(f"{value if value is not None else 'null'}")
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 2:
            changed_successfully: bool = self._set_config_value_via_dot_keys(arguments[0], arguments[1])
            if changed_successfully:
                return CommandHandlerResult(undoable=False)
            else:
                return CommandHandlerResult(undoable=False)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count > 2
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _get_config_value_via_dot_keys(self, value_path: str, get_dict_structure: bool) -> Any:
        keys: list[str] = value_path.split(".")
        dictionary: dict[str, Any] | Any = Config.data.model_dump() if get_dict_structure else Config.data
        for key in keys:
            if not get_dict_structure and not isinstance(dictionary, BaseModel):
                return self._MISSING
            elif get_dict_structure and not isinstance(dictionary, dict):
                return self._MISSING

            if get_dict_structure:
                if key not in dictionary:
                    return self._MISSING
                dictionary = dictionary[key]
            else:
                dictionary = getattr(dictionary, key, self._MISSING)
        return dictionary

    def _set_config_value_via_dot_keys(self, value_path: str, value: Any) -> bool:
        keys: list[str] = value_path.split(".")
        keys_before_last, last_key = keys[:-1], keys[-1]
        if last_key == "version":
            self.io.output("The version field value can not be changed.")
            return False

        dictionary: BaseModel | None = self._get_config_value_via_dot_keys(".".join(keys_before_last), False)
        if dictionary is self._MISSING:
            self.io.output(f"Could not find the specified field {Color.from_key(Config.data.output.error_color).value}{value_path}{Color.Reset.value}. Ensure that the path is correct.")
            return False
        elif not isinstance(dictionary, BaseModel):
            self.io.output(f"The field {Color.from_key(Config.data.output.error_color).value}{value_path}{Color.Reset.value} could not be found in the config.")
            return False
        elif getattr(dictionary, last_key, self._MISSING) is self._MISSING:
            self.io.output(f"The field {Color.from_key(Config.data.output.error_color).value}{value_path}{Color.Reset.value} could not be found in the config.")
            return False
        elif isinstance(getattr(dictionary, last_key), BaseModel):
            self.io.output(f"The field {Color.from_key(Config.data.output.error_color).value}{value_path}{Color.Reset.value} is not a changeable config field.")
            return False

        parent: BaseModel = self._get_config_value_via_dot_keys(".".join(keys[:-1]), False)
        processed_value: Any = None if str(value).lower() in ("null", "none") else value
        try:
            annotation: type = parent.model_fields[last_key].annotation
            validated_value: Any = TypeAdapter(annotation).validate_python(processed_value)
            setattr(parent, last_key, validated_value)
            Config.save()
            return True
        except Exception:
            self.io.output(f"Invalid type of value to change field {Color.from_key(Config.data.output.error_color).value}{last_key}{Color.Reset.value}.")
            return False

    def _get_printable_nested_config_value(self, value_path: str) -> Any:
        value: Any = self._get_config_value_via_dot_keys(value_path, True)
        if value is self._MISSING:
            return self._MISSING

        if isinstance(value, dict):
            yamllike_text: str = yaml.safe_dump(value, default_flow_style=False, sort_keys=False)
            text_with_lines: list[str] = []
            for line in yamllike_text.splitlines():
                text_with_lines.append(f"| {line}")

            return "\n".join(text_with_lines)
        else:
            return value
