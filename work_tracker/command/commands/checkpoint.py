import datetime
import re

from work_tracker.checkpoint_manager import CheckpointManager
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount
from work_tracker.text.common import Color, wrap_text, frame_text


class CheckpointHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            checkpoints: list[tuple[str, str]] = []
            for index, checkpoint_path in enumerate(CheckpointManager.all_manual_checkpoints()):
                checkpoint_name: str = checkpoint_path.name.removesuffix('.save.checkpoint') # TODO hardcoded '.save.checkpoint'
                match: re.Match = re.search(r'__(?!.*__)', checkpoint_name)
                checkpoints.append((checkpoint_name[:match.start()], checkpoint_name[match.end():]))
            if len(checkpoints) == 0:
                self.io.output(f"No checkpoints were yet created, create one via {Color.Brightblue.value}checkpoint <name>{Color.Reset.value}.")
                return CommandHandlerResult(undoable=False)

            sorted_checkpoints_by_time: list[tuple[str, str]] = sorted(checkpoints, key=lambda checkpoint: checkpoint[1])

            seperator: str = " | " # TODO make seperator configurable
            checkpoints_text: list[str] = [
                f"{Color.Brightblack.value if index % 2 == 1 else Color.Reset.value}{date.replace('-', ':')}{seperator}{identifier}"
                for index, (identifier, date) in enumerate(sorted_checkpoints_by_time)
            ]
            wrapped_text: str = wrap_text(
                text="\n".join(checkpoints_text),
                frame_wrap=True,
            )
            framed_text: str = frame_text(
                text=wrapped_text,
                title="Checkpoints",
                title_color=Color.Bold
            )
            self.io.output(framed_text)

            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            checkpoint_identifier: str = arguments[0]
            CheckpointManager.save(checkpoint_identifier, self.data, manual_checkpoint=True)
            return CommandHandlerResult(undoable=False)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
