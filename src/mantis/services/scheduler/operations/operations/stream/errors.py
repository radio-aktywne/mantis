from datetime import datetime
from uuid import UUID

from mantis.services.beaver import models as bm
from mantis.utils.time import isostringify


class EventNotFoundError(Exception):
    """Raised when an event cannot be found."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"No event found for id {event_id}.")


class ScheduleNotFoundError(Exception):
    """Raised when a schedule cannot be found."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"No schedule found for event {event_id}.")


class InstanceNotFoundError(Exception):
    """Raised when an instance cannot be found."""

    def __init__(self, event_id: UUID, start: datetime) -> None:
        super().__init__(
            f"No instance found for event {event_id} and start {isostringify(start)}."
        )


class InstanceAlreadyEndedError(Exception):
    """Raised when an instance has already ended."""

    def __init__(self, event_id: UUID, start: datetime, end: datetime) -> None:
        super().__init__(
            f"Instance for event {event_id} and start {isostringify(start)} has already ended at {isostringify(end)}."
        )


class UnexpectedEventTypeError(Exception):
    """Raised when an unexpected event type is encountered."""

    def __init__(self, event_id: UUID, event_type: bm.EventType) -> None:
        super().__init__(f"Event {event_id} has unexpected type {event_type}.")


class DownloadUnavailableError(Exception):
    """Raised when a download is unavailable."""

    def __init__(self, event_id: UUID, start: datetime) -> None:
        super().__init__(
            f"No download available for event {event_id} and start {isostringify(start)}."
        )


class UnexpectedFormatError(Exception):
    """Raised when an unexpected format is encountered."""

    def __init__(self, fmt: str) -> None:
        super().__init__(f"Unexpected format {fmt}.")


class ReservationFailedError(Exception):
    """Raised when a stream reservation fails."""

    def __init__(self, event_id: UUID) -> None:
        super().__init__(f"Failed to reserve stream for event {event_id}.")
