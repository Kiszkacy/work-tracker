import calendar
import re
from fractions import Fraction
from typing import get_origin, get_args

from work_tracker.command.command_manager import CommandManager
from work_tracker.command.command_text_parser import CommandTextParser
from work_tracker.command.common import Command, CommandQuery, Date, CommandArgument, TimeArgument, TimeArgumentType, ParseResult, Number, AdditionalInputArgument
from work_tracker.error import ParserError, ParserErrorMultipleDates, ParserErrorInvalidArgumentCount, ParserErrorInvalidArgumentTypes, ParserErrorUnknownCommand
from work_tracker.command.macro_manager import MacroManager
from work_tracker.common import month_map
from work_tracker.config import Config


# TODO move to config
multi_command_dates_start_string: str = "("
multi_command_dates_end_string: str = ")"
time_argument_add_prefix_string: str = "+"
time_argument_subtract_prefix_string: str = "-"


class CommandParser:
    _date_pattern: str = r'^(?:(\d{1,2}))?\.(?:(\d{1,2})(?:\.(\d{1,2}|\d{4})?)?)?$' # e.g. DD.MM.YYYY, DD.MM.YY, DD.MM, DD., .MM., .MM.YYYY
    _year_pattern: str = r'^(\d{4})$' # e.g. YYYY
    _hour_pattern: str = r'^\d+(\.\d+)?\s*(h|hour|hours)$' # e.g. 1h, 1 hour, 1.5hour
    _minute_pattern: str = r'^\d+\s*(m|min|mins|minute|minutes)$' # e.g. 300m, 300 minutes
    _time_pattern: str = r'^\d+:\d{2}$' # e.g. 1:20, 2:30

    @classmethod
    def parse(cls, text: str) -> ParseResult:
        text = re.sub(r"\s+", " ", text)
        text_per_command: list[str] = cls._split_text_per_command(text)
        queries: list[CommandQuery] = []
        error: ParserError | None = None

        multi_dates: list[Date] = []
        for index, text in enumerate(text_per_command):
            parser: CommandTextParser = CommandTextParser(text)
            dates: list[Date] = []
            if parser.peak() is None:
                continue
            
            is_first_command_in_chain: bool = index == 0
            if is_first_command_in_chain and cls._has_multi_command_dates(parser):
                multi_dates = cls._get_multi_command_dates(parser) # TODO fix, this does not check if the multi_end_string is required so input '(<date> <date>...' is valid

            predefined_command_arguments: list[CommandArgument] = []
            command: Command = None
            if (time := cls._get_time(parser)) is not None:
                command = CommandManager.time_command
                predefined_command_arguments.append(time)
            else:
                dates = cls._get_dates(parser)

            if command is not None:
                pass
            elif parser.peak() is not None and (time := cls._get_time(parser)) is not None:
                command: Command = CommandManager.time_command
                predefined_command_arguments.append(time)
            elif parser.peak() is None and len(dates) == 1:
                command: Command = CommandManager.date_command
            elif parser.peak() is None and len(dates) > 1: # situation where only dates are provided
                error = ParserErrorMultipleDates()
                break
            elif parser.peak() in MacroManager.macros: # TODO macro
                command: Command = CommandManager.macro_execute_command
                predefined_command_arguments.append(parser.next())
            else:
                command_string: str = parser.next()
                is_valid_command_string: bool = cls._is_valid_command_string(command_string)
                if not is_valid_command_string and len(dates) == 1: # this is here to properly catch errors further ahead when reading arguments
                    command: Command = CommandManager.date_command
                elif not is_valid_command_string:
                    error = ParserErrorUnknownCommand(
                        received_name=command_string
                    )
                    break
                else:
                    command: Command = cls.find_matching_command(command_string)

            command_arguments: list[CommandArgument] = predefined_command_arguments + cls._get_command_arguments(parser)
            has_valid_argument_count: bool = cls._has_valid_argument_count(command, command_arguments)
            if not has_valid_argument_count:
                error = ParserErrorInvalidArgumentCount(
                    command=command,
                    received_amount=len(command_arguments)
                )
                break

            has_valid_argument_types: bool = cls._has_valid_argument_types(command, command_arguments)
            if not has_valid_argument_types:
                error = ParserErrorInvalidArgumentTypes(
                    command=command,
                    received_types=[type(argument) for argument in command_arguments]
                )
                break

            final_dates: list[Date] = Date.normalize_dates(multi_dates + dates, preserve_order=True) # TODO allow user to turn off normalization
            queries.append(CommandQuery(
                command=command,
                dates=final_dates,
                date_count=len(final_dates),
                arguments=command_arguments,
                argument_count=len(command_arguments),
                raw_text=text
            ))

        return ParseResult(
            queries=queries,
            error=error,
        )

    @classmethod
    def _split_text_per_command(cls, text: str) -> list[str]: # TODO add tests
        text = text.strip()

        # TODO original pattern looked like that: it only supported " " (source: https://stackoverflow.com/questions/6462578/regex-to-match-all-instances-not-inside-quotes#:~:text=130-,Actually,-%2C%20you%20can%20match)
        # TODO my edit supports ' but probably doesnt support all of the cases, please check it in the future
        # TODO         rf'''{Config.data.input.command_chain_symbol}(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)'''
        pattern: str = rf'''{Config.data.input.command_chain_symbol}(?=([^"\\']*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"']*$)'''
        parts: list[str] = re.split(pattern, text)
        return [part.strip() for part in parts if part is not None]

    @classmethod
    def _has_multi_command_dates(cls, parser: CommandTextParser) -> bool:
        return parser.peak().startswith(multi_command_dates_start_string)

    @classmethod
    def _get_multi_command_dates(cls, parser: CommandTextParser) -> list[Date]:
        if parser.peak() == multi_command_dates_start_string:
            parser.next()
        return cls._get_dates(parser, multi_command_dates=True)

    @classmethod
    def _get_dates(cls, parser: CommandTextParser, multi_command_dates: bool = False) -> list[Date]:
        parsed_dates: list[Date] = []
        force_break: bool = False
        first_word: bool = True
        while word := parser.peak(): # TODO split the 'multi_command_dates_end_string' logic into _get_multi_command_dates ?
            if multi_command_dates and first_word and word != multi_command_dates_start_string and word.startswith(multi_command_dates_start_string):
                word = word[len(multi_command_dates_start_string):]
                first_word = False
            if multi_command_dates and word == multi_command_dates_end_string:
                parser.next()
                break
            if multi_command_dates and word.endswith(multi_command_dates_end_string):
                word = word[:-len(multi_command_dates_end_string)]
                force_break = True
            
            date: Date | None = cls._extract_date(word)
            if date is not None:
                parsed_dates.append(date)
                parser.next()
            else:
                break

            if force_break:
                break

        return Date.normalize_dates(parsed_dates, preserve_order=True) # TODO normalize too aggressive in some cases, allow user to turn it off ?

    @classmethod
    def _extract_date(cls, text: str) -> Date | None:
        date_match: re.Match = re.fullmatch(cls._date_pattern, text)
        year_match: re.Match = re.fullmatch(cls._year_pattern, text)

        if date_match:
            day, month, year = date_match.groups()
            if day:
                day = int(day)
            if month:
                month = int(month)
                if month < 1 or month > 12:
                    return None # TODO inform user that input was invalid
            if year:
                year = int(year)
                if year <= 50:
                    year += 2000
                elif year <= 99:
                    year += 1900
                if year < 1951 or year > 2050:
                    return None # TODO inform user that input was invalid

            if year and month: # TODO if no year or month is provided this wont work correctly
                _, day_count = calendar.monthrange(year, month)
                if day is not None and day > day_count:
                    raise Exception()
            return Date(day=day, month=month, year=year)
        elif year_match:
            year = int(year_match.group())
            return Date(day=None, month=None, year=year)
        elif text in month_map:
            return Date(day=None, month=month_map[text], year=None)
        else:
            return None

    @classmethod
    def parse_arguments(cls, text: str) -> list[AdditionalInputArgument]:
        parser: CommandTextParser = CommandTextParser(text)
        return cls._extract_arguments(parser, read_dates=True)

    @classmethod
    def _get_command_arguments(cls, parser: CommandTextParser) -> list[CommandArgument]:
        return cls._extract_arguments(parser)

    @classmethod
    def _extract_arguments(cls, parser: CommandTextParser, read_dates: bool = False) -> list[CommandArgument]:
        arguments: list[CommandArgument] = []
        while parser.peak() is not None:
            if read_dates:
                parsed_value = cls._extract_date(parser.peak())
                if parsed_value is not None:
                    parser.next()
                    arguments.append(parsed_value)
                    continue

            parsed_value = cls._get_time(parser)
            if parsed_value is not None:
                arguments.append(parsed_value)
                continue

            parsed_value = cls._get_number(parser)
            if parsed_value is not None:
                arguments.append(parsed_value)
                continue

            arguments.append(cls._get_string(parser))

        return arguments

    @classmethod
    def _get_time(cls, parser: CommandTextParser) -> TimeArgument | None:
        parser.checkpoint()
        argument_type: TimeArgumentType = TimeArgumentType.Overwrite
        text: str = parser.peak()
        if text == time_argument_add_prefix_string:
            argument_type = TimeArgumentType.Add
            parser.next()
        elif text.startswith(time_argument_add_prefix_string):
            argument_type = TimeArgumentType.Add
        elif text == time_argument_subtract_prefix_string:
            argument_type = TimeArgumentType.Subtract
            parser.next()
        elif text.startswith(time_argument_subtract_prefix_string):
            argument_type = TimeArgumentType.Subtract

        minutes: int = cls._get_minute_count(parser)
        if minutes is not None:
            return TimeArgument(minutes, argument_type)

        parser.go_to_checkpoint()
        return None

    @classmethod
    def _get_number(cls, parser: CommandTextParser) -> Number | None:
        if not all(character in '0123456789,.%/' for character in parser.peak()): # TODO add expression evaluation here in the future
            return None

        parser.checkpoint()
        text: str = parser.next()

        if parser.peak() == "/":
            text += parser.next()
            if parser.peak() is None:
                parser.go_to_checkpoint()
                return None
            text += parser.next()
        elif parser.peak() == "%":
            text += parser.next()

        if (number := cls._extract_number(text)) is not None:
            return number
        else:
            parser.go_to_checkpoint()
            return None

    @classmethod
    def _extract_number(cls, text: str) -> Number | None:
        if "/" in text:
            return float(Fraction(text))
        elif "%" in text:
            return float(text.strip('%')) / 100
        else:
            try:
                value: Number = int(text)
            except ValueError:
                try:
                    value = float(text)
                except ValueError:
                    return None
            return value

    @classmethod
    def _get_string(cls, parser: CommandTextParser) -> str:
        word: str = parser.peak()

        if (word.startswith('"') and word.endswith('"')) or (word.startswith("'") and word.endswith("'")):
            word = word[1:-1]

        parser.next()
        return word

    @classmethod
    def _get_minute_count(cls, parser: CommandTextParser) -> int | None:
        parser.checkpoint()
        text: str = parser.next()
        if text is None:
            parser.go_to_checkpoint()
            return None
        elif text.startswith(time_argument_add_prefix_string):
            text = text[len(time_argument_add_prefix_string):]
        elif text.startswith(time_argument_subtract_prefix_string):
            text = text[len(time_argument_subtract_prefix_string):]

        minutes: int = cls._extract_minute_count(text)
        if minutes is not None:
            return minutes

        if parser.peak() is None:
            parser.go_to_checkpoint()
            return None

        text += parser.next()
        minutes = cls._extract_minute_count(text)
        if minutes:
            return minutes

        parser.go_to_checkpoint()
        return None

    @classmethod
    def _extract_minute_count(cls, text: str) -> int | None:
        if re.fullmatch(cls._time_pattern, text):
            hours, minutes = map(int, text.split(':'))
            return hours * 60 + minutes
        if re.fullmatch(cls._hour_pattern, text):
            hours = float(re.search(r'\d+(\.\d+)?', text).group())
            return int(hours * 60)
        if re.fullmatch(cls._minute_pattern, text):
            return int(re.search(r'\d+', text).group())

        return None

    @classmethod
    def _has_valid_argument_count(cls, command: Command, arguments: list[CommandArgument]) -> bool:
        return any(
            len(arguments) >= len(valid_types)-1 if len(valid_types) != 0 and valid_types[-1] is Ellipsis else
            len(arguments) == len(valid_types)
            for valid_types in command.valid_argument_types
        )

    @classmethod
    def _has_valid_argument_types(cls, command: Command, arguments: list[CommandArgument]) -> bool: # TODO this whole method could be optimized
        for valid_types in command.valid_argument_types:
            has_variadic_type: bool = len(valid_types) != 0 and valid_types[-1] is Ellipsis
            base_types: list[type] = valid_types if not has_variadic_type else valid_types[:-1]
            variadic_type: type | tuple[type, ...] | None = None
            if has_variadic_type and get_origin(base_types[-1]) is not None:
                variadic_type = get_args(base_types[-1])
            elif has_variadic_type and get_origin(base_types[-1]) is None:
                variadic_type = base_types[-1]

            if (not has_variadic_type and len(arguments) != len(valid_types)) or (has_variadic_type and len(arguments) < len(valid_types)-1):
                continue

            all_valid: bool = True
            for index, valid_type in enumerate(base_types):
                if get_origin(valid_type) is not None and not isinstance(arguments[index], get_args(valid_type)):
                    all_valid = False
                    break
                elif get_origin(valid_type) is None and not isinstance(arguments[index], valid_type):
                    all_valid = False
                    break

            if has_variadic_type and not all(isinstance(argument, variadic_type) for argument in arguments[len(base_types):]):
                break
            if all_valid:
                return True

        return False

    @classmethod
    def _is_valid_command_string(cls, text: str) -> bool:
        return cls.find_matching_command(text) is not None

    @classmethod
    def find_matching_command(cls, text: str) -> Command | None:
        text = text.lower()
        found_command: Command | None = None
        for command in CommandManager.commands:
            if any([text == abbreviation for abbreviation in command.abbreviations]) or (text.startswith(command.shortest_valid_string) and text in command.name):
                if found_command:
                    return None
                found_command = command
        return found_command
