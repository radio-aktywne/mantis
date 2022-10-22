from datetime import datetime
from typing import Optional, Dict, Any, Literal
from uuid import UUID

from pydantic import validator

from emischeduler.models.base import SerializableModel
from emischeduler.time import parse_datetime_with_timezone


class Show(SerializableModel):
    id: int
    label: str
    title: str
    description: Optional[str]


class EventParams(SerializableModel):
    start: datetime
    end: datetime
    rules: Optional[Dict[str, Any]] = None

    @validator("start", "end", pre=True)
    def parse_dates(cls, value):
        return parse_datetime_with_timezone(value)


class Event(SerializableModel):
    id: UUID
    show: Show
    type: Literal[1, 2]
    params: EventParams
