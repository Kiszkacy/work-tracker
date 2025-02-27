from prompt_toolkit.completion import WordCompleter, CompleteEvent
from prompt_toolkit.document import Document

from work_tracker.command.command_manager import CommandManager
from work_tracker.common import month_map
from work_tracker.config import Config


# TODO make it work on backspace (might not be possible)
class InputCommandCompleter(WordCompleter):
    def __init__(self):
        self.active: bool = True
        self.custom_autocomplete: bool = False
        self._commands: list[str] = [command.name for command in CommandManager.commands]
        super().__init__(self._commands, ignore_case=True)

    def get_completions(self, document: Document, complete_event: CompleteEvent): # TODO add macros hinting ? + add variable hinting when using commands via 'full_use_case_template'
        if not self.active:
            return []
        if self.custom_autocomplete:
            return super().get_completions(document, complete_event)

        words: list[str] = (document.text.split(Config.data.input.command_chain_symbol)[-1]).split()

        # TODO rework this shit wtf bro
        is_whitespace_last: bool = len(document.text) != 0 and document.text[-1] == " "
        words_to_check_for_command: list[str] = words if is_whitespace_last else words[:-1]
        command_already_typed: bool = \
            any([((any([word == abbreviation for abbreviation in command.abbreviations]) or (word.startswith(command.shortest_valid_string) and word in command.name)) and word not in month_map) for command in CommandManager.commands for word in words_to_check_for_command]) \
            and (len(words) > 1 or (len(words) == 1 and document.text[-1] == " "))
        only_help_command_typed: bool = \
            ((len(words) == 2 and document.text[-1] != " ") or (len(words) == 1 and is_whitespace_last)) \
            and "help".startswith(words[0]) \
            and words[0].startswith(CommandManager.get_command_by_name("help").shortest_valid_string)

        if not only_help_command_typed and command_already_typed:
            return []
        else:
            return super().get_completions(document, complete_event)

    def activate_custom_autocomplete(self, autocomplete_list: list[str]):
        self.words = autocomplete_list
        self.custom_autocomplete = True

    def deactivate_custom_autocomplete(self):
        self.words = self._commands
        self.custom_autocomplete = False
