from datetime import datetime, timedelta
from dataclasses import dataclass

from work_tracker.common import Mode, ReadonlyAppState, classproperty


@dataclass(frozen=True)
class KeywordTemplate:
    identifier: str
    description: str
    supported_modes: set[Mode]


class KeywordManager:
    _keywords: dict[str, KeywordTemplate] = {}
    _initialized: bool = False

    @classproperty
    def keywords(cls) -> dict[str, KeywordTemplate]:
        cls._check_initialization()
        return cls._keywords # TODO deepcopy

    @classproperty
    def iterable_keywords(cls) -> list[KeywordTemplate]:
        cls._check_initialization()
        return list(cls._keywords.values())
    
    @classmethod
    def _check_initialization(cls):
        if not cls._initialized:
            cls._keywords = cls._initialize_keywords()
            cls._initialized = True

    @classmethod
    def _initialize_keywords(cls) -> dict[str, KeywordTemplate]:
        return {
            "today": KeywordTemplate(
                identifier="today",
                description="Current system date",
                supported_modes={Mode.Today, Mode.Day, Mode.Month}
            ),
            "tomorrow": KeywordTemplate(
                identifier="tomorrow",
                description="Tomorrow's date",
                supported_modes={Mode.Today, Mode.Day, Mode.Month}
            ),
            "yesterday": KeywordTemplate(
                identifier="yesterday",
                description="Yesterday's date",
                supported_modes={Mode.Today, Mode.Day, Mode.Month}
            ),
            "nextday": KeywordTemplate(
                identifier="nextday",
                description="Next day from active date",
                supported_modes={Mode.Today, Mode.Day}
            ),
            "prevday": KeywordTemplate(
                identifier="prevday",
                description="Previous day from active date",
                supported_modes={Mode.Today, Mode.Day}
            ),
            "month": KeywordTemplate(
                identifier="month",
                description="Active month",
                supported_modes={Mode.Today, Mode.Day, Mode.Month}
            ),
            "nextmonth": KeywordTemplate(
                identifier="nextmonth",
                description="Next month from active date",
                supported_modes={Mode.Today, Mode.Day, Mode.Month}
            ),
            "prevmonth": KeywordTemplate(
                identifier="prevmonth",
                description="Previous month from active date",
                supported_modes={Mode.Today, Mode.Day, Mode.Month}
            ),
        }

    @classmethod
    def _format_date(cls, date: datetime) -> str:
        return date.strftime("%d.%m.%Y") # TODO it would be neat if this format was configurable, but the input must change too => parser would have to have dynamic logic

    @classmethod
    def _format_month(cls, date: datetime) -> str:
        return date.strftime(".%m.%Y") # TODO check if this is possible to format easily via Date class

    @classmethod
    def get_keyword_value(cls, keyword: str, state: ReadonlyAppState) -> str:
        match_state: tuple[str, Mode] = (keyword.lower(), state.mode)
        match match_state:
            case ('today', _): # TODO how is Mode.Today handled the same way ? comparing to the system time ?
                today: datetime = datetime.now()
                return cls._format_date(today)
            
            case ('tomorrow', _):
                today: datetime = datetime.now()
                return cls._format_date(today + timedelta(days=1))
            
            case ('yesterday', _):
                today: datetime = datetime.now()
                return cls._format_date(today - timedelta(days=1))
            
            case ('nextday', Mode.Month):
                return ""
            
            case ('nextday', _):
                active_datetime: datetime = state.active_date.fill_with_today().to_datetime()
                return cls._format_date(active_datetime + timedelta(days=1))

            case ('prevday', Mode.Month):
                return ""
            
            case ('prevday', _):
                active_datetime: datetime = state.active_date.fill_with_today().to_datetime()
                return cls._format_date(active_datetime - timedelta(days=1))

            case ('month', _):
                return cls._format_month(datetime(state.active_date.year, state.active_date.month, 1))

            case ('nextmonth', _):
                if state.active_date.month == 12:
                    next_month = datetime(state.active_date.year + 1, 1, 1)
                else:
                    next_month = datetime(state.active_date.year, state.active_date.month + 1, 1)
                return cls._format_month(next_month)

            case ('prevmonth', _):
                if state.active_date.month == 1:
                    prev_month = datetime(state.active_date.year - 1, 12, 1)
                else:
                    prev_month = datetime(state.active_date.year, state.active_date.month - 1, 1)
                return cls._format_month(prev_month)

            case _:
                return ""
        
        return ""
