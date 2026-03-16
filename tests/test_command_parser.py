import pytest

from tests.conftest import sample_data
from work_tracker.command.command_parser import CommandParser
from work_tracker.command.common import ParseResult, TimeArgument, TimeArgumentType
from work_tracker.common import AppData, Date


@pytest.mark.order(1)
def test_should_correctly_parse_different_times():
    test_cases: list[tuple[str, TimeArgument]] = [
        ("8:00", TimeArgument(minutes=480, type=TimeArgumentType.Overwrite)),
        ("7h", TimeArgument(minutes=420, type=TimeArgumentType.Overwrite)),
        # ("6 h", TimeArgument(minutes=360, type=TimeArgumentType.Overwrite)), # this case wont work because of the 'h' alias
        ("5hours", TimeArgument(minutes=300, type=TimeArgumentType.Overwrite)),
        ("4 hours", TimeArgument(minutes=240, type=TimeArgumentType.Overwrite)),
        ("3hour", TimeArgument(minutes=180, type=TimeArgumentType.Overwrite)),
        ("2 hour", TimeArgument(minutes=120, type=TimeArgumentType.Overwrite)),
        ("300minutes", TimeArgument(minutes=300, type=TimeArgumentType.Overwrite)),
        ("290 minutes", TimeArgument(minutes=290, type=TimeArgumentType.Overwrite)),
        ("280minute", TimeArgument(minutes=280, type=TimeArgumentType.Overwrite)),
        ("270 minute", TimeArgument(minutes=270, type=TimeArgumentType.Overwrite)),
        ("260mins", TimeArgument(minutes=260, type=TimeArgumentType.Overwrite)),
        ("250 mins", TimeArgument(minutes=250, type=TimeArgumentType.Overwrite)),
        ("240min", TimeArgument(minutes=240, type=TimeArgumentType.Overwrite)),
        ("230 min", TimeArgument(minutes=230, type=TimeArgumentType.Overwrite)),
        ("220m", TimeArgument(minutes=220, type=TimeArgumentType.Overwrite)),
        ("210 m", TimeArgument(minutes=210, type=TimeArgumentType.Overwrite)),
    ]

    for text, expected in test_cases:
        data: AppData = sample_data()
        for prefix in ("+", "+ ", "-", "- ", ""):
            parse_result: ParseResult = CommandParser.parse(prefix + text, data)
            assert parse_result.error is None
            assert len(parse_result.queries) == 1
            assert parse_result.queries[0].command.name == "__time"
            assert len(parse_result.queries[0].arguments) == 1
            assert isinstance(parse_result.queries[0].arguments[0], TimeArgument)
            assert parse_result.queries[0].arguments[0].minutes == expected.minutes
            if prefix.strip() == "+":
                assert parse_result.queries[0].arguments[0].type == TimeArgumentType.Add
            elif prefix.strip() == "-":
                assert parse_result.queries[0].arguments[0].type == TimeArgumentType.Subtract
            else:
                assert parse_result.queries[0].arguments[0].type == TimeArgumentType.Overwrite


@pytest.mark.order(1)
def test_should_correctly_parse_different_dates():
    test_cases: list[tuple[str, Date]] = [
        ("22.", Date(year=None, month=None, day=22)),
        ("01.", Date(year=None, month=None, day=1)),
        ("2.", Date(year=None, month=None, day=2)),
        ("03.12", Date(year=None, month=12, day=3)),
        ("2.11", Date(year=None, month=11, day=2)),
        ("10.10", Date(year=None, month=10, day=10)),
        ("30.12.98", Date(year=1998, month=12, day=30)),
        ("01.02.03", Date(year=2003, month=2, day=1)),
        ("2.3.4", Date(year=2004, month=3, day=2)),
        ("03.04.2005", Date(year=2005, month=4, day=3)),
        ("4.5.2006", Date(year=2006, month=5, day=4)),

        (".03.", Date(year=None, month=3, day=None)),
        (".4.", Date(year=None, month=4, day=None)),
        (".05.2007", Date(year=2007, month=5, day=None)),
        (".6.08", Date(year=2008, month=6, day=None)),

        ("feb", Date(year=None, month=2, day=None)),
        ("february", Date(year=None, month=2, day=None)),
    ]

    for text, expected in test_cases:
        data: AppData = sample_data()
        parse_result: ParseResult = CommandParser.parse(text, data)
        assert parse_result.error is None
        assert len(parse_result.queries) == 1
        assert parse_result.queries[0].command.name == "__date"
        assert len(parse_result.queries[0].arguments) == 0
        assert parse_result.queries[0].date_count == 1
        assert parse_result.queries[0].dates[0] == expected


# @pytest.mark.order(1)
# def test_should_correctly_parse_multiple_dates():
#     test_cases: list[tuple[str, list[Date]]] = [
#         ("22. 23. 24.", [Date(year=None, month=None, day=22), Date(year=None, month=None, day=23), Date(year=None, month=None, day=24)]),
#         ("22. 23. 24.", [Date(year=None, month=None, day=22), Date(year=None, month=None, day=23), Date(year=None, month=None, day=24)]),
#         ("22. 23. 24.", [Date(year=None, month=None, day=22), Date(year=None, month=None, day=23), Date(year=None, month=None, day=24)]),
#     ]

#     for text, expected in test_cases:
#         data: AppData = sample_data()
#         parse_result: ParseResult = CommandParser.parse(text, data)
#         assert parse_result.error is None
#         assert len(parse_result.queries) == 1
#         assert parse_result.queries[0].command.name == "__date"
#         assert len(parse_result.queries[0].arguments) == 0
#         assert parse_result.queries[0].date_count == 1
#         assert parse_result.queries[0].dates[0] == expected