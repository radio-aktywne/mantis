from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    id: str
    title: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class Reservation(BaseModel):
    event: Event
    record: bool = False


class Token(BaseModel):
    token: str
    expires_at: datetime


class ReserveRequest(BaseModel):
    reservation: Reservation


class ReserveResponse(BaseModel):
    token: Token


class Availability(BaseModel):
    available: bool
    reservation: Optional[Reservation] = None


class AvailableResponse(BaseModel):
    availability: Availability


class AvailableNotification(BaseModel):
    availability: Availability
