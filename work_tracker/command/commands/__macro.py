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
        given_argument_count: int = len(given_arguments)

        max_accepted_argument_count: int = len(macro.default_argument_values)
        min_required_argument_count: int = len([argument for argument in macro.default_argument_values if argument is None])

        # TODO: really dont like using nested methods, but this is a quick fix
        def plural_argument(count: int) -> str: return "argument" if count == 1 else "arguments"
        def plural_be(count: int) -> str: return "was" if count == 1 else "were"

        if given_argument_count > max_accepted_argument_count:
            if max_accepted_argument_count == 0:
                message = f"macro {macro_identifier} expects no arguments, but {given_argument_count} {plural_be(given_argument_count)} provided."
            else:
                message = f"macro {macro_identifier} expects at most {max_accepted_argument_count} {plural_argument(max_accepted_argument_count)}, but {given_argument_count} {plural_be(given_argument_count)} provided."

            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(command_name=self.command_name, custom_message=message)
            )
        elif given_argument_count < min_required_argument_count:
            if given_argument_count == 0:
                message = f"macro {macro_identifier} requires at least {min_required_argument_count} {plural_argument(min_required_argument_count)}, but no arguments were provided."
            else:
                message = f"macro {macro_identifier} requires at least {min_required_argument_count} {plural_argument(min_required_argument_count)}, but only {given_argument_count} {plural_be(given_argument_count)} provided."

            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(command_name=self.command_name, custom_message=message)
            )

        macro_arguments: list[str] = macro.default_argument_values.copy()
        macro_arguments[:len(given_arguments)] = given_arguments
        command_text: str = macro.command_text
        for index, argument_identifier in enumerate(macro.arguments):
            command_text = command_text.replace(f"<{argument_identifier}>", macro_arguments[index])

        interpret_result: ParseResult = CommandParser.parse(command_text, state)
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
