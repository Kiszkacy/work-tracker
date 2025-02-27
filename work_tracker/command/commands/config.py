import yaml
from pydantic import BaseModel

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.config import Config
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount
from work_tracker.text.common import Color


class ConfigHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            yamllike_text: str = yaml.dump(Config.data.dict(), default_flow_style=False, sort_keys=False)
            text_with_lines: list[str] = []
            for line in yamllike_text.splitlines():
                text_with_lines.append(f"| {line}")

            self.io.output("\n".join(text_with_lines))
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            value: any = self._get_printable_nested_config_value(arguments[0])
            if value is None:
                self.io.output(f"The field {Color.Brightblue.value}{arguments[0]}{Color.Reset.value} could not be found in the config.")
            else:
                self.io.output(f"{value}")
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

    def _get_config_value_via_dot_keys(self, value_path: str, use_clean_copy: bool) -> any:
        keys: list[str] = value_path.split(".")
        dictionary: dict[str, any] | any = Config.data.dict() if use_clean_copy else Config.data
        for key in keys:
            if not isinstance(dictionary, BaseModel):
                return None
            dictionary = getattr(dictionary, key)
        return dictionary

    def _set_config_value_via_dot_keys(self, value_path: str, value: any) -> bool:
        keys: list[str] = value_path.split(".")
        keys_before_last, last_key = keys[:-1], keys[-1]
        if last_key == "version":
            self.io.output("The version field value can not be changed.")
            return False

        dictionary: BaseModel | None = self._get_config_value_via_dot_keys(".".join(keys_before_last), False)
        if dictionary is None:
            self.io.output(f"Could not find the specified field {Color.Brightred.value}{value_path}{Color.Reset.value}. Ensure that the path is correct.")
            return False
        elif not isinstance(dictionary, BaseModel):
            self.io.output(f"The field {Color.Brightred.value}{value_path}{Color.Reset.value} could not be found in the config.")
            return False
        elif getattr(dictionary, last_key) is None:
            self.io.output(f"The field {Color.Brightred.value}{value_path}{Color.Reset.value} could not be found in the config.")
            return False
        elif isinstance(getattr(dictionary, last_key), BaseModel):
            self.io.output(f"The field {Color.Brightred.value}{value_path}{Color.Reset.value} is not a changeable config field.")
            return False

        expected_type: type = type(getattr(dictionary, last_key)) # TODO this wont work if field can be assigned multiple types
        if not isinstance(value, expected_type):
            self.io.output(f"Invalid type of value to change field {Color.Brightred.value}{last_key}{Color.Reset.value}.")
            return False

        setattr(dictionary, last_key, value)
        Config.save()
        return True

    def _get_printable_nested_config_value(self, value_path: str) -> any:
        value: any = self._get_config_value_via_dot_keys(value_path, True)
        if value is None:
            return None

        if isinstance(value, dict):
            yamllike_text: str = yaml.safe_dump(value, default_flow_style=False, sort_keys=False)
            text_with_lines: list[str] = []
            for line in yamllike_text.splitlines():
                text_with_lines.append(f"| {line}")

            return "\n".join(text_with_lines)
        else:
            return value
