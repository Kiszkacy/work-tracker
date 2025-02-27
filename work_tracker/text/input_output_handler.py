from pathlib import Path

import colorama
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from work_tracker.common import get_data_path
from work_tracker.config import Config
from work_tracker.text.common import TextWriter, wrap_text, Color
from work_tracker.text.input_command_completer import InputCommandCompleter


class InputOutputHandler:
    def __init__(self):
        colorama.init()
        self._writer: TextWriter = TextWriter()
        self.session: PromptSession = PromptSession(history=FileHistory(get_data_path().joinpath("cmd-history")))
        self.command_completer: InputCommandCompleter = InputCommandCompleter()
        self._truncate_history()

    @staticmethod
    def _truncate_history():
        history_path: Path = get_data_path().joinpath("cmd-history")
        if not history_path.exists():
            return

        with open(history_path, "r") as file:
            lines: list[str] = file.readlines()

        with open(history_path, "w", newline="\n") as file:
            file.writelines(lines[-50*3:]) # TODO config max history size constant, 3 size of one command

    def input(self, prefix: str, show_autocomplete: bool = True, custom_autocomplete: list[str] = None) -> str:
        if custom_autocomplete is not None:
            self.command_completer.activate_custom_autocomplete(custom_autocomplete)

        self.command_completer.active = show_autocomplete
        user_input: str = self.session.prompt(prefix, completer=self.command_completer)

        if custom_autocomplete is not None:
            self.command_completer.deactivate_custom_autocomplete()

        return user_input

    def write(self, text: str = "", color: Color = None, end: str = "\n") -> TextWriter:
        return self._writer.write(text + end, color)

    def output(self, text: str = "", color: Color = None, end: str = "\n"):
        if text is not None:
            self.write(text, color, end="")
        wrapped_text: str = wrap_text(text=self._writer.text, width=Config.data.output.max_width)
        print(wrapped_text, end=end)
        self._writer.clear()
