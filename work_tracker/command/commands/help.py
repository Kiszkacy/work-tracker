from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.command_manager import CommandManager
from work_tracker.command.command_parser import CommandParser
from work_tracker.command.common import CommandArgument, Command
from work_tracker.common import Date, ReadonlyAppState, Mode
from work_tracker.config import Config
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorCustom, CommandErrorInvalidDateCount
from work_tracker.text.common import wrap_text, Color, frame_text, strip_ansi


class HelpHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count == 0 and argument_count == 0:
            descriptions: list[str] = []
            longest_command_name_size: int = max(len(command.name) for command in CommandManager.commands)
            for index, command in enumerate(CommandManager.commands):
                space_padding: str = " " * (longest_command_name_size - len(command.name) + Config.data.command.help.command_list_description_padding)
                wrapped_description: str = wrap_text(
                    text=command.help.short_help_description,
                    indent=f"{' ' * (longest_command_name_size + Config.data.command.help.command_list_description_padding)}",
                    omit_first_line_indent=True,
                    frame_wrap=True
                )

                if command.name in ["block", "calculate", "info", "recalculate", "setup"]:
                    color = Color.Red if index % 2 == 1 else Color.Brightred
                elif index % 2 == 1:
                    color = Color.Brightblack
                else:
                    color = Color.Reset
                descriptions.append(f"{color.value}{command.name}{space_padding}{wrapped_description}")

            wrapped_text: str = "\n".join(descriptions)
            wrapped_footer_text: str = wrap_text(
                text=(
                    f" Commands not yet implemented are marked by {Color.Brightred.value}red{Color.Reset.value} color."
                    f"\nType {Color.Brightblue.value}help <command_name>{Color.Reset.value} to display detailed help description about a specific command."
                ).strip(),
                frame_wrap=True
            )

            longest_line_width: int = max([len(strip_ansi(line)) for line in wrapped_text.splitlines()] + [len(strip_ansi(line)) for line in wrapped_footer_text.splitlines()])

            framed_text: str = frame_text(
                text=wrapped_text,
                title="Commands",
                title_color=Color.Bold,
                skip_bottom_line=True,
                minimal_line_width=longest_line_width
            )
            framed_footer_text: str = frame_text(
                text=wrapped_footer_text,
                extend_top_line=True,
                minimal_line_width=longest_line_width
            )
            self.io.write(framed_text)
            self.io.output(framed_footer_text)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            command: Command | None = CommandParser.find_matching_command(arguments[0])
            if command is None:
                return CommandHandlerResult(undoable=False, error=CommandErrorCustom(self.command_name, custom_message=f"Command named {arguments[0]} was not found."))

            modes: list[Mode] = [Mode.Today, Mode.Day, Mode.Month]  # explicit list to define custom order of values
            modes_text: str = " | ".join([f"{(Color.Green if mode in command.supported_modes else Color.Red).value}{mode.name}{Color.Reset.value}" for mode in modes])
            usage_text: str = f"Supported modes: {modes_text}"

            if len(command.help.use_case_description) != 1:
                for index, use_case in enumerate(command.help.use_case_description):
                    space_padding: str = " " * (Config.data.command.help.command_use_case_description_padding)
                    supported_modes_text: str = "|".join([f"{(Color.Green if mode in use_case.supported_modes else Color.Red).value}{mode.name[0].upper()}{Color.Reset.value}" for mode in modes])
                    wrapped_description: str = wrap_text(
                        text=use_case.description,
                        width=Config.data.output.max_width,
                        indent=f"{space_padding}",
                        frame_wrap=True
                    )

                    usage_text += f"\n\n{Color.Reset.value}{' ' * Config.data.command.help.command_use_case_indent_size}{Config.data.command.help.command_use_case_bullet_point_symbol}{supported_modes_text} {Color.Bold.value}{use_case.template}"
                    usage_text += f"\n{Color.Brightblack.value}{wrapped_description}"

            description_text: str = command.help.full_help_description
            wrapped_description_text: str = wrap_text(
                text=description_text,
                frame_wrap=True
            )
            wrapped_usage_text: str = wrap_text(
                text=usage_text,
                frame_wrap=True
            )
            longest_line_width: int = max([len(strip_ansi(line)) for line in wrapped_description_text.splitlines()] + [len(strip_ansi(line)) for line in wrapped_usage_text.splitlines()])

            framed_description_text: str = frame_text(
                text=wrapped_description_text,
                title=command.help.full_use_case_template,
                title_color=Color.Bold,
                skip_bottom_line=True,
                minimal_line_width=longest_line_width
            )
            framed_usage_text: str = frame_text(
                text=wrapped_usage_text,
                title="Usage",
                title_color=Color.Bold,
                center_title=True,
                extend_top_line=True,
                minimal_line_width=longest_line_width
            )

            self.io.write(framed_description_text)
            self.io.output(framed_usage_text)
            return CommandHandlerResult(undoable=False)
        elif date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        else: # argument_count > 1
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

