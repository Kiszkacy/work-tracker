import re

from work_tracker.error import CommandErrorInvalidDateCount
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.command.macro_manager import MacroManager, MacroTemplate
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.text.common import wrap_text, frame_text, Color


class MacroHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        # TODO add pagination
        if date_count == 0 and argument_count == 0:
            raw_texts: list[str] = [macro.raw for macro in MacroManager.iterable_macros]
            macro_definitions: list[str] = [text.split("|", 1)[0].strip() for text in raw_texts]
            macro_commands: list[str] = [text.split("|", 1)[1].strip() for text in raw_texts]

            longest_definition_size: int = max(len(definition) for definition in macro_definitions)

            # TODO add ellipsis here and in other places modifiable by user (custom methods in the future)
            # TODO what if definition is very long => solution: set max length in config and add ellipsis if its too long
            seperator: str = " | " # TODO make seperator configurable, but the read logic must be changed too
            macro_texts: list[str] = []
            for index, (definition, command) in enumerate(zip(macro_definitions, macro_commands)):
                command_wrapped: str = wrap_text(
                    text=command,
                    indent=" "*(longest_definition_size + len(seperator)),
                    omit_first_line_indent=True,
                    frame_wrap=True
                )
                macro_texts.append(f"{Color.Brightblack.value if index % 2 == 1 else Color.Reset.value}{definition.rjust(longest_definition_size)}{seperator}{command_wrapped}")

            framed_text: str = frame_text(
                text="\n".join(macro_texts),
                title="Macros",
                title_color=Color.Bold
            )
            self.io.output(framed_text)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            macro_identifier: str = arguments[0]
            if macro_identifier in MacroManager.macros:
                self.io.output(MacroManager.macros[macro_identifier].raw)
            else:
                self.io.output(f"Could not find macro named {macro_identifier}.")
            return CommandHandlerResult(undoable=False)
        elif date_count == 0:
            macro_identifier: str = arguments[0]
            arguments_to_process: list[str] = arguments[1:]

            macro_arguments: list[str] = []
            command_text_starts_at: int = 0
            for index, argument in enumerate(arguments_to_process):
                if not re.match(r"^<[^<>]+>$", argument):
                    command_text_starts_at = index
                    break
                else:
                    macro_arguments.append(argument)

            command_text: str = " ".join(arguments_to_process[command_text_starts_at:])

            # TODO check if macro_identifier is equal to an existing command or its abbreviation
            default_values: list[any] = [] # TODO duplicated code via MacroManager
            parsed_arguments: list[str] = []
            for argument in macro_arguments:
                if "=" in argument: # TODO arguments with '=' must be after arguments without it
                    name, value = argument[1:-1].split("=", 1)
                    default_values.append(value)
                    parsed_arguments.append(f"{name}")
                else:
                    default_values.append(None)
                    parsed_arguments.append(argument[1:-1])

            macro: MacroTemplate = MacroTemplate(
                identifier=macro_identifier,
                raw=f"{macro_identifier} {' '.join(macro_arguments)} | {command_text}",
                command_text=command_text,
                arguments=parsed_arguments,
                default_argument_values=default_values,
            )
            MacroManager.update_macro(macro)
            MacroManager.save_macros_file()
            return CommandHandlerResult(undoable=False)
        else: # date_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
