from datetime import datetime
from uuid import UUID

from mantis.services.apis.beaver import models as bm
from mantis.utils.mime import MimeType
from mantis.utils.time import isostringify


class OperationError(Exception):
    """Base class for stream operation errors."""


class InstanceNotFoundError(OperationError):
    """Raised when an instance cannot be found."""

    def __init__(self, event_id: UUID, start: datetime) -> None:
        super().__init__(
            f"No instance found for event {event_id} and start {isostringify(start)}."
        )


class InstanceAlreadyEndedError(OperationError):
    """Raised when an instance has already ended."""

    def __init__(self, instance: bm.InstanceWithEvent) -> None:
        super().__init__(
            f"Instance for event {instance.event.id} "
            f"and start {isostringify(instance.start)} has already ended "
            f"at {isostringify(instance.start + instance.duration)}."
        )


class UnexpectedEventTypeError(OperationError):
    """Raised when an unexpected event type is encountered."""

    def __init__(self, event: bm.Event) -> None:
        super().__init__(f"Event {event.id} has unexpected type {event.type}.")


class DownloadUnavailableError(OperationError):
    """Raised when a download is unavailable."""

    def __init__(self, instance: bm.InstanceWithEvent) -> None:
        super().__init__(
            f"No download available for instance for event {instance.event.id} "
            f"and start {isostringify(instance.start)}."
        )


class UnexpectedFormatError(OperationError):
    """Raised when an unexpected format is encountered."""

    def __init__(self, fmt: MimeType) -> None:
        super().__init__(f"Unexpected format {fmt!s}.")


class ReservationFailedError(OperationError):
    """Raised when a stream reservation fails."""

    def __init__(self, instance: bm.InstanceWithEvent) -> None:
        super().__init__(
            f"Failed to reserve stream for instance for event {instance.event.id} "
            f"and start {isostringify(instance.start)}."
        )
