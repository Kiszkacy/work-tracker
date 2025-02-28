from work_tracker.command.command_initializer import CommandInitializer
from work_tracker.command.common import Command, TimeArgument, CommandHelp, _global_command_templates
from work_tracker.common import Mode, classproperty


class CommandManager:
    _commands: list[Command] = []

    # special commands
    _time_command: Command = Command(
        help=CommandHelp(
            full_use_case_template="",
            short_help_description="",
            full_help_description="",
            use_case_description=[],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        name="__time",
        shortest_valid_string="",
        snake_case_name="__time",
        camel_case_name="__Time",
        valid_argument_types=[[TimeArgument]]
    )
    _date_command: Command = Command(
        help=CommandHelp(
            full_use_case_template="",
            short_help_description="",
            full_help_description="",
            use_case_description=[],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        name="__date",
        shortest_valid_string="",
        snake_case_name="__date",
        camel_case_name="__Date",
        valid_argument_types=[[]]
    )
    _macro_execute_command: Command = Command(
        help=CommandHelp(
            full_use_case_template="",
            short_help_description="",
            full_help_description="",
            use_case_description=[],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        name="__macro",
        shortest_valid_string="",
        snake_case_name="__macro",
        camel_case_name="__Macro",
        valid_argument_types=[[object, ...]]
    )

    @classproperty
    def time_command(cls) -> Command:
        return cls._time_command

    @classproperty
    def date_command(cls) -> Command:
        return cls._date_command

    @classproperty
    def macro_execute_command(cls) -> Command:
        return cls._macro_execute_command

    @classproperty
    def commands(cls) -> list[Command]:
        if len(cls._commands) == 0:
            cls._commands = CommandInitializer.initialize_commands(_global_command_templates)
        return cls._commands

    @classmethod
    def get_command_by_name(cls, name: str) -> Command | None:
        filtered_commands: list[Command] = [command for command in cls.commands if command.name == name]
        command_found: bool = len(filtered_commands) == 1
        if command_found:
            return filtered_commands[0]
        else:
            return None
