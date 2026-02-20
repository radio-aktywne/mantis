from collections.abc import AsyncIterator
from collections.abc import Set as AbstractSet
from enum import StrEnum
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


class EventType(StrEnum):
    """Event types."""

    AVAILABILITY_CHANGED = "availability-changed"


class Credentials(SerializableModel):
    """Credentials for accessing the stream."""

    token: str
    """Token to use to connect to the stream."""


class ReservationInput(SerializableModel):
    """Data for reserving a stream."""

    event: UUID
    """Identifier of the event to reserve the stream for."""

    format: Format = Format.OGG
    """Format of the audio in the stream."""

    record: bool = False
    """Whether to record the stream."""


class Reservation(SerializableModel):
    """Reservation of a stream."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""


@datamodel
class EventMessage:
    """Event message data."""


type ReserveRequestData = ReservationInput

type ReserveResponseReservation = Reservation

type SubscribeRequestTypes = AbstractSet[EventType] | None

type SubscribeResponseMessages = AsyncIterator[EventMessage]


@datamodel
class ReserveRequest:
    """Request to reserve a stream."""

    data: ReserveRequestData
    """Data for reserving a stream."""


@datamodel
class ReserveResponse:
    """Response for reserving a stream."""

    reservation: ReserveResponseReservation
    """Reservation of the stream."""


@datamodel
class SubscribeRequest:
    """Request to subscribe."""

    types: SubscribeRequestTypes
    """Types of events to subscribe to."""


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    messages: SubscribeResponseMessages
    """Stream of event messages."""
