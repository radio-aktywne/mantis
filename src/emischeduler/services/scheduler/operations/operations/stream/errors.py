from datetime import datetime
from uuid import UUID

from emischeduler.services.emishows import models as eshm


class EventNotFoundError(Exception):
    """Raised when an event cannot be found."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"No event found for id {id}.")


class ScheduleNotFoundError(Exception):
    """Raised when a schedule cannot be found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No schedule found for event {event}.")


class InstanceNotFoundError(Exception):
    """Raised when an instance cannot be found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"No instance found for event {event} and start {start.isoformat()}."
        )


class InstanceAlreadyEndedError(Exception):
    """Raised when an instance has already ended."""

    def __init__(self, event: UUID, start: datetime, end: datetime) -> None:
        super().__init__(
            f"Instance for event {event} and start {start.isoformat()} has already ended at {end.isoformat()}."
        )


class UnexpectedEventTypeError(Exception):
    """Raised when an unexpected event type is encountered."""

    def __init__(self, event: UUID, type: eshm.EventType) -> None:
        super().__init__(f"Event {event} has unexpected type {type}.")


class DownloadUnavailableError(Exception):
    """Raised when a download is unavailable."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(f"No download available for event {event} and start {start}.")


class UnexpectedFormatError(Exception):
    """Raised when an unexpected format is encountered."""

    def __init__(self, format: str) -> None:
        super().__init__(f"Unexpected format {format}.")
