import importlib
from types import ModuleType

from prompt_toolkit.completion import WordCompleter, CompleteEvent, Completion
from prompt_toolkit.document import Document

from work_tracker.command.alias_manager import AliasManager
from work_tracker.command.command_manager import CommandManager
from work_tracker.command.command_parser import CommandParser
from work_tracker.command.common import Command, CompletionHint, CompletionCandidate
from work_tracker.command.keyword_manager import KeywordManager, KeywordTemplate
from work_tracker.command.macro_manager import MacroManager, MacroTemplate
from work_tracker.common import AppState
from work_tracker.config import Config


class InputCommandCompleter(WordCompleter):
    def __init__(self, state: AppState):
        self.active: bool = True
        self.custom_autocomplete: bool = False
        self._state: AppState = state
        self.in_subcommand_mode: bool = False # TODO move this to a separate object to which both input and completer have access ?
        self.subcommand_command: str | None = None
        super().__init__([], ignore_case=True)

    def get_completions(self, document: Document, complete_event: CompleteEvent):
        if not self.active:
            return []
        if self.custom_autocomplete:
            return super().get_completions(document, complete_event)

        segment: str = document.text.split(Config.data.input.command_chain_symbol)[-1]
        tokens: list[str] = segment.split()
        trailing_space: bool = bool(segment) and segment[-1] == " "
        committed_tokens: list[str] = tokens if trailing_space or not tokens else tokens[:-1]
        partial: str = "" if trailing_space or not tokens else tokens[-1]

        # handle aliases
        alias_expanded_committed_tokens: str = CommandParser.expand_aliases(" ".join(committed_tokens))
        if alias_expanded_committed_tokens:
            last_segment: str = alias_expanded_committed_tokens.split(Config.data.input.command_chain_symbol)[-1]
            committed_tokens = last_segment.split()
        else:
            committed_tokens = []

        # handle dates  by filtering them out (and keywords, for now)
        filtered_committed_tokens_by_date: list[str] = [
            token for token in committed_tokens 
            if not CommandParser._extract_date(token.lstrip(Config.data.input.date.multi_start_symbol).rstrip(Config.data.input.date.multi_end_symbol))
            and not (token.startswith(Config.data.input.keyword_prefix) and token[len(Config.data.input.keyword_prefix):].lower() in KeywordManager.keywords)
        ] # TODO: for now keywords are in here, because all of the current keywords are date dependant, but this behavior can break in the future

        # handle subcommand mode
        if self.in_subcommand_mode:
            command: Command | None = CommandParser.find_matching_command(self.subcommand_command)
            if command is None:
                return []
            return list(self._command_completions(command, filtered_committed_tokens_by_date, partial)) # TODO: there was[1:] on filtered

        # no tokens commited yet -> user is typing command, date or keyword
        if not filtered_committed_tokens_by_date:
            if partial.startswith(Config.data.input.keyword_prefix):
                return list(self._keyword_completions(partial))
            return list(self._name_completions(partial))

        first_token: str = filtered_committed_tokens_by_date[0]
        handler_committed: list[str] = filtered_committed_tokens_by_date[1:]

        # handle keyword typing
        if partial.startswith(Config.data.input.keyword_prefix):
            return list(self._keyword_completions(partial))

        # typed macro? -> get macro completions
        macro: MacroTemplate | None = MacroManager.macros.get(first_token)
        if macro is not None:
            completions = list(self._macro_completions(macro, handler_committed, partial))
        else: # typed command? -> get command completions
            command: Command | None = CommandParser.find_matching_command(first_token)
            if command is None:
                return []
            completions = list(self._command_completions(command, handler_committed, partial))

        if not completions and trailing_space and not partial:
            chain_symbol: str = Config.data.input.command_chain_symbol
            return [Completion(chain_symbol, start_position=0, display_meta=self._truncate_meta("chain another command", len(chain_symbol)))]
        return completions

    def _keyword_completions(self, partial: str):
        after_prefix: str = partial[len(Config.data.input.keyword_prefix):]
        matching: list[KeywordTemplate] = [
            keyword for keyword in KeywordManager.iterable_keywords
            if keyword.identifier.lower().startswith(after_prefix.lower())
        ]
        if not matching:
            return
        
        max_suggestion_width: int = max(len(Config.data.input.keyword_prefix + keyword.identifier) for keyword in matching)
        for keyword in matching:
            candidate: str = Config.data.input.keyword_prefix + keyword.identifier
            meta: str = self._get_keyword_meta(keyword.identifier)
            yield Completion(candidate, start_position=-len(partial), style="bg:ansigreen", display_meta=self._truncate_meta(meta, max_suggestion_width))

    def _get_keyword_meta(self, identifier: str) -> str:
        if self._state is None:
            return ""
        value: str = KeywordManager.get_keyword_value(identifier, self._state)
        return f"→ {value}" if value else ""

    def _name_completions(self, partial: str): # TODO: type hinting
        partial = partial.lower()
        seen: set[str] = set()
        raw: list[tuple[str, str, str]] = [] # (candidate, meta, color)

        for command in CommandManager.commands:
            if command.name not in seen and command.name.lower().startswith(partial):
                seen.add(command.name)
                raw.append((command.name, command.help.short_help_description[:1].lower() + command.help.short_help_description[1:], ""))

        for command in CommandManager.commands:
            for abbreviation in command.abbreviations:
                if abbreviation not in seen and abbreviation.lower().startswith(partial):
                    seen.add(abbreviation)
                    raw.append((abbreviation, f"abbrev. → {command.name}", "bg:ansibrightblack")) # TODO: make these configurable

        for alias_name, alias in AliasManager.aliases.items(): # TODO: aliases and macro first then commands ?
            if alias_name not in seen and alias_name.lower().startswith(partial):
                seen.add(alias_name)
                raw.append((alias_name, f"→ {alias.replacement_text}", "bg:ansiblue"))

        for macro in MacroManager.iterable_macros:
            if macro.identifier not in seen and macro.identifier.lower().startswith(partial):
                seen.add(macro.identifier)
                raw.append((macro.identifier, f"→ {macro.command_text}", "bg:ansired"))

        if not raw:
            return

        max_text: int = max(len(suggestion) for suggestion, _, _ in raw)

        for candidate, meta, style in raw:
            yield Completion(
                candidate,
                start_position=-len(partial),
                style=style,
                display_meta=self._truncate_meta(meta, max_text)
            )

    @staticmethod
    def _truncate_meta(meta: str, max_suggestion_width: int) -> str:
        suggestion_box: int = max(7, max_suggestion_width + 2)
        max_meta_width: int = Config.data.input.autocompletion.max_popup_width - suggestion_box - 3
        return meta if len(meta) <= max_meta_width else meta[:max_meta_width - 1].rstrip() + "…"

    def _macro_completions(self, macro: MacroTemplate, committed: list[str], partial: str):
        position: int = len(committed)
        if position >= len(macro.arguments):
            return
        arg_name: str = macro.arguments[position]
        default = macro.default_argument_values[position]
        meta: str = f"optional argument, default: {default}" if default is not None else "required argument"
        display: str = f"<{arg_name}>"
        if display.lower().startswith(partial.lower()):
            yield Completion(display, start_position=-len(partial), display_meta=self._truncate_meta(meta, len(display)))

    def _command_completions(self, command: Command, committed: list[str], partial: str):
        try:
            module: ModuleType = importlib.import_module(f"work_tracker.command.commands.{command.snake_case_name}")
            command_class: type = getattr(module, f"{command.camel_case_name}Handler")
        except (ImportError, AttributeError):
            return
        candidates: list[Completion | CompletionCandidate] = command_class.get_completions(committed, partial, self.in_subcommand_mode)
        yield from self._build_command_completions(candidates, partial)

    def _build_command_completions(self, candidates: list[Completion | CompletionCandidate], partial: str):
        completion_candidates: list[str] = [candidate.value for candidate in candidates if isinstance(candidate, CompletionCandidate) and isinstance(candidate.value, str)]
        completion_hints: list[str] = ["8h", "1:30", "90m", "1", "5", "10", "20", Config.data.input.command_chain_symbol] # TODO: temp hardcoded suggestions
        completions: list[str] = [candidate.text for candidate in candidates if isinstance(candidate, Completion)]
        max_suggestion_width: int = max((len(suggestion) for suggestion in completion_candidates + completion_hints + completions), default=0)

        for candidate in candidates:
            if isinstance(candidate, CompletionCandidate):
                if isinstance(candidate.value, CompletionHint):
                    if candidate.value == CompletionHint.Time:
                        for example in ("8h", "7:30", "8:30"): # TODO: handle examples properly, try to determine what user uses usually
                            if example.lower().startswith(partial.lower()):
                                yield Completion(example, start_position=-len(partial), display_meta=self._truncate_meta(candidate.meta or "time", max_suggestion_width))
                    elif candidate.value == CompletionHint.Integer:
                        for example in ("1", "2", "5", "10"):
                            if example.lower().startswith(partial.lower()):
                                yield Completion(example, start_position=-len(partial), display_meta=self._truncate_meta(candidate.meta or "number", max_suggestion_width))
                    elif candidate.value == CompletionHint.Chain:
                        if Config.data.input.command_chain_symbol.lower().startswith(partial.lower()):
                            yield Completion(Config.data.input.command_chain_symbol, start_position=-len(partial), display_meta=self._truncate_meta(candidate.meta or "chain another command", max_suggestion_width))
                elif isinstance(candidate.value, str) and candidate.value.lower().startswith(partial.lower()):
                    yield Completion(candidate.value, start_position=-len(partial), display_meta=self._truncate_meta(candidate.meta or "", max_suggestion_width))
            elif isinstance(candidate, Completion):
                yield candidate

    def activate_custom_autocomplete(self, autocomplete: list[str] | dict[str, str]):
        if isinstance(autocomplete, dict):
            self.words = list(autocomplete.keys())
            self.meta_dict = autocomplete
        else:
            self.words = autocomplete
            self.meta_dict = {}
        self.custom_autocomplete = True

    def deactivate_custom_autocomplete(self):
        self.custom_autocomplete = False
        self.words = []
        self.meta_dict = {}
