from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, RootModel

from mantis.models.base import SerializableModel, datamodel
from mantis.services.octopus import types as t
from mantis.utils.time import NaiveDatetime, naiveutcnow


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


class Availability(SerializableModel):
    """Availability of a stream."""

    event: UUID | None
    """Identifier of the event that is currently being streamed."""

    checked_at: NaiveDatetime
    """Time in UTC at which the availability was checked."""


class Credentials(SerializableModel):
    """Credentials for accessing the stream."""

    token: str
    """Token to use to connect to the stream."""

    expires_at: NaiveDatetime
    """Time in UTC at which the token expires if not used."""


class ReserveRequestData(SerializableModel):
    """Data for a reserve request."""

    event: UUID
    """Identifier of the event to reserve the stream for."""

    format: Format = Format.OGG
    """Format of the audio in the stream."""

    record: bool = False
    """Whether to record the stream."""


class ReserveResponseData(SerializableModel):
    """Data for a reserve response."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""

    port: Annotated[int, Field(ge=1, le=65535)]
    """Port to use to connect to the stream."""


class FooEventData(SerializableModel):
    """Data of a foo event."""

    foo: str
    """Foo field."""


class FooEvent(SerializableModel):
    """Foo event."""

    type: t.TypeField[Literal["foo"]] = "foo"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[FooEventData]


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability
    """New availability."""


class AvailabilityChangedEvent(SerializableModel):
    """Event emitted when the availability of a stream changes."""

    type: t.TypeField[Literal["availability-changed"]] = "availability-changed"
    created_at: t.CreatedAtField = Field(default_factory=naiveutcnow)
    data: t.DataField[AvailabilityChangedEventData]


Event = Annotated[FooEvent | AvailabilityChangedEvent, Field(..., discriminator="type")]
ParsableEvent = RootModel[Event]


@datamodel
class CheckRequest:
    """Request to check the availability of a stream."""


@datamodel
class CheckResponse:
    """Response for checking the availability of a stream."""

    availability: Availability
    """Availability of the stream."""


@datamodel
class ReserveRequest:
    """Request to reserve a stream."""

    data: ReserveRequestData
    """Data for the request."""


@datamodel
class ReserveResponse:
    """Response for reserving a stream."""

    data: ReserveResponseData
    """Data for the response."""


@datamodel
class SubscribeRequest:
    """Request to subscribe to events."""


@datamodel
class SubscribeResponse:
    """Response for subscribing to events."""

    events: AsyncIterator[Event]
    """Asynchronous iterator of events."""
