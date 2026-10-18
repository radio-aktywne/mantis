from collections.abc import Sequence
from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime, Timedelta, Timezone, UTCDatetime


class EventType(StrEnum):
    """Event type options."""

    live = "live"
    replay = "replay"
    prerecorded = "prerecorded"


class Event(SerializableModel):
    """Event data."""

    id: UUID
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: UUID | None
    """Identifier of the show the event belongs to."""

    timezone: Timezone
    """Timezone of the event."""


class Instance(SerializableModel):
    """Instance data."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""

    duration: Timedelta
    """Duration of the instance."""

    event_id: UUID
    """Identifier of the event the instance belongs to."""


class InstanceWithEvent(Instance):
    """Instance data with event relation included."""

    event: Event
    """Event the instance belongs to."""


class InstanceList(SerializableModel):
    """List of instances."""

    instances: Sequence[InstanceWithEvent | Instance]
    """Instances that matched the request."""


class EventWhereInput(TypedDict, total=False):
    """Event arguments for searching."""

    id: UUID
    """Identifier of the event."""

    type: EventType
    """Type of the event."""

    show_id: UUID | None
    """Identifier of the show the event belongs to."""

    OR: list[EventWhereInput]
    """List of event arguments for searching evaluated as alternatives."""


EventRelationFilter = TypedDict(
    "EventRelationFilter",
    {
        "is": EventWhereInput,
        "is_not": EventWhereInput,
    },
    total=False,
)


class InstanceWhereInput(TypedDict, total=False):
    """Instance arguments for searching."""

    event: EventRelationFilter
    """Event relation filter."""


class InstanceInclude(TypedDict, total=False):
    """Relations to include when querying instances."""

    event: bool
    """Event relation to include."""


type InstancesListRequestStart = UTCDatetime

type InstancesListRequestEnd = UTCDatetime

type InstancesListRequestWhere = InstanceWhereInput | None

type InstancesListRequestInclude = InstanceInclude | None

type InstancesListResponseResults = InstanceList

type InstancesGetRequestEventId = UUID

type InstancesGetRequestStart = NaiveDatetime

type InstancesGetRequestInclude = InstanceInclude | None

type InstancesGetResponseInstance = InstanceWithEvent | Instance


@datamodel
class InstancesListRequest:
    """Request to list instances."""

    start: InstancesListRequestStart
    """Start datetime in UTC to filter events instances."""

    end: InstancesListRequestEnd
    """End datetime in UTC to filter events instances."""

    where: InstancesListRequestWhere
    """Filter to apply to find events."""

    include: InstancesListRequestInclude
    """Relations to include in the response."""


@datamodel
class InstancesListResponse:
    """Response for listing instances."""

    results: InstancesListResponseResults
    """List of instances."""


@datamodel
class InstancesGetRequest:
    """Request to get an instance."""

    event_id: InstancesGetRequestEventId
    """Identifier of the event the instance to get belongs to."""

    start: InstancesGetRequestStart
    """Start datetime of the instance to get in event timezone."""

    include: InstancesGetRequestInclude
    """Relations to include in the response."""


@datamodel
class InstancesGetResponse:
    """Response for getting an instance."""

    instance: InstancesGetResponseInstance
    """Instance that matched the request."""
