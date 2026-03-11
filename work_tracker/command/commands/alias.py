from work_tracker.error import CommandErrorInvalidDateCount
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.command.alias_manager import AliasManager, AliasTemplate
from work_tracker.common import Date, ReadonlyAppState
from work_tracker.text.common import wrap_text, frame_text, Color


class AliasHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        # TODO add pagination
        if date_count == 0 and argument_count == 0:
            raw_texts: list[str] = [alias.raw for alias in AliasManager.iterable_aliases]
            alias_identifiers: list[str] = [text.split("|", 1)[0].strip() for text in raw_texts]
            alias_replacements: list[str] = [text.split("|", 1)[1].strip() if "|" in text else "" for text in raw_texts]

            longest_identifier_size: int = max(len(identifier) for identifier in alias_identifiers)

            # TODO add ellipsis here and in other places modifiable by user (custom methods in the future)
            # TODO what if identifier is very long => solution: set max length in config and add ellipsis if its too long
            separator: str = " | " # TODO make separator configurable, but the read logic must be changed too
            alias_texts: list[str] = []
            for index, (identifier, replacement) in enumerate(zip(alias_identifiers, alias_replacements)):
                replacement_wrapped: str = wrap_text(
                    text=replacement,
                    indent=" "*(longest_identifier_size + len(separator)),
                    omit_first_line_indent=True,
                    frame_wrap=True
                )
                alias_texts.append(f"{Color.Brightblack.value if index % 2 == 1 else Color.Reset.value}{identifier.rjust(longest_identifier_size)}{separator}{replacement_wrapped}")

            framed_text: str = frame_text(
                text="\n".join(alias_texts),
                title="Aliases",
                title_color=Color.Bold
            )
            self.io.output(framed_text)
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count == 1:
            alias_identifier: str = arguments[0]
            if alias_identifier in AliasManager.aliases:
                self.io.output(AliasManager.aliases[alias_identifier].raw)
            else:
                self.io.output(f"Could not find alias named {alias_identifier}.")
            return CommandHandlerResult(undoable=False)
        elif date_count == 0 and argument_count >= 2:
            alias_identifier: str = arguments[0]
            replacement_text: str = " ".join(str(arg) for arg in arguments[1:])

            # alias cant be named 'alias' nor 'deletealias' to prevent softlocking user out of creating/updating aliases
            if alias_identifier.lower() in ["alias", "deletealias"]:
                self.io.output("Alias identifier cannot be 'alias' or 'deletealias'.")
                return CommandHandlerResult(undoable=False)
            
            alias: AliasTemplate = AliasTemplate(
                identifier=alias_identifier,
                raw=f"{alias_identifier} | {replacement_text}",
                replacement_text=replacement_text,
            )
            AliasManager.update_alias(alias)
            AliasManager.save_aliases_file()
            return CommandHandlerResult(undoable=False)
        else: # date_count != 0
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
