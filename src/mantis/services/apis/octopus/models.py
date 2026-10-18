from collections.abc import AsyncGenerator, Set as AbstractSet
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import PlainSerializer

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


class EventType(StrEnum):
    """Event types."""

    AVAILABILITY_CHANGED = "availability-changed"


class Instance(SerializableModel):
    """Instance data."""

    event: UUID
    """Identifier of the event the instance belongs to."""

    start: NaiveDatetime
    """Start datetime of the instance in event timezone."""


class ReservationInput(SerializableModel):
    """Data for reserving a stream."""

    instance: Instance
    """Instance to reserve the stream for."""

    format: Format = Format.OGG
    """Format of the audio in the stream."""


class Credentials(SerializableModel):
    """Credentials for accessing the stream."""

    token: str
    """Token to use to connect to the stream."""


class Reservation(SerializableModel):
    """Reservation of a stream."""

    credentials: Credentials
    """Credentials to use to connect to the stream."""


@datamodel
class EventMessage:
    """Event message data."""


type ReserveRequestData = ReservationInput

type ReserveResponseReservation = Reservation

type SubscribeRequestTypes = Annotated[
    AbstractSet[EventType] | None,
    PlainSerializer(
        lambda value: ",".join(value) if value is not None else None,
        return_type=str | None,
    ),
]

type SubscribeResponseMessages = AsyncGenerator[EventMessage]


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
