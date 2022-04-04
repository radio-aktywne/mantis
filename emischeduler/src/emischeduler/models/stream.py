from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class Show(BaseModel):
    label: str
    metadata: Dict[str, str] = {}


class Event(BaseModel):
    show: Show
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    metadata: Dict[str, str] = {}


class Token(BaseModel):
    token: str
    expires_at: datetime


class ReserveRequest(BaseModel):
    event: Event
    record: bool = False


class ReserveResponse(BaseModel):
    token: Token


class Availability(BaseModel):
    available: bool
    event: Optional[Event] = None


class AvailableResponse(BaseModel):
    availability: Availability


class AvailableNotification(BaseModel):
    availability: Availability
