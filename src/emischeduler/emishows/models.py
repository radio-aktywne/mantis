from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, Field, NaiveDatetime
from typing_extensions import TypedDict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from emischeduler.models.base import SerializableModel

SortMode = Literal["default", "insensitive"]
SortOrder = Literal["asc", "desc"]

StringFilter = TypedDict(
    "StringFilter",
    {
        "equals": str,
        "not_in": list[str],
        "lt": str,
        "lte": str,
        "gt": str,
        "gte": str,
        "contains": str,
        "startswith": str,
        "endswith": str,
        "in": list[str],
        "not": "str | StringFilter",
        "mode": SortMode,
    },
    total=False,
)


class EventType(StrEnum):
    """Event type."""

    live = "live"
    replay = "replay"
    prerecorded = "prerecorded"


class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: str | StringFilter
    type: EventType
    showId: str | StringFilter

    AND: list["EventWhereInput"]
    OR: list["EventWhereInput"]
    NOT: list["EventWhereInput"]


class EventInclude(TypedDict, total=False):
    """Event relational arguments."""

    show: bool


class EventIdOrderByInput(TypedDict, total=True):
    """Event order by id."""

    id: SortOrder


class EventTypeOrderByInput(TypedDict, total=True):
    """Event order by type."""

    type: SortOrder


class EventShowIdOrderByInput(TypedDict, total=True):
    """Event order by showId."""

    showId: SortOrder


class EventStartOrderByInput(TypedDict, total=True):
    """Order by start time."""

    start: SortOrder


class EventEndOrderByInput(TypedDict, total=True):
    """Order by end time."""

    end: SortOrder


class EventTimezoneOrderByInput(TypedDict, total=True):
    """Order by timezone."""

    timezone: SortOrder


EventOrderByInput = (
    EventIdOrderByInput
    | EventTypeOrderByInput
    | EventShowIdOrderByInput
    | EventStartOrderByInput
    | EventEndOrderByInput
    | EventTimezoneOrderByInput
)


class TimezoneValidationError(ValueError):
    """Timezone validation error."""

    def __init__(self, value: str) -> None:
        super().__init__(f"Invalid time zone: {value}")


def validate_timezone(value: str) -> str:
    """Validate a time zone."""

    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as e:
        raise TimezoneValidationError(value) from e

    return value


Timezone = Annotated[str, AfterValidator(validate_timezone)]


class Show(SerializableModel):
    """Show model."""

    id: UUID = Field(
        ...,
        title="Show.Id",
        description="Identifier of the show.",
    )
    title: str = Field(
        ...,
        title="Show.Title",
        description="Title of the show.",
    )
    description: str | None = Field(
        None,
        title="Show.Description",
        description="Description of the show.",
    )
    events: list["Event"] | None = Field(
        None,
        title="Show.Events",
        description="Events belonging to the show.",
    )


Frequency = Literal[
    "secondly",
    "minutely",
    "hourly",
    "daily",
    "weekly",
    "monthly",
    "yearly",
]

Second = Annotated[int, Field(..., ge=0, le=60)]

Minute = Annotated[int, Field(..., ge=0, le=59)]

Hour = Annotated[int, Field(..., ge=0, le=23)]

Weekday = Literal[
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

Monthday = (
    Annotated[int, Field(..., ge=-31, le=-1)] | Annotated[int, Field(..., ge=1, le=31)]
)

Yearday = (
    Annotated[int, Field(..., ge=-366, le=-1)]
    | Annotated[int, Field(..., ge=1, le=366)]
)

Week = (
    Annotated[int, Field(..., ge=-53, le=-1)] | Annotated[int, Field(..., ge=1, le=53)]
)

Month = Annotated[int, Field(..., ge=1, le=12)]


class WeekdayRule(SerializableModel):
    """Day rule model."""

    day: Weekday = Field(
        ...,
        title="DayRule.Day",
        description="Day of the week.",
    )
    occurrence: Week | None = Field(
        None,
        title="DayRule.Occurrence",
        description="Occurrence of the day in the year.",
    )


class RecurrenceRule(SerializableModel):
    """Recurrence rule model."""

    frequency: Frequency = Field(
        ...,
        title="RecurrenceRule.Frequency",
        description="Frequency of the recurrence.",
    )
    until: NaiveDatetime | None = Field(
        None,
        title="RecurrenceRule.Until",
        description="End date of the recurrence in UTC.",
    )
    count: int | None = Field(
        None,
        title="RecurrenceRule.Count",
        description="Number of occurrences of the recurrence.",
    )
    interval: int | None = Field(
        None,
        title="RecurrenceRule.Interval",
        description="Interval of the recurrence.",
    )
    by_seconds: list[Second] | None = Field(
        None,
        title="RecurrenceRule.BySeconds",
        description="Seconds of the recurrence.",
    )
    by_minutes: list[Minute] | None = Field(
        None,
        title="RecurrenceRule.ByMinutes",
        description="Minutes of the recurrence.",
    )
    by_hours: list[Hour] | None = Field(
        None,
        title="RecurrenceRule.ByHours",
        description="Hours of the recurrence.",
    )
    by_weekdays: list[WeekdayRule] | None = Field(
        None,
        title="RecurrenceRule.ByWeekdays",
        description="Weekdays of the recurrence.",
    )
    by_monthdays: list[Monthday] | None = Field(
        None,
        title="RecurrenceRule.ByMonthdays",
        description="Monthdays of the recurrence.",
    )
    by_yeardays: list[Yearday] | None = Field(
        None,
        title="RecurrenceRule.ByYeardays",
        description="Yeardays of the recurrence.",
    )
    by_weeks: list[Week] | None = Field(
        None,
        title="RecurrenceRule.ByWeeks",
        description="Weeks of the recurrence.",
    )
    by_months: list[Month] | None = Field(
        None,
        title="RecurrenceRule.ByMonths",
        description="Months of the recurrence.",
    )
    by_set_positions: list[int] | None = Field(
        None,
        title="RecurrenceRule.BySetPositions",
        description="Set positions of the recurrence.",
    )
    week_start: Weekday | None = Field(
        None,
        title="RecurrenceRule.WeekStart",
        description="Start day of the week.",
    )


class Recurrence(SerializableModel):
    """Recurrence model."""

    rule: RecurrenceRule | None = Field(
        None,
        title="Recurrence.Rule",
        description="Rule of the recurrence.",
    )
    include: list[NaiveDatetime] | None = Field(
        None,
        title="Recurrence.Include",
        description="Included dates of the recurrence in event timezone.",
    )
    exclude: list[NaiveDatetime] | None = Field(
        None,
        title="Recurrence.Exclude",
        description="Excluded dates of the recurrence in event timezone.",
    )


class Event(SerializableModel):
    """Event model."""

    id: UUID = Field(
        ...,
        title="Event.Id",
        description="Identifier of the event.",
    )
    type: EventType = Field(
        ...,
        title="Event.Type",
        description="Type of the event.",
    )
    show_id: UUID = Field(
        ...,
        title="Event.ShowId",
        description="Identifier of the show the event belongs to.",
    )
    show: Show | None = Field(
        None,
        title="Event.Show",
        description="Show the event belongs to.",
    )
    start: NaiveDatetime = Field(
        ...,
        title="Event.Start",
        description="Start time of the event in event timezone.",
    )
    end: NaiveDatetime = Field(
        ...,
        title="Event.End",
        description="End time of the event in event timezone.",
    )
    timezone: Timezone = Field(
        ...,
        title="Event.Timezone",
        description="Timezone of the event.",
    )
    recurrence: Recurrence | None = Field(
        None,
        title="Event.Recurrence",
        description="Recurrence of the event.",
    )


class EventInstance(SerializableModel):
    """Event instance."""

    start: NaiveDatetime = Field(
        ...,
        title="EventInstance.Start",
        description="Start time of the event instance in event timezone.",
    )
    end: NaiveDatetime = Field(
        ...,
        title="EventInstance.End",
        description="End time of the event instance in event timezone.",
    )


class EventSchedule(SerializableModel):
    """Event schedule."""

    event: Event = Field(
        ...,
        title="EventSchedule.Event",
        description="Event.",
    )
    instances: list[EventInstance] = Field(
        ...,
        title="EventSchedule.Instances",
        description="Event instances.",
    )


EventsGetByIdIdParameter = UUID

EventsGetByIdIncludeParameter = EventInclude | None

EventsListLimitParameter = int | None

EventsListOffsetParameter = int | None

EventsListWhereParameter = EventWhereInput | None

EventsListIncludeParameter = EventInclude | None

EventsListOrderParameter = EventOrderByInput | list[EventOrderByInput] | None


class EventsListResponse(SerializableModel):
    """Response from GET /events."""

    count: int = Field(
        ...,
        title="EventsListResponse.Count",
        description="Number of events that matched the request.",
    )
    limit: int | None = Field(
        ...,
        title="EventsListResponse.Limit",
        description="Maximum number of returned events.",
    )
    offset: int | None = Field(
        ...,
        title="EventsListResponse.Offset",
        description="Number of events skipped.",
    )
    events: list[Event] = Field(
        ...,
        title="EventsListResponse.Events",
        description="Events that matched the request.",
    )


ScheduleListStartParameter = NaiveDatetime | None

ScheduleListEndParameter = NaiveDatetime | None

ScheduleListLimitParameter = int | None

ScheduleListOffsetParameter = int | None

ScheduleListWhereParameter = EventWhereInput | None

ScheduleListIncludeParameter = EventInclude | None

ScheduleListOrderParameter = EventOrderByInput | list[EventOrderByInput] | None


class ScheduleListResponse(SerializableModel):
    """Response from GET /schedule."""

    count: int = Field(
        ...,
        title="ScheduleListResponse.Count",
        description="Number of event schedules that matched the request.",
    )
    limit: int | None = Field(
        ...,
        title="ScheduleListResponse.Limit",
        description="Maximum number of returned event schedules.",
    )
    offset: int | None = Field(
        ...,
        title="ScheduleListResponse.Offset",
        description="Number of event schedules skipped.",
    )
    schedules: list[EventSchedule] = Field(
        ...,
        title="ScheduleListResponse.Schedules",
        description="Event schedules that matched the request.",
    )
