from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorInvalidDateCount
from work_tracker.text.common import Color, wrap_text, frame_text, strip_ansi


class HistoryHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            raw_texts: list[str] = [state.command for state in state.states]

            longest_index_size: int = len(str(len(state.states))) # could just use log10 here

            # TODO add ellipsis here and in other places modifiable by user (custom methods in the future)
            # TODO what if definition is very long => solution: set max length in config and add ellipsis if its too long
            seperator: str = " | " # TODO make seperator configurable
            state_texts: list[str] = []
            for index, command_text in enumerate(raw_texts):
                command_wrapped: str = wrap_text(
                    text=command_text,
                    indent=" " * (longest_index_size + len(seperator)),
                    omit_first_line_indent=True,
                    frame_wrap=True
                )

                if index == state.current_state_index:
                    color = Color.Brightblue
                elif index % 2 == 1:
                    color = Color.Brightblack
                else:
                    color = Color.Reset
                state_texts.append(f"{color.value}{str(index+1).rjust(longest_index_size)}{seperator}{command_wrapped}")

            wrapped_history_text: str = "\n".join(state_texts)
            wrapped_footer_text: str = wrap_text(
                text=f"Current state is marked by {Color.Brightblue.value}blue{Color.Reset.value} color."
            )

            longest_line_width: int = max([len(strip_ansi(line)) for line in wrapped_history_text.splitlines()] + [len(strip_ansi(line)) for line in wrapped_footer_text.splitlines()])

            framed_text: str = frame_text(
                text=wrapped_history_text,
                title="State history",
                title_color=Color.Bold,
                skip_bottom_line=True,
                minimal_line_width=longest_line_width
            )
            framed_footer: str = frame_text(
                text=wrapped_footer_text,
                extend_top_line=True,
                minimal_line_width=longest_line_width
            )
            self.io.write(framed_text)
            self.io.output(framed_footer)
            return CommandHandlerResult(undoable=False)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
