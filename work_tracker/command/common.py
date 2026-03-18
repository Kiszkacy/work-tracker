import base64
import lzma
import pickle
from dataclasses import dataclass
from enum import Enum, auto
from types import UnionType
from typing import Any

from work_tracker.common import AppData, Date, Mode
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
    own_dates: list[Date]
    own_date_count: int
    multi_dates: list[Date]
    multi_dates_count: int
    arguments: list[CommandArgument]
    argument_count: int
    raw_text: str
    raw_full_input: str
    order_index: int


@dataclass(frozen=True)
class ParseResult:
    queries: list[CommandQuery]
    # error: ParserError | None = None
    # TODO had to remove ParserError typehint due to circular imports, fix it in the future
    error: Any = None


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
        name="absence",
        help=CommandHelp(
            full_use_case_template="absence",
            short_help_description="Marks a date as an absence",
            full_help_description=(
                " Marks a date as an absence. When used within the context of a specific month it will mark all work days as absences within that month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "absence", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=["absent"],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="alias",
        help=CommandHelp(
            full_use_case_template="(alias [name]) | (alias <name> <replacement_text...>)",
            short_help_description="Displays, updates or creates aliases",
            full_help_description=(
                f" Aliases are simple text replacements that occur before command parsing."
                f" When an alias is detected at the beginning of user input, it is expanded to its replacement text."
                f" Unlike macros, aliases do not support arguments and are purely text-based substitutions."
                f" Aliases can be layered, meaning one alias can reference another."
                f"\n\nTo avoid any problems during the alias definition, it is recommended to enclose the entire command sequence of the macro in quotes (single or double)."
                f" For example to define an alias that during runtime replaces the word {Color.Brightblue.value}ha{Color.Reset.value} with {Color.Brightblue.value}help alias{Color.Reset.value}, you would type the following:"
                f'\n  {Color.Blue.value}>> {Color.Brightblue.value}alias ha "help alias"{Color.Reset.value}'
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "alias", "displays all available aliases"),
                CommandUseCaseDescription(set(Mode), "alias <name>", "displays the definition of the specified alias"),
                CommandUseCaseDescription(set(Mode), "alias <name> <replacement_text...>", "creates or overwrites an alias with the given name"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [str], [str, str, ...]],
    ),
    CommandTemplate(
        name="calendar",
        help=CommandHelp(
            full_use_case_template="calendar",
            short_help_description="Displays the calendar for the month",
            full_help_description=(
                " Displays the calendar for the month corresponding to the given date."
                f" Dates are marked using a color-coded legend which can be easily configured via {Color.Brightblue.value}config{Color.Reset.value} command,"
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
        name="checkpoint",
        help=CommandHelp(
            full_use_case_template="checkpoint [name] ['permanent']",
            short_help_description="Creates or lists available checkpoints",
            full_help_description=(
                " Allows you to create a checkpoint which represents a saved state of the app."
                " If no argument is provided, it lists all available checkpoints."
                " If a checkpoint name is provided, it creates a checkpoint with that name."
                " Checkpoints by default are session-specific and are deleted when the app is closed, meaning they only exist until you exit the app."
                f" If the optional {Color.Brightblue.value}permanent{Color.Reset.value} argument is included when creating a checkpoint,"
                f" it becomes a permanent checkpoint that persists across sessions and is not deleted when the app is closed."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "checkpoint", "lists all available checkpoints"),
                CommandUseCaseDescription(set(Mode), "checkpoint <name>", "creates a checkpoint with the given name"),
                CommandUseCaseDescription(set(Mode), "checkpoint <name> 'permanent'", "creates a permanent checkpoint with the given name"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [str], [str, str]],
    ),
    CommandTemplate(
        name="clear",
        help=CommandHelp(
            full_use_case_template="clear",
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
            short_help_description="Marks a date as a day off",
            full_help_description=(
                " Marks a date as a day off. When used within the context of a specific month it will mark all work days as days off within that month."
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
                f" If {Color.Brightblue.value}remote{Color.Reset.value} or {Color.Brightblue.value}office{Color.Reset.value} is specified as the first argument, the calculation is limited to that specific type of work."
                f" If the {Color.Brightblue.value}clean{Color.Reset.value} argument is included, the calculation ignores any previously logged work time and assumes a clean month."
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
        name="deletealias",
        help=CommandHelp(
            full_use_case_template="deletealias <name>",
            short_help_description="Deletes the specified alias",
            full_help_description=(
                " Deletes the alias identified by the given name."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "deletealias <name>", "deletes the alias with the specified name"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[str]],
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
                f" Sets the time spent at work to the value of the target time, which can be displayed using the {Color.Brightblue.value}target{Color.Reset.value} command."
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
                f" This command works together with the {Color.Brightblue.value}start{Color.Reset.value} command to calculate the total time worked by subtracting the start time from the end time."
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
                " If you are working within the context of any other date, it will switch you back to the today mode."
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
                f" Alternatively, {Color.Brightblue.value}help <command-name>{Color.Reset.value} can be used to get detailed information about a specific command."
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
                " If the current monthly target work time matches fte-based calculation, it will be automatically updated to reflect the change in workdays."
                " Otherwise the monthly target work time remains unchanged."
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
                " Displays all relevant information for a given date."
                " For a specific day, this includes the time worked, target time, and attributes such as whether the day is marked as a holiday or workday."
                " For a month, this includes monthly target time, remote work ratio, and other month-level details."
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
        name="keyword",
        help=CommandHelp(
            full_use_case_template="keyword",
            short_help_description="Displays a list of all available keywords with their descriptions and supported modes",
            full_help_description=(
                " Displays all available keywords, including their descriptions and the modes they support."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "keyword", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="macro",
        help=CommandHelp(
            full_use_case_template="(macro [name]) | (macro {argument} <command_text...>)",
            short_help_description="Displays, updates or creates macros",
            full_help_description=(
                f" Macros act as reusable command sequences, allowing users to define custom methods that execute multiple commands (or other macros) in order."
                f" A macro consists of an identifier (name) and optional or required arguments, which can be used within the command sequence."
                f" The parser processes macros like any other command. Consequently, if you specify a date before a macro, that date is passed down to each individual command contained inside."
                f"\n\nMacro arguments must be specified using the format {Color.Brightblue.value}<argument_name>{Color.Reset.value},"
                f" and the first word after the macro identifier (excluding arguments in {Color.Brightblue.value}<>{Color.Reset.value}) marks the beginning of the macro's command sequence."
                f" These arguments can be referenced throughout the sequence by using the format {Color.Brightblue.value}<argument_name>{Color.Reset.value}."
                f"\n\nTo avoid any problems during the macro definition, it is recommended to enclose the entire command sequence of the macro in quotes (single or double)."
                f" This makes the text inside the quotes treated as a literal string, preventing any issues with special characters or spaces in the command sequence."
                f" For example, defining a macro called {Color.Brightblue.value}custom-help{Color.Reset.value} that runs {Color.Brightblue.value}help{Color.Reset.value} on a user-specified command name "
                f" (or {Color.Brightblue.value}macro{Color.Reset.value} if no name is provided) would look like this:"
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
                f" If {Color.Brightblue.value}remote{Color.Reset.value} or {Color.Brightblue.value}office{Color.Reset.value} is specified as the first argument, the calculation is restricted to that specific type of work."
                f" If the {Color.Brightblue.value}clean{Color.Reset.value} argument is included, the calculation ignores any previously logged work time and assumes a clean month."
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
                " Marks a date as office work. When used within the context of a specific month it will mark all work days as office work within that month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "office", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="present",
        help=CommandHelp(
            full_use_case_template="present",
            short_help_description="Marks a date as being present at work",
            full_help_description=(
                " Marks a date as being present, clearing any absence or day off status."
                " When used within the context of a specific month it will mark all work days as being present within that month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "present", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=["working"],
        valid_argument_types=[[]],
    ),
    CommandTemplate(
        name="redo",
        help=CommandHelp(
            full_use_case_template="redo [count]",
            short_help_description="Re-applies the last undone command that altered the state of the data",
            full_help_description=(
                " Re-applies the last command that was undone and altered the state of the data."
                " If a count is provided, it re-applies that many commands at once."
                f" The history of commands that can be undone or redone is tracked and can be viewed using the {Color.Brightblue.value}history{Color.Reset.value} command."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "redo", "re-applies the last undone command"),
                CommandUseCaseDescription(set(Mode), "redo <count>", "re-applies the last <count> undone commands"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [int]],
    ),
    CommandTemplate(
        name="remote",
        help=CommandHelp(
            full_use_case_template="remote",
            short_help_description="Marks a date as remote work",
            full_help_description=(
                " Marks a date as remote work. When used within the context of a specific month it will mark all work days as remote work within that month."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "remote", ""),
            ],
        ),
        supported_modes=set(Mode),
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
                f" {Color.Brightblue.value}checkpoint{Color.Reset.value} command."
                f" WorkTracker will revert to that state undoing or applying any changes made since the checkpoint was created, regardless of any actions taken in the meantime."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "rollback <checkpoint>", ""),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[str], [int]],
    ),
    CommandTemplate(
        name="rwr",
        help=CommandHelp(
            full_use_case_template="rwr [value]",
            short_help_description="Displays or modifies the remote work ratio",
            full_help_description=(
                " Displays the current remote work ratio (RWR) for the given date."
                " If called with an argument it sets the remote work ratio to that value for the specified date allowing users to adjust their remote work percentage."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "rwr", "displays the current remote work ratio for the given date."),
                CommandUseCaseDescription(set(Mode), "rwr <value>", "sets the remote work ratio to the specified value for the given date's month."),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [Number]],
    ),
    CommandTemplate(
        name="start",
        help=CommandHelp(
            full_use_case_template="start [time]",
            short_help_description="Marks the start of work",
            full_help_description=(
                " Marks the start of work to track time spent at work. If no time is provided, it uses the current system time."
                " If a time is provided, it sets that as the start time."
                f" This command works together with the {Color.Brightblue.value}end{Color.Reset.value} command to precisely and with ease track the total time worked."
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
                f" The arguments {Color.Brightblue.value}office{Color.Reset.value} and {Color.Brightblue.value}remote{Color.Reset.value} display the target time for office and remote work for the entire month, respectively."
                f" The argument {Color.Brightblue.value}current{Color.Reset.value} sets the target time to match the amount of time already worked on the current day."
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
                f" Switch between pages by specifying a page number, to exit tutorial mode, type {Color.Brightblue.value}quit{Color.Reset.value}."
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
            full_use_case_template="undo [count]",
            short_help_description="Undoes the last command executed that altered the state of the data",
            full_help_description=(
                " Undoes the last command executed that altered the state of the data."
                " If a count is provided, it undoes that many commands at once."
                f" The history of commands that can be undone or redone is tracked and can be viewed using the {Color.Brightblue.value}history{Color.Reset.value} command."
            ).strip(),
            use_case_description=[
                CommandUseCaseDescription(set(Mode), "undo", "undoes the last command"),
                CommandUseCaseDescription(set(Mode), "undo <count>", "undoes the last <count> commands"),
            ],
        ),
        supported_modes=set(Mode),
        abbreviations=[],
        valid_argument_types=[[], [int]],
    ),
    CommandTemplate(
        name="workday",
        help=CommandHelp(
            full_use_case_template="workday",
            short_help_description="Marks a date as a work day",
            full_help_description=(
                " Marks a date as a work day. As a result, this date is no longer treated as a holiday or weekend, even if it was marked as one before."
                " If the current monthly target work time matches fte-based calculation, it will be automatically updated to reflect the change in workdays."
                " Otherwise the monthly target work time remains unchanged."
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
