from emischeduler.models.base import SerializableModel


class StatusResponse(SerializableModel):
    alive: bool


class StatusStreamResponse(SerializableModel):
    alive: bool
