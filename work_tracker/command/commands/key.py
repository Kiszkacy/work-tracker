import pyperclip
from prompt_toolkit.completion import Completion

from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, AdditionalInputArgument, CompletionCandidate, CompletionHint
from work_tracker.command.common import KeyManager
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount
from work_tracker.text.common import Color


class KeyHandler(CommandHandler):
    @classmethod
    def get_completions(cls, typed_words: list[str], last_word: str, in_subcommand_mode: bool) -> list[Completion | CompletionCandidate]:
        if not in_subcommand_mode and len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate("<key>", "optional argument, provide to load app state from the key"), CompletionCandidate(CompletionHint.Chain)], last_word)
        if in_subcommand_mode and len(typed_words) == 0:
            return cls.get_fitting_completions([CompletionCandidate("yes"), CompletionCandidate("no"), CompletionCandidate("quit")], last_word)
        return []

    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            self.io.output(
                text="Generated keys can be thousands of characters long. Do you want to copy it into a clipboard instead of displaying it in a terminal?",
                color=Color.Brightred,
            )
            self.enter_subcommand_mode()
            while True:
                sub_arguments: list[AdditionalInputArgument] = self.get_additional_input()
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
            self.exit_subcommand_mode()
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            self.data.copy_from(KeyManager.decode(arguments[0]))
            return CommandHandlerResult(undoable=True)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
