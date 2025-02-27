import pyperclip

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, AdditionalInputArgument
from work_tracker.command.common import KeyManager
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount
from work_tracker.text.common import Color


class KeyHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            self.io.output(
                text="Generated keys can be quite long. Do you want to copy it into a clipboard instead of displaying it in a terminal?",
                color=Color.Brightred,
            )
            while True:
                sub_arguments: list[AdditionalInputArgument] = self.get_additional_input(custom_autocomplete=["yes", "no", "quit"])
                if len(sub_arguments) != 1 or not isinstance(sub_arguments[0], str):
                    continue

                choice: str = sub_arguments[0].lower()
                if "yes".startswith(choice):
                    pyperclip.copy(KeyManager.encode(self.data))
                    break
                elif "no".startswith(choice):
                    self.io.output(KeyManager.encode(self.data))
                    break
                elif "quit".startswith(choice):
                    break
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            self.data.copy_from(KeyManager.decode(arguments[0]))
            return CommandHandlerResult(undoable=True)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
