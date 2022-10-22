from emischeduler.models.base import SerializableModel
from emischeduler.stream.models.data import Event, Token, Availability


class ReserveRequest(SerializableModel):
    event: Event
    record: bool = False


class ReserveResponse(SerializableModel):
    token: Token


class AvailableResponse(SerializableModel):
    availability: Availability


class AvailableStreamResponse(SerializableModel):
    availability: Availability
