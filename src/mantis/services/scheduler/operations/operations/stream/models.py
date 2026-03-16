from datetime import datetime
from pathlib import Path
from uuid import UUID

from mantis.models.base import SerializableModel, dataclass
from mantis.services.beaver import models as bm
from mantis.services.octopus import models as om
from mantis.utils.time import NaiveDatetime


class Parameters(SerializableModel):
    """Parameters for the stream operation."""

    id: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""


@dataclass
class FindRequest:
    """Request to find an event instance."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start datetime of the event instance in event timezone."""


@dataclass
class FindResponse:
    """Results of the find operation."""

    event: bm.Event
    """Event that was found."""

    instance: bm.EventInstance
    """Instance of the event that was found."""


@dataclass
class DownloadRequest:
    """Request to download media for an event instance."""

    event: bm.Event
    """Event to download the media for."""

    instance: bm.EventInstance
    """Instance of the event to download the media for."""

    directory: Path
    """Directory to download the media to."""


@dataclass
class DownloadResponse:
    """Results of the download operation."""

    path: Path
    """Path to the downloaded media."""

    format: om.Format
    """Audio format of the downloaded media."""


@dataclass
class ReserveRequest:
    """Request to reserve a stream."""

    event: UUID
    """Identifier of the event."""

    format: om.Format
    """Audio format to stream."""


@dataclass
class ReserveResponse:
    """Results of the reserve operation."""

    credentials: om.Credentials
    """Credentials to access the stream."""
