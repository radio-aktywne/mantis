from datetime import datetime
from typing import Annotated, Literal, TypeVar
from uuid import UUID

from pydantic import Field, NaiveDatetime, RootModel

from emischeduler.models.base import SerializableModel

Format = Literal["ogg"]


class Availability(SerializableModel):
    """Availability information."""

    event: UUID | None = Field(
        ...,
        title="Availability.Event",
        description="Identifier of the event that is currently on air.",
    )
    checked_at: NaiveDatetime = Field(
        ...,
        title="Availability.CheckedAt",
        description="Time in UTC at which the availability was checked.",
    )


class ReserveRequest(SerializableModel):
    """Request for reserving a stream."""

    event: UUID = Field(
        ...,
        title="ReserveRequest.Event",
        description="Identifier of the event to reserve the stream for.",
    )
    format: Format = Field(
        "ogg",
        title="ReserveRequest.Format",
        description="Format of the audio stream.",
    )
    record: bool = Field(
        False,
        title="ReserveRequest.Record",
        description="Whether to record the stream.",
    )


class Credentials(SerializableModel):
    """Credentials for accessing the stream."""

    token: str = Field(
        ...,
        title="Credentials.Token",
        description="Token to use to connect to the stream.",
    )
    expires_at: NaiveDatetime = Field(
        ...,
        title="Credentials.ExpiresAt",
        description="Time in UTC at which the token expires if not used.",
    )


class ReserveResponse(SerializableModel):
    """Response to a stream reservation request."""

    credentials: Credentials = Field(
        ...,
        title="ReserveResponse.Credentials",
        description="Credentials to use to connect to the stream.",
    )
    port: int = Field(
        ...,
        title="ReserveResponse.Port",
        description="Port to use to connect to the stream.",
    )


TypeType = TypeVar("TypeType")
DataType = TypeVar("DataType", bound=SerializableModel)

TypeFieldType = Annotated[
    TypeType,
    Field(description="Type of the event."),
]
CreatedAtFieldType = Annotated[
    datetime,
    Field(description="Time at which the event was created."),
]
DataFieldType = Annotated[
    DataType,
    Field(description="Data of the event."),
]


class DummyEventData(SerializableModel):
    """Data of a dummy event."""

    pass


class DummyEvent(SerializableModel):
    """Dummy event that exists only so that there can be two types in discriminated union."""

    type: TypeFieldType[Literal["dummy"]] = Field(
        "dummy",
        title="DummyEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="DummyEvent.CreatedAt",
    )
    data: DataFieldType[DummyEventData] = Field(
        DummyEventData(),
        title="DummyEvent.Data",
    )


class AvailabilityChangedEventData(SerializableModel):
    """Data of an availability-changed event."""

    availability: Availability = Field(
        ...,
        title="AvailabilityChangedEventData.Availability",
        description="New availability.",
    )


class AvailabilityChangedEvent(SerializableModel):
    """Event that indicates a change in availability."""

    type: TypeFieldType[Literal["availability-changed"]] = Field(
        "availability-changed",
        title="AvailabilityChangedEvent.Type",
    )
    created_at: CreatedAtFieldType = Field(
        ...,
        title="AvailabilityChangedEvent.CreatedAt",
    )
    data: DataFieldType[AvailabilityChangedEventData] = Field(
        ...,
        title="AvailabilityChangedEvent.Data",
    )


Event = Annotated[
    DummyEvent | AvailabilityChangedEvent, Field(..., discriminator="type")
]
ParsableEvent = RootModel[Event]
