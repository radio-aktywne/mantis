from collections.abc import AsyncIterator
from enum import StrEnum
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


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


type ReserveRequestData = ReservationInput

type ReserveResponseReservation = Reservation


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


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    messages: AsyncIterator[str]
    """Stream of messages."""
