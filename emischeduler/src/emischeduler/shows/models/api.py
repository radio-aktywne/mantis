from typing import List

from emischeduler.models.base import SerializableModel
from emischeduler.shows.models.data import Event


class TimetableResponse(SerializableModel):
    __root__: List[Event]
