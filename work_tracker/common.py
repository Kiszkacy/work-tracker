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


class AttendanceType(Enum):
    PRESENT = auto()
    DAYOFF = auto()
    ABSENCE = auto()


class DayType(Enum):
    WORKDAY = auto()
    WEEKEND = auto()
    HOLIDAY = auto()


class WorkLocation(Enum):
    UNSPECIFIED = auto()
    REMOTE = auto()
    OFFICE = auto()


@dataclass
class DayData: # add setters for remote/office so they autofill properly
    attendance_type: AttendanceType = AttendanceType.PRESENT
    day_type: DayType = DayType.WORKDAY
    work_location: WorkLocation = WorkLocation.UNSPECIFIED  
    minutes_at_work: int = 0
    target_minutes: int = 0
    work_start: Time | None = None
    work_end: Time | None = None

    def reset(self, day_type: DayType = DayType.WORKDAY):
        self.attendance_type = AttendanceType.PRESENT
        self.day_type = day_type
        self.work_location = WorkLocation.UNSPECIFIED
        self.minutes_at_work = 0
        self.target_minutes = 0
        self.work_start = None
        self.work_end = None


@dataclass
class MonthData:
    target_minutes: int
    remote_work_ratio: float
    fte: float = 1.0
    # v2 deleted
    # target_office_days: int | None = None
    # target_remote_days: int | None = None


__data_version__: int = 2


@dataclass
class AppData:
    country_code: str
    day: defaultdict[Date, DayData] = field(init=False) # when using KeyDefaultDict as a typehint pycharm IDE breaks and stops suggesting any methods or properties
    month: defaultdict[Date, MonthData] = field(init=False)
    calendar: CoreCalendar = field(init=False, repr=False)
    _version: int = field(init=False)

    def __post_init__(self): # this runs only once when user creates new AppData (first time prompt)
        self._version = __data_version__

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
        datetime_date: datetime.date = date.to_datetime()
        
        if self.calendar.is_working_day(datetime_date):
            day_type = DayType.WORKDAY
        elif self.calendar.is_holiday(datetime_date):
            day_type = DayType.HOLIDAY
        else:
            day_type = DayType.WEEKEND
        
        return DayData(
            day_type=day_type,
            attendance_type=AttendanceType.PRESENT,
            work_location=WorkLocation.UNSPECIFIED
        )
        
    def _on_month_initialization(self, date: Date) -> MonthData:
        from work_tracker.config import Config
        default_fte: float = Config.data.command.fte.default_value
        default_remote_work_ratio: float = Config.data.command.rwr.default_value
        target_minutes_total: int = sum([480 * default_fte if self.calendar.is_working_day(day.to_datetime()) else 0 for day in date.days_in_a_month()])
        return MonthData(target_minutes=target_minutes_total, remote_work_ratio=default_remote_work_ratio, fte=default_fte)

    def copy_from(self, data: AppData):
        if self._version != data._version:
            raise Exception() # TODO
        self.country_code = data.country_code
        self.day = data.day
        self.month = data.month
        self.calendar = data.calendar

    @property
    def version(self) -> int:
        return self._version

    def is_latest_data_version(self) -> bool:
        return self.version == __data_version__

    def _update_data_to_v2(self):
        for date, day_data in self.day.items():
            # get old values
            old_is_a_work_day: bool = getattr(day_data, 'is_a_work_day', False)
            old_is_a_day_off: bool = getattr(day_data, 'is_a_day_off', False)
            old_remote_work: bool | None = getattr(day_data, 'remote_work', None)
            old_office_work: bool | None = getattr(day_data, 'office_work', None)
            # config attendance_type
            attendance_type: AttendanceType
            if old_is_a_day_off:
                attendance_type = AttendanceType.DAYOFF
            else:
                attendance_type = AttendanceType.PRESENT
            # config day_type
            day_type: DayType
            if old_is_a_work_day:
                day_type = DayType.WORKDAY
            else:
                datetime_date: datetime.date = date.to_datetime()
                if self.calendar.is_holiday(datetime_date):
                    day_type = DayType.HOLIDAY
                else:
                    day_type = DayType.WEEKEND
            # config work_location
            work_location: WorkLocation
            if old_remote_work is True:
                work_location = WorkLocation.REMOTE
            elif old_office_work is True:
                work_location = WorkLocation.OFFICE
            else:
                work_location = WorkLocation.UNSPECIFIED
            # setup new fields
            day_data.attendance_type = attendance_type
            day_data.day_type = day_type
            day_data.work_location = work_location
            # remove old fields
            if hasattr(day_data, 'is_a_work_day'):
                delattr(day_data, 'is_a_work_day')
            if hasattr(day_data, 'is_a_day_off'):
                delattr(day_data, 'is_a_day_off')
            if hasattr(day_data, 'remote_work'):
                delattr(day_data, 'remote_work')
            if hasattr(day_data, 'office_work'):
                delattr(day_data, 'office_work')
        
        # remove old appData field
        if hasattr(self, 'setup'):
            delattr(self, 'setup')
        # remove old monthData fields
        for date, month_data in self.month.items():
            if hasattr(month_data, 'target_office_days'):
                delattr(month_data, 'target_office_days')
            if hasattr(month_data, 'target_remote_days'):
                delattr(month_data, 'target_remote_days')

    def update_data_to_latest_version(self):
        # if loading a very old version run each updater in order A -> A+1 -> A+2 -> A+3 -> ... B
        current_version: int = self._version
        
        if current_version == 1:
            self._update_data_to_v2()
            current_version = 2


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