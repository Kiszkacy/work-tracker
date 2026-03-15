from work_tracker.config import Config
from work_tracker.error import CommandErrorInvalidDateCount, CommandErrorInvalidArgumentCount
from work_tracker.command.command_handler import CommandHandlerResult, CommandHandler
from work_tracker.command.common import CommandArgument
from work_tracker.command.keyword_manager import KeywordManager, KeywordTemplate
from work_tracker.common import Date, Mode, ReadonlyAppState
from work_tracker.text.common import wrap_text, frame_text, Color, strip_ansi


class KeywordHandler(CommandHandler):
    def handle(self, dates: list[Date], date_count: int, arguments: list[CommandArgument], argument_count: int, state: ReadonlyAppState) -> CommandHandlerResult:
        if date_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidDateCount(self.command_name, received_date_count=date_count, expected_date_count=0))
        
        if argument_count != 0:
            return CommandHandlerResult(undoable=False, error=CommandErrorInvalidArgumentCount(self.command_name, received_argument_count=argument_count))
        
        keywords: list[KeywordTemplate] = KeywordManager.iterable_keywords
        longest_identifier_size: int = max(len(keyword.identifier) for keyword in keywords)
        
        example_values: dict[str, str] = {keyword.identifier: f"{KeywordManager.get_keyword_value(keyword.identifier, state)}" for keyword in keywords}
        longest_example_value_size: int = max(len(example_values[keyword.identifier]) for keyword in keywords)
        
        separator: str = " | " # TODO make separator configurable
        keyword_texts: list[str] = []
        
        modes: list[Mode] = [Mode.Today, Mode.Day, Mode.Month] # explicit list to define custom order of values
        modes_text_length: int = len(" ".join([mode.name[0].upper() for mode in modes]))
        
        for index, keyword in enumerate(keywords):
            identifier_padded: str = keyword.identifier.ljust(longest_identifier_size)
            modes_text: str = " ".join([f"{(Color.Green if mode in keyword.supported_modes else Color.Red).value}{mode.name[0].upper()}{Color.Reset.value}" for mode in modes])
            
            example_value: str = example_values[keyword.identifier]
            example_value_padded: str = example_value.ljust(longest_example_value_size)
            
            indent_size: int = longest_identifier_size + len(separator) + modes_text_length + len(separator) + longest_example_value_size + len(separator)
            indent: str = " " * indent_size
            
            wrapped_description: str = wrap_text(
                text=keyword.description,
                indent=indent,
                omit_first_line_indent=True,
                frame_wrap=True
            )

            color: str = Color.Brightblack.value if index % 2 == 1 else Color.Reset.value
            keyword_texts.append(
                f"{color}{identifier_padded}{color}{separator}{modes_text}{color}{separator}{Color.Brightcyan.value}{example_value_padded}{color}{separator}{wrapped_description}"
            )
        
        wrapped_text: str = "\n".join(keyword_texts)
        
        prefix: str = Config.data.input.keyword_prefix
        footer_text: str = wrap_text(
            text=f"To use keywords type its name with a prefix: {Color.Brightblue.value}{prefix}{Color.Reset.value}, for example: {Color.Brightblue.value}{prefix}today{Color.Reset.value}. Prefix can be changed via the config command.",
            frame_wrap=True
        )
        
        longest_line_width: int = max([len(strip_ansi(line)) for line in wrapped_text.splitlines()] + [len(strip_ansi(line)) for line in footer_text.splitlines()])
        
        framed_text: str = frame_text(
            text=wrapped_text,
            title="Built-in Keywords",
            title_color=Color.Bold,
            skip_bottom_line=True,
            minimal_line_width=longest_line_width
        )
        framed_footer_text: str = frame_text(
            text=footer_text,
            extend_top_line=True,
            minimal_line_width=longest_line_width
        )
        
        self.io.write(framed_text)
        self.io.output(framed_footer_text)
        return CommandHandlerResult(undoable=False)
