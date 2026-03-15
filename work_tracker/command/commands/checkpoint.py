import datetime
import os
import re
from dataclasses import dataclass

from path import Path

from work_tracker.checkpoint_manager import CheckpointManager
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount, CommandErrorInvalidArgumentValue
from work_tracker.text.common import Color, wrap_text, frame_text, strip_ansi


@dataclass(frozen=True)
class CheckpointTemplate:
    path: Path
    name: str
    date: str
    persistent: bool

# TODO: fix rollback
# TODO: handle same name checkpoints

class CheckpointHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            checkpoints: list[CheckpointTemplate] = []
            for index, checkpoint_path in enumerate([checkpoint for checkpoint in CheckpointManager.all_temporary_checkpoints() if checkpoint.name.startswith("user.")]): # TODO hardcoded 'user.'
                raw_name: str = checkpoint_path.name.removesuffix('.save.checkpoint') # TODO hardcoded '.save.checkpoint'
                match: re.Match = re.match(r"user\.(.+?)__(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", raw_name)
                if match:
                    name: str = match.group(1)
                    date: str = match.group(2)
                else:
                    name: str = raw_name
                    date: str = "-"
                checkpoints.append(CheckpointTemplate(
                    path=checkpoint_path,
                    name=name,
                    date=date,
                    persistent=False
                ))
            for index, checkpoint_path in enumerate([checkpoint for checkpoint in CheckpointManager.all_persistent_checkpoints() if checkpoint.name.startswith("user.")]):
                raw_name: str = checkpoint_path.name.removesuffix('.save.checkpoint') # TODO hardcoded '.save.checkpoint'
                match: re.Match = re.match(r"user\.(.+?)__(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", raw_name)
                if match:
                    name: str = match.group(1)
                    date: str = match.group(2)
                else:
                    name: str = raw_name
                    date: str = "-"
                checkpoints.append(CheckpointTemplate(
                    path=checkpoint_path,
                    name=name,
                    date=date,
                    persistent=True
                ))
            if len(checkpoints) == 0:
                self.io.output(f"No checkpoints were yet created, create one via {Color.Brightblue.value}checkpoint <name>{Color.Reset.value}.")
                return CommandHandlerResult(undoable=False)

            sorted_checkpoints_by_time: list[CheckpointTemplate] = sorted(checkpoints, key=lambda checkpoint: os.path.getctime(checkpoint.path)) # TODO this sorting might be unclear for user

            formatted_dates: list[str] = [
                checkpoint.date if checkpoint.date == "-" else datetime.datetime.strptime(checkpoint.date, "%Y-%m-%d_%H-%M-%S").strftime("%d-%m-%Y %H:%M:%S")
                for checkpoint in sorted_checkpoints_by_time
            ]

            longest_index_size: int = len(str(len(sorted_checkpoints_by_time))) if sorted_checkpoints_by_time else 1
            longest_date_size: int = max((len(date) for date in formatted_dates), default=0)

            separator: str = " | " # TODO make separator configurable
            checkpoints_text: list[str] = []

            for index, checkpoint in enumerate(sorted_checkpoints_by_time):
                index_padded: str = str(index + 1).ljust(longest_index_size)
                date_padded: str = formatted_dates[index].ljust(longest_date_size)

                indent_size: int = longest_index_size + len(separator) + longest_date_size + len(separator)
                indent: str = " " * indent_size

                wrapped_name: str = wrap_text(
                    text=checkpoint.name,
                    indent=indent,
                    omit_first_line_indent=True,
                    frame_wrap=True
                )

                is_temporary: bool = not checkpoint.persistent
                if is_temporary:
                    color: str = Color.Red.value if index % 2 == 1 else Color.Brightred.value
                else:
                    color: str = Color.Brightblack.value if index % 2 == 1 else Color.Reset.value

                checkpoints_text.append(
                    f"{color}{index_padded}{color}{separator}{date_padded}{color}{separator}{wrapped_name}"
                )

            wrapped_text: str = "\n".join(checkpoints_text)

            footer_text: str = wrap_text(
                text=f"Checkpoints in {Color.Red.value}red{Color.Reset.value} are temporary and will be automatically deleted after exiting the app.",
                frame_wrap=True
            )

            wrapped_lines_len: list[int] = [len(strip_ansi(line)) for line in wrapped_text.splitlines()]
            footer_lines_len: list[int] = [len(strip_ansi(line)) for line in footer_text.splitlines()]
            longest_line_width: int = max(wrapped_lines_len + footer_lines_len, default=0)

            framed_text: str = frame_text(
                text=wrapped_text,
                title="Checkpoints",
                title_color=Color.Bold,
                skip_bottom_line=True,
                minimal_line_width=longest_line_width
            )
            framed_footer_text: str = frame_text(
                text=footer_text,
                extend_top_line=True,
                minimal_line_width=longest_line_width
            )

            self.io.write(framed_text)
            self.io.output(framed_footer_text)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            checkpoint_identifier: str = arguments[0]
            CheckpointManager.save(checkpoint_identifier, self.data, persistent_checkpoint=False, add_suffix_timestamp=True, created_by_user=True)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 2:
            if not "permanent".startswith(arguments[1]):
                return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentValue(self.command_name, received_value=arguments[1], expected_value="permanent"))
            checkpoint_identifier: str = arguments[0]
            CheckpointManager.save(checkpoint_identifier, self.data, persistent_checkpoint=True, add_suffix_timestamp=True, created_by_user=True)
            return CommandHandlerResult(undoable=False)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
