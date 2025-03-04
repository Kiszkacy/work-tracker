import base64
import lzma
import pickle
from dataclasses import dataclass
from enum import Enum, auto
from types import UnionType

from work_tracker.common import AppData, Date, Mode
# from work_tracker.error import ParserError
from work_tracker.text.common import Color


class TimeArgumentType(Enum):
    Overwrite = auto()
    Add = auto()
    Subtract = auto()


@dataclass(frozen=True)
class TimeArgument:
    minutes: int
    type: TimeArgumentType


Number: UnionType = int | float
CommandArgument: UnionType = Number | str | TimeArgument
SimpleTypeArgument: UnionType = Number | str
AdditionalInputArgument: UnionType = Number | str | TimeArgument | Date


@dataclass(frozen=True)
class CommandUseCaseDescription:
    supported_modes: set[Mode]
    template: str
    description: str


@dataclass(frozen=True)
class CommandHelp:
    full_use_case_template: str
    short_help_description: str
    full_help_description: str
    use_case_description: list[CommandUseCaseDescription]


@dataclass(frozen=True)
class CommandTemplate:
    name: str
    help: CommandHelp
    supported_modes: set[Mode]
    abbreviations: list[str]
    valid_argument_types: list[list[type]]


@dataclass(frozen=True)
class Command(CommandTemplate):
    shortest_valid_string: str
    snake_case_name: str
    camel_case_name: str


@dataclass(frozen=True)
class CommandQuery:
    command: Command
    dates: list[Date]
    date_count: int
    arguments: list[CommandArgument]
    argument_count: int
    raw_text: str


@dataclass(frozen=True)
class ParseResult:
    queries: list[CommandQuery]
    # error: ParserError | None = None
    # TODO had to remove ParserError typehint due to circular imports, fix it in the future
    error: any = None


class KeyManager: # TODO shorten codes
    @staticmethod
    def encode(data: AppData) -> str:
        pickled_data: bytes = pickle.dumps(data)
        compressed_data: bytes = lzma.compress(pickled_data)
        return base64.b64encode(compressed_data).decode()

    @staticmethod
    def decode(key: str) -> AppData:
        compressed_data: bytes = base64.b64decode(key)
        pickled_data: bytes = lzma.decompress(compressed_data)
        return pickle.loads(pickled_data)


_global_command_templates: list[CommandTemplate] = [
    CommandTemplate(
        name="block",
        help=CommandHelp(
            full_use_case_template="block",
            short_help_description="Prevents a date from being reset during recalculation",
            full_help_description=(
                " Marks the date as blocked, ensuring that its data is preserved when running 'calculate' or 'recalculate'."
                " Both commands will skip resetting a blocked date, preserving its existing values while still updating the rest of the schedule."
                " This allows you to protect specific dates from being overwritten while still updating the rest of the schedule automatically."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "block", ""),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="calendar",
        help=CommandHelp(
            full_use_case_template="calendar",
            short_help_description="Displays the calendar for the month",
            full_help_description=(
                " Displays the calendar for the month corresponding to the given date."
                " Dates are marked using a color-coded legend which can be easily configured via 'config' command,"
                " this provides a clear distinction between different types of days."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "calendar", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="calculate",
        help=CommandHelp(
            full_use_case_template="calculate",
            short_help_description="Calculates the schedule based on the setup parameters",
            full_help_description=(
                " Calculates the work schedule for the given month according to the parameters set during the setup process."
                " This is a 'hard reset' of the data, meaning that any previously entered data for specific dates will be overwritten."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "calculate", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="checkpoint",
        help=CommandHelp(
            full_use_case_template="checkpoint [name]",
            short_help_description="Creates or lists available checkpoints",
            full_help_description=(
                " Allows you to create a checkpoint which represents a saved state of the app."
                " If no argument is provided, it lists all available checkpoints in current session."
                " If a checkpoint name is provided, it creates or overwrites a checkpoint with that name."
                " Checkpoints are session-specific and are deleted when the app is closed, meaning they only exist until you exit the app."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "checkpoint", "lists all available checkpoints"),
                CommandUseCaseDescription(set(Mode), "checkpoint <name>", "creates or overwrites a checkpoint with the given name"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [str]],
    ),
    CommandTemplate(
        name="clear",
        help=CommandHelp(
            full_use_case_template="clear [month]",
            short_help_description="Resets a date to its initial state",
            full_help_description=(
                " Resets the given date to its initial state, as it was when first initialized."
                " If called within a context of a month, it resets all dates within that month to their default state."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "clear", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=["reset"],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="config",
        help=CommandHelp(
            full_use_case_template="config [key] [value]",
            short_help_description="Displays or modifies the configuration settings",
            full_help_description=(
                " Displays the entire configuration structure if no arguments are provided."
                " When used with a single argument, it looks for the specified key in the configuration and shows its value or its sub-settings."
                " If two arguments are provided, it updates the specified setting with a new value."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "config", "displays the entire configuration structure"),
                CommandUseCaseDescription(set(Mode), "config <key>", "shows the value or sub-settings for the specified key"),
                CommandUseCaseDescription(set(Mode), "config <key> <value>", "updates the specified setting with the new value"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [str], [str, SimpleTypeArgument]],
    ),
    CommandTemplate(
        name="dayoff",
        help=CommandHelp(
            full_use_case_template="dayoff",
            short_help_description="Marks a date as a day off.",
            full_help_description=(
                " Marks a date as a day off. When used within the context of a specific month it will mark all dates containing work as days off within that month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "dayoff", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=["offday"],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="days",
        help=CommandHelp(
            full_use_case_template="days ['remote'|'office'] <minutes> ['clean']",
            short_help_description="Calculates the number of days needed to meet the monthly target work time",
            full_help_description=(
                " Calculates the number of days required to reach the total work time while matching the daily work time as closely as possible to the provided amount."
                " If no additional parameters are given, it calculates the required number of days based on the total work time specified."
                " If 'remote' or 'office' is specified as the first argument, the calculation is limited to that specific type of work."
                " If the 'clean' argument is included, the calculation ignores any previously logged work time and assumes a clean month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "days <minutes>", "calculates the number of days required to reach the monthly target work time while keeping daily work time as close as possible to the given amount"),
                CommandUseCaseDescription(set(Mode), "days <'office'|'remote'> <minutes>", "calculates the required number of days, limited to remote or office work"),
                CommandUseCaseDescription(set(Mode), "days <minutes> 'clean'", "calculates the required number of days, ignoring already logged work time in a month"),
                CommandUseCaseDescription(set(Mode), "days <'office'|'remote'> <minutes> 'clean'", "calculates the required number of days, limited to remote or office work, while ignoring already logged work time in a month"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[TimeArgument], [str, TimeArgument], [TimeArgument, str], [str, TimeArgument, str]],
    ),
    CommandTemplate(
        name="deletemacro",
        help=CommandHelp(
            full_use_case_template="deletemacro <name>",
            short_help_description="Deletes the specified macro",
            full_help_description=(
                " Deletes the macro identified by the given name."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "deletemacro <name>", "deletes the macro with the specified name"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[str]],
    ),
    CommandTemplate(
        name="done",
        help=CommandHelp(
            full_use_case_template="done",
            short_help_description="Sets the time spent at work to match the target time",
            full_help_description=(
                " Sets the time spent at work to the value of the target time, which can be displayed using the 'target' command."
                " This command is useful for quickly aligning your time worked with the preset target, without needing to manually adjust the time."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "done", ""),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="end",
        help=CommandHelp(
            full_use_case_template="end [time]",
            short_help_description="Marks the end of work and records the time spent at work",
            full_help_description=(
                " Marks the end of work to track time spent at work. If no time is provided, it uses the current system time."
                " If a time is provided, it sets that as the end time."
                " This command works together with the 'start' command to calculate the total time worked by subtracting the start time from the end time."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "end", "marks the end of work at the current system time."),
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "end <time>", "marks the end of work at the specified time."),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[], [TimeArgument]],
    ),
    CommandTemplate(
        name="exit",
        help=CommandHelp(
            full_use_case_template="exit",
            short_help_description="Exits the current mode or application",
            full_help_description=(
                " Exits the app and saves the data if you are currently working in the today mode. "
                " If you're working within the context of any other date, it will switch you back to the today mode."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "exit", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="fte",
        help=CommandHelp(
            full_use_case_template="fte [value]",
            short_help_description="Displays or modifies the full-time equivalent (FTE)",
            full_help_description=(
                " Displays the full-time equivalent (FTE) for the month corresponding to the given date."
                " If an argument is provided, it updates the FTE for that month accordingly."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "fte", "displays the full-time equivalent (FTE) for the month corresponding to the given date."),
                CommandUseCaseDescription(set(Mode), "fte <value>", "sets the full-time equivalent (FTE) for the month based on the provided value."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [Number]],
    ),
    CommandTemplate(
        name="help",
        help=CommandHelp(
            full_use_case_template="help (command-name)",
            short_help_description="Displays a list of all commands with short descriptions or detailed help for a specific command.",
            full_help_description=(
                " Displays a list of all available commands along with short descriptions. "
                " Alternatively, 'help <command-name>' can be used to get detailed information about a specific command."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "help", "displays a list of all commands with short descriptions."),
                CommandUseCaseDescription(set(Mode), "help <command-name>", "displays detailed information about a specific command."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=["commands", "list", "menu", "options"],
        valid_argument_types=[[], [str]],
    ),
    CommandTemplate(
        name="history",
        help=CommandHelp(
            full_use_case_template="history",
            short_help_description="Displays the history of undo and redo actions",
            full_help_description=(
                " Displays a history of actions that can be undone or redone, showing the commands that altered the app's state."
                " Currently active state is marked by the blue color."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "history", "displays the history of actions that can be undone or redone."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=["undos", "redos"],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="holiday",
        help=CommandHelp(
            full_use_case_template="holiday",
            short_help_description="Marks a date as a holiday",
            full_help_description=(
                " Marks a date as a holiday. As a result, this date is no longer treated as a workday, even if it was marked as one before."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "holiday", ""),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="info",
        help=CommandHelp(
            full_use_case_template="info",
            short_help_description="Displays detailed information for a specific date",
            full_help_description=(
                " Displays all relevant information for a given date, including the time worked, target time, and various attributes such as "
                " whether the day is marked as a holiday, workday, remote or office work, or a day off."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "info", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="key",
        help=CommandHelp(
            full_use_case_template="key [value]",
            short_help_description="Generates a unique key for the current data or loads data from a given key",
            full_help_description=(
                " If no argument is provided, a unique key representing the current state of the data is generated."
                " If a value (key) is provided, it loads and overwrites the current data with the data associated with that key."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "key", "generates a unique key representing the current state of data."),
                CommandUseCaseDescription(set(Mode), "key <value>", "loads and overwrites the current data with the data from the specified key."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [str]],
    ),
    CommandTemplate(
        name="macro",
        help=CommandHelp(
            full_use_case_template="(macro [name]) | (macro {argument} <command_text...>)",
            short_help_description="Displays, updates or creates macros",
            full_help_description=(
                f" Macros act as reusable command sequences, allowing users to define custom methods that execute multiple commands (or other macros) in order."
                f" A macro consists of an identifier (name) and optional or required arguments, which can be used within the command sequence."
                f" Macros can also function as simple aliases for other commands."
                f"\n\nMacro arguments must be specified using the format {Color.Brightblue.value}<argument_name>{Color.Reset.value}, and the first word after the macro identifier (excluding arguments in {Color.Brightblue.value}<>{Color.Reset.value}) marks the beginning of the macro's command sequence."
                f" These arguments can be referenced throughout the sequence by using the format {Color.Brightblue.value}<argument_name>{Color.Reset.value}."
                f"\n\nTo avoid any problems during the macro definition, it is recommended to enclose the entire command sequence of the macro in quotes (single or double)."
                f" For example, defining a macro called {Color.Brightblue.value}custom-help{Color.Reset.value} that runs {Color.Brightblue.value}help{Color.Reset.value} on a user-specified command name (or 'macro' if no name is provided) would look like this:"
                f'\n  {Color.Blue.value}>> {Color.Brightblue.value}macro custom-help <command_name=macro> "help <command_name>"{Color.Reset.value}'
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "macro", "displays all available macros"),
                CommandUseCaseDescription(set(Mode), "macro <name>", "displays the definition of the specified macro"),
                CommandUseCaseDescription(set(Mode), "macro <name> {argument} <command_text...>", "creates or overwrites a macro with the given name"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [str], [str, str, ...]],
    ),
    CommandTemplate(
        name="minutes",
        help=CommandHelp(
            full_use_case_template="minutes ['remote'|'office'] <days> ['clean']",
            short_help_description="Calculates daily work time required to reach the target in a given number of days",
            full_help_description=(
                " Calculates the required daily work time to reach the total monthly work time, based on the target number of days provided."
                " If no additional parameters are given, it calculates the required minutes per day based on the total monthly work time required."
                " If 'remote' or 'office' is specified as the first argument, the calculation is restricted to that specific type of work."
                " If the 'clean' argument is included, the calculation ignores any previously logged work time and assumes a clean month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "minutes <days>", "calculates the daily minutes required to reach the monthly target work time within the given number of days"),
                CommandUseCaseDescription(set(Mode), "minutes <'office'|'remote'> <days>", "calculates required minutes per day, limited to remote or office work"),
                CommandUseCaseDescription(set(Mode), "minutes <days> 'clean'", "calculates required minutes per day, ignoring already logged work time in a month"),
                CommandUseCaseDescription(set(Mode), "minutes <'office'|'remote'> <days> 'clean'", "calculates required minutes per day, limited to remote or office work, while ignoring already logged work time in a month"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[int], [str, int], [int, str], [str, int, str]],
    ),
    CommandTemplate(
        name="office",
        help=CommandHelp(
            full_use_case_template="office",
            short_help_description="Marks a date as office work",
            full_help_description=(
                " Marks a date as office work. As a result, this date is no longer treated as a remote work, even if it was marked as one before."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "office", ""),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="recalculate",
        help=CommandHelp(
            full_use_case_template="recalculate",
            short_help_description="Recalculates the schedule while preserving data before and including the active date",
            full_help_description=(
                " Recalculates the work schedule for the given month based on the parameters set during the setup process."
                " Unlike 'calculate', which performs a 'hard reset' of the entire schedule, 'recalculate' updates only the data"
                " from the next date onward. Any data before and including the active date remains unchanged, ensuring past records"
                " and the current day's data are preserved. "
                " This allows for automatic updates while maintaining consistency with previously recorded work data."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "recalculate", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="redo",
        help=CommandHelp(
            full_use_case_template="redo",
            short_help_description="Re-applies the last undone command that altered the state of the data",
            full_help_description=(
                " Re-applies the last command that was undone and altered the state of the data."
                " The history of commands that can be undone or redone is tracked and can be viewed using the 'history' command."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "redo", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="remote",
        help=CommandHelp(
            full_use_case_template="remote",
            short_help_description="Marks a date as remote work",
            full_help_description=(
                " Marks a date as remote work. As a result, this date is no longer treated as a office work, even if it was marked as one before."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "remote", ""),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="rollback",
        help=CommandHelp(
            full_use_case_template="rollback <checkpoint>",
            short_help_description="Rolls back the app state to a specified checkpoint",
            full_help_description=(
                " Rolls back the app state to a specified checkpoint. A checkpoint is a saved state created by the user using the"
                " 'checkpoint' command. WorkTracker will revert to that state undoing or applying any changes made since"
                " the checkpoint was created, regardless of any actions taken in the meantime."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "rollback <checkpoint>", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[str]],
    ),
    CommandTemplate(
        name="rwr",
        help=CommandHelp(
            full_use_case_template="rwr [value]",
            short_help_description="Displays or modifies the remote work ratio",
            full_help_description=(
                "Displays the current remote work ratio (RWR) for the given date."
                " If called with an argument it sets the remote work ratio to that value for the specified date allowing users to adjust their remote work percentage."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "rwr", "displays the current remote work ratio for the given date."),
                CommandUseCaseDescription(set(Mode), "rwr <value>", "sets the remote work ratio to the specified value for the given date."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [Number]],
    ),
    CommandTemplate(
        name="setup",
        help=CommandHelp(
            full_use_case_template="setup [info]",
            short_help_description="Starts the setup process or displays the current configuration",
            full_help_description=(
                " Starts the setup mode, where the user is prompted with a series of questions to configure their work schedule,"
                " including preferred work days, hours, and other relevant parameters, within the context of the given month. If no"
                " month is provided, the setup will be applied to the currently active date's month."
                " The setup for the previous month is automatically used for the next month if no new setup was provided."
                " Once setup is complete, the user must call the 'calculate' method to automatically generate the work schedule for the given month."
                " The 'recalculate' method can be used to refresh the schedule while respecting any manually entered data for specific dates, unlike"
                " 'calculate' which performs a 'hard reset' of the data."
                "\nAdditionaly, 'setup info' displays the current configuration including all set parameters."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "setup", "starts the setup process, prompting the user for configuration options."),
                CommandUseCaseDescription(set(Mode), "setup <info>", "displays the current configuration with all set parameters."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [str]],
    ),
    CommandTemplate(
        name="start",
        help=CommandHelp(
            full_use_case_template="start [time]",
            short_help_description="Marks the start of work",
            full_help_description=(
                " Marks the start of work to track time spent at work. If no time is provided, it uses the current system time."
                " If a time is provided, it sets that as the start time."
                " This command works together with the 'end' command to precisely and with ease track the total time worked."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "start", "marks the start of work at the current system time."),
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "start <time>", "marks the start of work at the specified time."),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[], [TimeArgument]],
    ),
    CommandTemplate(
        name="status",
        help=CommandHelp(
            full_use_case_template="status",
            short_help_description="Displays the time spent and the target time at work",
            full_help_description=(
                "Displays the time spent at work on the given date and the target time set for that date."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "status", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="target",
        help=CommandHelp(
            full_use_case_template="target [time|'office'|'remote'|'current']",
            short_help_description="Displays or modifies the target time at work",
            full_help_description=(
                " When run without arguments, this command prints the target time spent at work for the given date."
                " If a time is provided, it modifies the target time by the specified amount."
                " The arguments 'office' and 'remote' display the target time for office and remote work for the entire month, respectively."
                " The argument 'current' sets the target time to match the amount of time already worked on the current day."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "target", "displays the target time at work for the given date."),
                CommandUseCaseDescription(set(Mode), "target <time>", "modifies the target time at work by the given amount."),
                CommandUseCaseDescription(set(Mode), "target <'office'|'remote'>", "displays the target time at work for the entire month of office or remote work."),
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "target <'current'>", "sets the target time at work to the time already spent at work on the given date."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [TimeArgument], [str]],
    ),
    CommandTemplate(
        name="tutorial",
        help=CommandHelp(
            full_use_case_template="tutorial [page-number]",
            short_help_description="Presents a brief guide on how to use WorkTracker",
            full_help_description=(
                " Starts tutorial mode to walk you through a brief guide on how to use WorkTracker."
                " Switch between pages by specifying a page number, to exit tutorial mode, type 'quit'."
                " If command is run with a page number provided, it will display the content of that specific page without entering the tutorial mode."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "tutorial", "starts the tutorial mode and presents a guide on how to use WorkTracker."),
                CommandUseCaseDescription(set(Mode), "tutorial <page-number>", "displays the content of the specified page of the guide."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=["guide", "instruction"],
        valid_argument_types=[[], [int]],
    ),
    CommandTemplate(
        name="undo",
        help=CommandHelp(
            full_use_case_template="undo",
            short_help_description="Undoes the last command executed that altered the state of the data",
            full_help_description=(
                " Undoes the last command executed that altered the state of the data."
                " The history of commands that can be undone or redone is tracked and can be viewed using the 'history' command."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "undo", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="workday",
        help=CommandHelp(
            full_use_case_template="workday",
            short_help_description="Marks a date as a work day",
            full_help_description=(
                " Marks a date as a work day. As a result, this date is no longer treated as a holiday or weekend, even if it was marked as one before."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription({Mode.Today, Mode.Day}, "workday", ""),
            ],
        ),
        supported_modes={Mode.Today, Mode.Day},
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="version",
        help=CommandHelp(
            full_use_case_template="version",
            short_help_description="Displays the version of currently running WorkTracker instance",
            full_help_description=(
                " Displays version of currently running WorkTracker instance."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "version", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="zero",
        help=CommandHelp(
            full_use_case_template="zero",
            short_help_description="Sets the time spent at work to 0 minutes",
            full_help_description=(
                " Sets the time spent at work to 0 minutes."
                " If run in context of a month, it sets the time spent at work to 0 minutes for every day within that month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "zero", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
]
