from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.command_parser import CommandParser
from work_tracker.command.common import CommandArgument, ParseResult, CommandQuery
from work_tracker.command.macro_manager import MacroManager, MacroTemplate
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorCustom
from dataclasses import replace


class __MacroHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if argument_count == 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))

        macro_identifier: str = arguments[0]
        macro: MacroTemplate = MacroManager.macros[macro_identifier]
        if macro is None:
            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(
                    command_name=self.command_name,
                    custom_message=f"macro {macro_identifier} not found. Please check if the macro is defined correctly or if there are any typos."
                )
            )

        given_arguments: list[any] = arguments[1:]
        required_argument_count: int = len([argument for argument in macro.default_argument_values if argument is None])
        given_argument_count: int = len(given_arguments)
        argument_suffix: str = "argument" if required_argument_count == 1 else "arguments"
        if required_argument_count == 0 and given_argument_count > 0:
            message: str = f"macro {macro_identifier} expects no arguments, but {given_argument_count} were provided." if given_argument_count > 1 else f"macro {macro_identifier} expects no arguments, but 1 was provided."
            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(
                    command_name=self.command_name,
                    custom_message=message
                )
            )
        elif required_argument_count != 0 and given_argument_count == 0:
            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(
                    command_name=self.command_name,
                    custom_message=f"macro {macro_identifier} requires {required_argument_count} {argument_suffix}, but no values were provided."
                )
            )
        elif required_argument_count != 0 and given_argument_count < required_argument_count:
            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(
                    command_name=self.command_name,
                    custom_message=f"macro {macro_identifier} requires {required_argument_count} {argument_suffix}, but only {given_argument_count} values were provided."
                )
            )
        elif required_argument_count != 0 and given_argument_count > required_argument_count:
            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(
                    command_name=self.command_name,
                    custom_message=f"macro {macro_identifier} requires {required_argument_count} {argument_suffix}, but {given_argument_count} values were provided."
                )
            )

        macro_arguments: list[str] = macro.default_argument_values.copy()
        macro_arguments[:len(given_arguments)] = given_arguments
        command_text: str = macro.command_text
        for index, argument_identifier in enumerate(macro.arguments):
            command_text = command_text.replace(f"<{argument_identifier}>", macro_arguments[index])

        interpret_result: ParseResult = CommandParser.parse(command_text)
        if interpret_result.error is not None:
            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(
                    command_name=self.command_name,
                    custom_message="something went wrong during macro execution. This may be due to incorrect argument values or an issue with the macro definition. Please check the command syntax and argument types."
                )
            )

        queries: list[CommandQuery] = interpret_result.queries
        for index, query in enumerate(queries): # TODO: this is quite ugly, but works, here date normalization is OMITTED !
            new_dates: list[Date] = query.dates + dates
            queries[index] = replace(query, dates=new_dates, date_count=new_dates.__len__())
        return CommandHandlerResult(undoable=True, execute_after=queries)
