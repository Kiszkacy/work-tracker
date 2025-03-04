from __future__ import annotations

import re
import textwrap
from enum import Enum, auto
from re import Match

from work_tracker.config import Config


ansi_pattern: str = r'\033\[[0-9;]*m'
ansi_pattern_compiled: re = re.compile(ansi_pattern)
about_symbol: str = "≈"


class Color(Enum): # TODO rethink these names
    Reset = "\033[0m"
    Clear = "\033[0m"
    Default = "\033[0m"

    Bold = "\033[1m" # TODO bold + color = bright color
    Dim = "\033[2m"
    Italic = "\033[3m"
    Underline = "\033[4m"
    Blink = "\033[5m"
    Reverse = "\033[7m"
    Hidden = "\033[8m"

    Black = "\033[30m"
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    White = "\033[37m"

    Brightblack = "\033[90m"
    Brightred = "\033[91m"
    Brightgreen = "\033[92m"
    Brightyellow = "\033[93m"
    Brightblue = "\033[94m"
    Brightmagenta = "\033[95m"
    Brightcyan = "\033[96m"
    Brightwhite = "\033[97m"

    BG_Black = "\033[40m"
    BG_Red = "\033[41m"
    BG_Green = "\033[42m"
    BG_Yellow = "\033[43m"
    BG_Blue = "\033[44m"
    BG_Magenta = "\033[45m"
    BG_Cyan = "\033[46m"
    BG_White = "\033[47m"

    BG_Brightblack = "\033[100m"
    BG_Brightred = "\033[101m"
    BG_Brightgreen = "\033[102m"
    BG_Brightyellow = "\033[103m"
    BG_Brightblue = "\033[104m"
    BG_Brightmagenta = "\033[105m"
    BG_Brightcyan = "\033[106m"
    BG_Brightwhite = "\033[107m"

    @staticmethod
    def from_key(key: str) -> Color | None:
        key = key.strip().lower()
        try:
            if len(key) != 0 and "_" in key and key[0] != "_" and key[-1] != 0:
                bg, rest = key.split("_", 1)
                return Color[f"{bg.upper(), rest.capitalize()}"]
            else:
                return Color[key.capitalize()]
        except KeyError:
            return None


def strip_ansi(text: str) -> str:
    return ansi_pattern_compiled.sub("", text)


def _reinsert_ansi(wrapped_text: str, original_text: str) -> str: # TODO refactor this
    original_text_without_whitespace_characters: str = original_text.replace("\n", "").replace(" ", "")
    matches: list[Match[str]] = [match for match in ansi_pattern_compiled.finditer(original_text_without_whitespace_characters)]

    position_without_whitespace_characters: int = 0
    real_position: int = 0
    current_match_index: int = 0
    while real_position < len(wrapped_text) + 1 and current_match_index < len(matches): # +1 to handle real_position == len(wrapped_text) <-> code at the end of string
        if matches[current_match_index].group() != Color.Reset.value: # TODO this fixes underline but code is messier
            if real_position == len(wrapped_text):
                break

            while wrapped_text[real_position] in ["\n", " "]:
                real_position += 1
        
        if position_without_whitespace_characters == matches[current_match_index].start():
            wrapped_text = wrapped_text[:real_position] + matches[current_match_index].group() + wrapped_text[real_position:]
            real_position += len(matches[current_match_index].group())-1
            position_without_whitespace_characters += len(matches[current_match_index].group())-1
            current_match_index += 1

        if real_position == len(wrapped_text):
            break

        while wrapped_text[real_position] in ["\n", " "]:
            real_position += 1

        position_without_whitespace_characters += 1
        real_position += 1

    return wrapped_text


def _wrap_text(text: str, width: int) -> str:
    stripped: str = strip_ansi(text)
    wrapped: str = textwrap.fill(text=stripped, width=width, break_on_hyphens=False, break_long_words=False)
    return _reinsert_ansi(wrapped_text=wrapped, original_text=text)


def wrap_text( # TODO doesnt work when one word is longer than width (wont break the word)
    text: str,
    width: int = None,
    indent: str = "",
    omit_first_line_indent: bool = False,
    preserve_newlines: bool = True,
    frame_wrap: bool = False
) -> str:
    if width is None:
        width = Config.data.output.max_width
    calculated_width: int = width - len(indent) - (Config.data.output.frame.padding*2 + 2 if frame_wrap else 0)
    if not preserve_newlines:
        wrapped_text: str = f"{indent if not omit_first_line_indent else ''}{_wrap_text(text, calculated_width)}"
        wrapped_text = wrapped_text.replace("\n", f"\n{indent}")
        return wrapped_text
    else:
        lines: list[str] = text.splitlines()
        wrapped_lines: list[str] = [_wrap_text(line, calculated_width) for line in lines]
        wrapped_text: str = "\n".join(wrapped_lines).replace("\n", f"\n{indent}")
        return f"{indent if not omit_first_line_indent else ''}{wrapped_text}"


class FrameStyle(Enum):
    Single = auto()
    Double = auto()
    Rounded = auto()


# TODO frame breaks when the provided text max width is < title length
# TODO width should be max(longest_provided_text_width, 2 + padding*2 + (title_left_side_padding*2 # even if its centered) + title.length)
def frame_text(
    text: str,
    minimal_width: int = None,
    minimal_line_width: int = None,
    title: str = None,
    center_title: bool = False,
    footer_title: bool = False,
    frame_style: FrameStyle = FrameStyle.Rounded,
    skip_bottom_line: bool = False,
    extend_top_line: bool = False,
    frame_color: Color = Color.Default,
    title_color: Color = Color.Default
) -> str:
    styles: dict[FrameStyle, tuple[str, str, str, str, str, str, str, str]] = {
        FrameStyle.Single: ("┌", "─", "┐", "│", "└", "┘", "├", "┤"),
        FrameStyle.Double: ("╔", "═", "╗", "║", "╚", "╝", "╠", "╣"),
        FrameStyle.Rounded: ("╭", "─", "╮", "│", "╰", "╯", "├", "┤"),
    }
    top_left, horizontal, top_right, vertical, bottom_left, bottom_right, top_left_extension, top_right_extension = styles[frame_style]

    padding: int = Config.data.output.frame.padding
    lines: list[str] = text.split("\n")
    max_width: int = max([len(title or '') + padding*2 + Config.data.output.frame.title_padding*2 or 0] + [(minimal_line_width or 0)] + [(minimal_width or 0) - (padding*2 + 2)] + [len(strip_ansi(line)) for line in lines])

    if title is not None and not footer_title:
        title = f"{title_color.value}{' '*Config.data.output.frame.title_padding}{title}{' '*Config.data.output.frame.title_padding}{frame_color.value}"
        title_width: int = len(strip_ansi(title))
        start_title_at: int = (max_width + padding*2 - title_width) // 2 if center_title else Config.data.output.frame.title_left_side_padding
        top_border: str = f"{top_left_extension if extend_top_line else top_left}{horizontal * (max_width + padding * 2)}{top_right_extension if extend_top_line else top_right}"
        top_border = top_border[:start_title_at + 1] + title + top_border[start_title_at + title_width + 1:]
        top_border = f"{frame_color.value}{top_border}{Color.Reset.value}"
    else:
        top_border: str = f"{frame_color.value}{top_left_extension if extend_top_line else top_left}{horizontal * (max_width + padding * 2)}{top_right_extension if extend_top_line else top_right}{Color.Reset.value}"

    framed_lines: list[str] = []
    last_known_color_in_text: str | None = None
    for line in lines:
        framed_lines.append(f"{frame_color.value}{vertical}{last_known_color_in_text or Color.Reset.value}{' ' * padding}{line}{' ' * (max_width - len(strip_ansi(line)))}{' ' * padding}{frame_color.value}{vertical}{Color.Reset.value}")
        last_known_color_in_text = (re.findall(ansi_pattern_compiled, line)[-1] if re.findall(ansi_pattern_compiled, line) else last_known_color_in_text)

    if title is not None and footer_title:
        title = f"{title_color.value}{' '*Config.data.output.frame.title_padding}{title}{' '*Config.data.output.frame.title_padding}{frame_color.value}"
        title_width: int = len(strip_ansi(title))
        start_title_at: int = (max_width + padding * 2 - title_width) // 2 if center_title else (max_width + padding * 2 - title_width - Config.data.output.frame.title_footer_right_side_padding)
        bottom_border: str = f"{bottom_left}{horizontal * (max_width + padding*2)}{bottom_right}"
        bottom_border = bottom_border[:start_title_at + 1] + title + bottom_border[start_title_at + title_width + 1:]
        bottom_border = f"{frame_color.value}{bottom_border}{Color.Reset.value}"
    else:
        bottom_border: str = f"{frame_color.value}{bottom_left}{horizontal * (max_width + padding*2)}{bottom_right}{Color.Reset.value}"

    result: list[str] = [top_border] + framed_lines
    if not skip_bottom_line:
        result.append(bottom_border)
    return "\n".join(result)


class TextWriter:
    def __init__(self):
        self.text: str = ""

    def color(self, color: Color) -> TextWriter:
        self.text += color

        return self

    def write(self, text: str, color: Color = None) -> TextWriter:
        if color is not None:
            self.text += color.value

        self.text += text

        if color is not None:
            self.text += Color.Reset.value

        return self

    def clear(self):
        self.text = ""
