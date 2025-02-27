from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.command_parser import CommandParser
from work_tracker.command.common import CommandArgument, ParseResult, CommandQuery
from work_tracker.command.macro_manager import MacroManager, MacroTemplate
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.error import CommandErrorInvalidArgumentCount, CommandErrorCustom


class __MacroHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if argument_count == 0:
            print(arguments)
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
        if len(given_arguments) < required_argument_count:
            return CommandHandlerResult(
                undoable=False,
                error=CommandErrorCustom(
                    command_name=self.command_name,
                    custom_message=f"macro {macro_identifier} requires {required_argument_count} arguments but only {len(given_arguments)} values were provided. Please provide the missing arguments."
                )
            )

        macro_arguments: list[any] = macro.default_argument_values
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
        return CommandHandlerResult(undoable=True, execute_after=queries)
