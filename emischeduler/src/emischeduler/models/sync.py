from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel


class Event(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime
    type: Literal["live", "replay"]


class Timetable(BaseModel):
    events: List[Event]
