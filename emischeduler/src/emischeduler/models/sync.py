from datetime import datetime
from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, validator

from emischeduler.utils import parse_datetime_with_timezone


class Show(BaseModel):
    id: int
    label: str
    title: str
    description: Optional[str]


class EventParams(BaseModel):
    start: datetime
    end: datetime
    rules: Optional[Dict[str, Any]] = None

    @validator("start", "end", pre=True)
    def parse_dates(cls, value):
        return parse_datetime_with_timezone(value)


class Event(BaseModel):
    id: UUID
    show: Show
    type: Literal[1, 2]
    params: EventParams
