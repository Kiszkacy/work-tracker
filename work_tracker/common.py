from __future__ import annotations

import calendar
import datetime
import os
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Type, Callable

import appdirs
from multimethod import multimethod
from path import Path
from workalendar.core import CoreCalendar
from workalendar.registry import registry

from work_tracker.command.command_history import CommandHistoryEntry


month_map: dict[str, int] = { # 'jan', 'january', 'feb', 'february', ...
    **{month.lower(): index+1 for index, month in enumerate(calendar.month_name[1:])},
    **{month.lower(): index+1 for index, month in enumerate(calendar.month_abbr[1:])},
}


def get_cache_path() -> Path:
    cache_path: str = appdirs.user_cache_dir("work_tracker", "kiszkacy")
    os.makedirs(cache_path, exist_ok=True)
    return Path(cache_path).absolute()


def get_data_path() -> Path:
    data_path: str = appdirs.user_data_dir("work_tracker", "kiszkacy")
    os.makedirs(data_path, exist_ok=True)
    return Path(data_path).absolute()


def find_first_not_fulfilling(items: list[any], predicate: Callable[[list[any]], bool]) -> any | None:
    return next((item for item in items if not predicate(item)), None)


class KeyDefaultDict(defaultdict):
    def __init__(self, function: Callable[[any], any]):
        super().__init__(None)
        self.function: Callable[[any], any] = function

    def __missing__(self, key) -> any:
        value: any = self.function(key)
        self[key] = value
        return value

    def __reduce__(self):
        return self.__class__, (self.function,), dict(self)

    def __setstate__(self, state: any):
        self.update(state)


class classproperty:
    def __init__(self, func):
        self.fget = func

    def __get__(self, instance, owner):
        return self.fget(owner)


@dataclass(frozen=True)
class Time:
    minutes_since_midnight: int


@dataclass(frozen=True)
class Date:
    day: int | None = None
    month: int | None = None
    year: int | None = None

    @staticmethod
    def _day_count_in_a_month(date: Date) -> int:
        _, day_count = calendar.monthrange(date.year, date.month)
        return day_count

    @staticmethod
    @multimethod
    def day_count_in_a_month(date: Date) -> int:
        return Date._day_count_in_a_month(date)

    @multimethod
    def day_count_in_a_month(self) -> int:
        return Date._day_count_in_a_month(self)

    @staticmethod
    def _days_in_a_month(date: Date) -> list[Date]:
        result: list[Date] = []
        for day_index in range(date.day_count_in_a_month()):
            result.append(Date(day=day_index+1, month=date.month, year=date.year))
        return result

    @staticmethod
    @multimethod
    def days_in_a_month(date: Date) -> list[Date]:
        return Date._days_in_a_month(date)

    @multimethod
    def days_in_a_month(self) -> list[Date]:
        return Date._days_in_a_month(self)

    @staticmethod
    def _is_day_only_date(date: Date) -> bool:
        return date.day is not None and date.month is None and date.year is None

    @staticmethod
    @multimethod
    def is_day_only_date(date: Date) -> bool:
        return Date._is_day_only_date(date)

    @multimethod
    def is_day_only_date(self) -> bool:
        return Date._is_day_only_date(self)

    @staticmethod
    def _is_month_only_date(date: Date) -> bool:
        return date.day is None and date.month is not None and date.year is None

    @staticmethod
    @multimethod
    def is_month_only_date(date: Date) -> bool:
        return Date._is_month_only_date(date)

    @multimethod
    def is_month_only_date(self) -> bool:
        return Date._is_month_only_date(self)

    @staticmethod
    def _is_year_only_date(date: Date) -> bool:
        return date.day is None and date.month is None and date.year is not None

    @staticmethod
    @multimethod
    def is_year_only_date(date: Date) -> bool:
        return Date._is_year_only_date(date)

    @multimethod
    def is_year_only_date(self) -> bool:
        return Date._is_year_only_date(self)

    @staticmethod
    def _is_full_date(date: Date) -> bool:
        return date.day is not None and date.month is not None and date.year is not None

    @staticmethod
    @multimethod
    def is_full_date(date: Date) -> bool:
        return Date._is_full_date(date)

    @multimethod
    def is_full_date(self) -> bool:
        return Date._is_full_date(self)

    @staticmethod
    def _is_year_date(date: Date) -> bool:
        return Date._is_year_only_date(date)

    @staticmethod
    @multimethod
    def is_year_date(date: Date) -> bool:
        return Date._is_year_date(date)

    @multimethod
    def is_year_date(self) -> bool:
        return Date._is_year_date(self)

    @staticmethod
    def _is_month_date(date: Date) -> bool:
        return date.day is None and date.month is not None

    @staticmethod
    @multimethod
    def is_month_date(date: Date) -> bool:
        return Date._is_month_date(date)

    @multimethod
    def is_month_date(self) -> bool:
        return Date._is_month_date(self)

    @staticmethod
    def _is_day_date(date: Date) -> bool:
        return date.day is not None

    @staticmethod
    @multimethod
    def is_day_date(date: Date) -> bool:
        return Date._is_day_date(date)

    @multimethod
    def is_day_date(self) -> bool:
        return Date._is_day_date(self)

    @staticmethod
    def _to_year_date(date: Date) -> Date:
        return Date(day=None, month=None, year=date.year)

    @staticmethod
    @multimethod
    def to_year_date(date: Date) -> Date:
        return Date._to_year_date(date)

    @multimethod
    def to_year_date(self) -> Date:
        return Date._to_year_date(self)

    @staticmethod
    def _to_month_date(date: Date) -> Date:
        return Date(day=None, month=date.month, year=date.year)

    @staticmethod
    @multimethod
    def to_month_date(date: Date) -> Date:
        return Date._to_month_date(date)

    @multimethod
    def to_month_date(self) -> Date:
        return Date._to_month_date(self)

    @staticmethod
    def _to_day_date(date: Date) -> Date:
        return Date(day=date.day, month=date.month, year=date.year)

    @staticmethod
    @multimethod
    def to_day_date(date: Date) -> Date:
        return Date._to_day_date(date)

    @multimethod
    def to_day_date(self) -> Date:
        return Date._to_day_date(self)

    @staticmethod
    def _fill_with(date: Date, with_: Date) -> Date:
        return Date(
            day=date.day if date.day is not None else with_.day,
            month=date.month if date.month is not None else with_.month,
            year=date.year if date.year is not None else with_.year,
        )

    def fill_with(self, date: Date) -> Date:
        return Date._fill_with(self, date)

    def fill_with_today(self) -> Date:
        return Date._fill_with(self, Date.today())

    @staticmethod
    def _fill_date_with(date: Date, with_: Date) -> Date:
        return Date._fill_with(date, with_)

    @staticmethod
    def fill_date_with_today(date: Date) -> Date:
        return Date._fill_with(date, Date.today())

    @staticmethod
    def from_datetime(date: datetime.date) -> Date:
        return Date(day=date.day, month=date.month, year=date.year)

    @staticmethod
    def _to_datetime(date: Date) -> datetime.date:
        if not date.day or not date.month or not date.year:
            raise ValueError("Incomplete date: day, month, and year must all be provided.")
        return datetime.date(day=date.day, month=date.month, year=date.year)

    @staticmethod
    @multimethod
    def to_datetime(date: Date) -> datetime.date:
        return Date._to_datetime(date)

    @multimethod
    def to_datetime(self) -> datetime.date:
        return Date._to_datetime(self)

    @staticmethod
    def today() -> Date:
        return Date.from_datetime(datetime.date.today())

    @staticmethod
    def normalize_dates(dates: list[Date], preserve_order: bool = False) -> list[Date]:
        if preserve_order:
            seen: set[Date] = set()

            years: list[Date] = []
            months: list[Date] = []
            specific_dates: list[Date] = []

            for date in dates:
                if date in seen:
                    continue
                seen.add(date)
                if date.day is None and date.month is None and date.year is not None:
                    years.append(date)
                elif date.day is None and date.month is not None and date.year is None:
                    months.append(date)
                elif date.month is not None or date.day is not None:
                    specific_dates.append(date)
        else:
            years: set[Date] = set(date for date in dates if date.day is None and date.month is None and date.year is not None)
            months: set[Date] = set(date for date in dates if date.day is None and date.month is not None and date.year is None)
            specific_dates: set[Date] = set(date for date in dates if date.month is not None or date.day is not None)

        normalized_dates: list[Date] = [
            date for date in specific_dates
            if not any(date.year == year_date.year for year_date in years) and not any(date.month == month_date.month and date.year is None for month_date in months)
        ]
        normalized_dates.extend(years)
        normalized_dates.extend(months)

        return normalized_dates


@dataclass
class DayData: # add setters for remote/office so they autofill properly
    is_a_work_day: bool = False
    minutes_at_work: int = 0
    target_minutes: int = 0
    remote_work: bool | None = None
    office_work: bool | None = None
    is_a_day_off: bool = False
    work_start: Time | None = None
    work_end: Time | None = None

    def __post_init__(self):
        if self.is_a_work_day and self.remote_work is None:
            self.remote_work = False
        if self.is_a_work_day and self.office_work is None:
            self.office_work = False

    def reset(self, is_a_work_day: bool = False):
        self.is_a_work_day = is_a_work_day
        self.minutes_at_work = 0
        self.target_minutes = 0
        self.remote_work = False if is_a_work_day else None
        self.office_work = False if is_a_work_day else None
        self.is_a_day_off = False


@dataclass
class MonthData:
    target_minutes: int
    remote_work_ratio: float
    fte: float = 1.0
    target_office_days: int | None = None
    target_remote_days: int | None = None


class WorkStrategy(Enum):
    Default = auto()
    Quick = auto()


@dataclass
class WorkSetup:
    default_fte: float = 1.0
    preferred_weekdays: list[int] = field(default_factory=list)
    non_availability_weekdays: list[int] = field(default_factory=list)
    default_remote_work_ratio: float = 0.4
    preferred_remote_weekdays: list[int] = field(default_factory=list)
    preferred_office_day_length_in_minutes: int | None = 480
    preferred_remote_day_length_in_minutes: int | None = 480
    office_day_max_length_in_minutes: int | None = 600
    remote_day_max_length_in_minutes: int | None = 600
    each_weekday_max_length_in_minutes: list[int | None] = field(default_factory=lambda: [None, None, None, None, None])
    strategy: WorkStrategy = WorkStrategy.Default


__data_version__: int = 1


@dataclass
class AppData:
    country_code: str
    setup: WorkSetup = field(init=False)
    day: defaultdict[Date, DayData] = field(init=False) # when using KeyDefaultDict as a typehint pycharm IDE breaks and stops suggesting any methods or properties
    month: defaultdict[Date, MonthData] = field(init=False)
    calendar: CoreCalendar = field(init=False, repr=False)
    _version: int = field(init=False)

    def __post_init__(self): # this runs only once when user creates new AppData (first time prompt)
        self._version = __data_version__
        self.setup = WorkSetup()

        self.calendar = AppData._determine_country(self.country_code)
        if self.calendar is None:
            raise ValueError(f"Unknown calendar for country with ISO code: {self.country_code}")
        
        self.day = KeyDefaultDict(self._on_day_initialization)
        self.month = KeyDefaultDict(self._on_month_initialization)

    @staticmethod
    def _determine_country(country_code: str) -> CoreCalendar | None:
        calendars: dict[str, Type[CoreCalendar]] = registry.get_calendars()
        calendar: Type[CoreCalendar] | None = calendars.get(country_code)
        if calendar is not None:
            return calendars.get(country_code)()
        return None

    def _on_day_initialization(self, date: Date) -> DayData:
        return DayData(is_a_work_day=self.calendar.is_working_day(date.to_datetime()))
        
    def _on_month_initialization(self, date: Date) -> MonthData:
        target_minutes_total: int = sum([480 * self.setup.default_fte if self.calendar.is_working_day(day.to_datetime()) else 0 for day in date.days_in_a_month()])
        return MonthData(target_minutes=target_minutes_total, remote_work_ratio=self.setup.default_remote_work_ratio, fte=self.setup.default_fte)

    def copy_from(self, data: AppData):
        if self._version != data._version:
            raise Exception() # TODO
        self.country_code = data.country_code
        self.setup = data.setup
        self.day = data.day
        self.month = data.month
        self.calendar = data.calendar

    @property
    def version(self) -> int:
        return self._version

    def is_latest_data_version(self) -> bool:
        return self.version == __data_version__

    def update_data_to_latest_version(self):
        # if loading a very old version run each updater in order A -> A+1 -> A+2 -> A+3 -> ... B
        pass


class Mode(Enum):
    Today = auto()
    Day = auto()
    Month = auto()


@dataclass
class AppState:
    active_date: Date = Date.from_datetime(datetime.date.today())
    mode: Mode = Mode.Today


# cant use inheritance due to 'Frozen dataclasses can not inherit non-frozen one and vice versa'
@dataclass(frozen=True)
class ReadonlyAppState:
    active_date: Date
    mode: Mode
    states: tuple[CommandHistoryEntry]
    current_state_index: int