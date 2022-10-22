from datetime import datetime
from typing import Dict, Optional, Literal

from emischeduler.models.base import SerializableModel


class Show(SerializableModel):
    label: str
    metadata: Dict[str, str] = {}


class Event(SerializableModel):
    show: Show
    type: Literal[1, 2]
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    metadata: Dict[str, str] = {}


class Token(SerializableModel):
    token: str
    expires_at: datetime


class Availability(SerializableModel):
    available: bool
    event: Optional[Event] = None
