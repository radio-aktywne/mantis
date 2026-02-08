from collections.abc import Sequence
from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime, Timezone


class EventType(StrEnum):
    """Event type options."""

    live = "live"
    replay = "replay"
    prerecorded = "prerecorded"


StringFilter = TypedDict(
    "StringFilter",
    {
        "in": Sequence[str],
    },
    total=False,
)


class Event(SerializableModel):
    """Event data."""

    id: UUID
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: UUID
    """Identifier of the show that the event belongs to."""

    timezone: Timezone
    """Timezone of the event."""


class EventList(SerializableModel):
    """List of events."""

    count: int
    """Total number of events that matched the query."""

    events: Sequence[Event]
    """Events that matched the request."""


class EventInstance(SerializableModel):
    """Event instance data."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""

    end: NaiveDatetime
    """End datetime of the event instance in event timezone."""


class Schedule(SerializableModel):
    """Schedule data."""

    event: Event
    """Event data."""

    instances: Sequence[EventInstance]
    """Event instances."""


class ScheduleList(SerializableModel):
    """List of event schedules."""

    count: int
    """Total number of schedules that matched the query."""

    schedules: Sequence[Schedule]
    """Schedules that matched the request."""


class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: str | StringFilter
    type: EventType
    show_id: str

    OR: Sequence["EventWhereInput"]


type EventsListRequestLimit = int | None

type EventsListRequestOffset = int | None

type EventsListRequestWhere = EventWhereInput | None

type EventsListResponseResults = EventList

type EventsGetRequestId = UUID

type EventsGetResponseEvent = Event

type ScheduleListRequestStart = NaiveDatetime | None

type ScheduleListRequestEnd = NaiveDatetime | None

type ScheduleListRequestLimit = int | None

type ScheduleListRequestOffset = int | None

type ScheduleListRequestWhere = EventWhereInput | None

type ScheduleListResponseResults = ScheduleList


@datamodel
class EventsListRequest:
    """Request to list events."""

    limit: EventsListRequestLimit
    """Maximum number of events to return."""

    offset: EventsListRequestOffset
    """Number of events to skip."""

    where: EventsListRequestWhere
    """Filter to apply to find events."""


@datamodel
class EventsListResponse:
    """Response for listing events."""

    results: EventsListResponseResults
    """List of events."""


@datamodel
class EventsGetRequest:
    """Request to get an event."""

    id: EventsGetRequestId
    """Identifier of the event to get."""


@datamodel
class EventsGetResponse:
    """Response for getting an event."""

    event: EventsGetResponseEvent
    """Event that matched the request."""


@datamodel
class ScheduleListRequest:
    """Request to list schedules."""

    start: ScheduleListRequestStart
    """Start datetime in UTC to filter events instances."""

    end: ScheduleListRequestEnd
    """End datetime in UTC to filter events instances."""

    limit: ScheduleListRequestLimit
    """Maximum number of schedules to return."""

    offset: ScheduleListRequestOffset
    """Number of schedules to skip."""

    where: ScheduleListRequestWhere
    """Filter to apply to find events."""


@datamodel
class ScheduleListResponse:
    """Response for listing schedules."""

    results: ScheduleListResponseResults
    """List of schedules."""
