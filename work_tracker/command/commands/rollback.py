import datetime
import os

from work_tracker.checkpoint_manager import CheckpointManager, CheckpointTemplate
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument, AdditionalInputArgument
from work_tracker.common import Date, ReadonlyAppState, AppData
from work_tracker.config import Config
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount
from work_tracker.text.common import Color, wrap_text, frame_text, strip_ansi


class RollbackHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 1 and isinstance(arguments[0], str):
            checkpoint_identifier: str = arguments[0]
            matches: list[CheckpointTemplate] = self._find_checkpoint_by_name(checkpoint_identifier)

            if len(matches) == 0:
                self.io.output(f"Could not find a checkpoint named {checkpoint_identifier}.")
                return CommandHandlerResult(undoable=False)
            elif len(matches) == 1:
                return self._load_checkpoint(matches[0])
            else:
                return self._prompt_selection(matches, checkpoint_identifier)

        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

    def _find_checkpoint_by_name(self, name: str) -> list[CheckpointTemplate]:
        matches: list[CheckpointTemplate] = []

        for checkpoint in CheckpointManager.checkpoints():
            if not checkpoint.name.startswith(CheckpointManager.usermade_checkpoint_prefix):
                continue

            checkpoint_name: str = checkpoint.name.removeprefix(CheckpointManager.usermade_checkpoint_prefix)
            if checkpoint_name == name:
                matches.append(checkpoint)

        return sorted(matches, key=lambda m: os.path.getctime(m.path))

    def _load_checkpoint(self, checkpoint: CheckpointTemplate) -> CommandHandlerResult:
        data: AppData = CheckpointManager.load(
            checkpoint.full_identifier,
            persistent_checkpoint=checkpoint.persistent
        )
        if data is None:
            self.io.output(f"Failed to load checkpoint {checkpoint.name}.")
            return CommandHandlerResult(undoable=False)
        self.data.copy_from(data)
        return CommandHandlerResult(undoable=True)

    def _display_found_checkpoints(self, matches: list[CheckpointTemplate], checkpoint_identifier: str):
        formatted_dates: list[str] = [
            match.date if match.date == "-" else datetime.datetime.strptime(match.date, "%Y-%m-%d_%H-%M-%S").strftime("%d-%m-%Y %H:%M:%S")
            for match in matches
        ]

        longest_index_size: int = len(str(len(matches)))
        longest_date_size: int = max((len(date) for date in formatted_dates), default=0)
        separator: str = " | "

        lines: list[str] = []
        for index, match in enumerate(matches):
            index_padded: str = str(index + 1).ljust(longest_index_size)
            date_padded: str = formatted_dates[index].ljust(longest_date_size)
            type_: str = "temporary" if not match.persistent else "permanent"
            if not match.persistent:
                color: str = Color.Red.value if index % 2 == 1 else Color.Brightred.value
            else:
                color: str = Color.Brightblack.value if index % 2 == 1 else Color.Reset.value

            indent_size: int = longest_index_size + len(separator) + longest_date_size + len(separator)
            indent: str = " " * indent_size

            wrapped_type: str = wrap_text(
                text=type_,
                indent=indent,
                omit_first_line_indent=True,
                frame_wrap=True
            )
            lines.append(f"{color}{index_padded}{separator}{date_padded}{separator}{wrapped_type}{Color.Reset.value}")

        text: str = "\n".join(lines)

        footer_text: str = wrap_text(
            text=(
                f"Found {len(matches)} checkpoints named {Color.Brightblue.value}{checkpoint_identifier}{Color.Reset.value}."
                f" Type a checkpoint's number to load it or type {Color.Brightblue.value}quit{Color.Reset.value} to cancel."
            ),
            frame_wrap=True
        )

        text_lines_len: list[int] = [len(strip_ansi(line)) for line in text.splitlines()]
        footer_lines_len: list[int] = [len(strip_ansi(line)) for line in footer_text.splitlines()]
        longest_line_width: int = max(text_lines_len + footer_lines_len, default=0)

        framed_text: str = frame_text(
            text=text,
            title="Matching checkpoints",
            title_color=Color.Bold,
            skip_bottom_line=True,
            minimal_line_width=longest_line_width
        )
        framed_footer: str = frame_text(
            text=footer_text,
            extend_top_line=True,
            minimal_line_width=longest_line_width
        )

        self.io.write(framed_text)
        self.io.output(framed_footer)

    def _prompt_selection(self, matches: list[CheckpointTemplate], checkpoint_identifier: str) -> CommandHandlerResult:
        valid_indices: list[str] = [str(i + 1) for i in range(len(matches))]

        while True:
            self._display_found_checkpoints(matches, checkpoint_identifier)
            user_input: list[AdditionalInputArgument] = self.get_additional_input(custom_autocomplete=valid_indices + ["quit"])
            if len(user_input) != 1:
                continue

            if isinstance(user_input[0], int) and 1 <= user_input[0] <= len(matches):
                return self._load_checkpoint(matches[user_input[0]-1])
            elif isinstance(user_input[0], str):
                word: str = user_input[0].lower()
                if "quit".startswith(word):
                    return CommandHandlerResult(undoable=False)
                else:
                    self.io.output("Unknown command.", color=Color.from_key(Config.data.output.error_color))
            else:
                self.io.output("Please enter a valid checkpoint number.", color=Color.from_key(Config.data.output.error_color))
