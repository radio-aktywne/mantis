from datetime import datetime
from pathlib import Path
from uuid import UUID

from emischeduler.models.base import SerializableModel, dataclass
from emischeduler.services.emishows import models as eshm
from emischeduler.services.emistream import models as estm
from emischeduler.utils.time import NaiveDatetime


class Parameters(SerializableModel):
    """Parameters for the stream operation."""

    id: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start time of the event instance in event timezone."""


@dataclass
class FindRequest:
    """Request to find an event instance."""

    event: UUID
    """Identifier of the event."""

    start: datetime
    """Start time of the event instance in event timezone."""


@dataclass
class FindResponse:
    """Results of the find operation."""

    event: eshm.Event
    """Event that was found."""

    instance: eshm.EventInstance
    """Instance of the event that was found."""


@dataclass
class DownloadRequest:
    """Request to download a replay record."""

    event: eshm.Event
    """Event to download the replay record for."""

    instance: eshm.EventInstance
    """Instance of the event to download the replay record for."""

    directory: Path
    """Directory to download the replay record to."""


@dataclass
class DownloadResponse:
    """Results of the download operation."""

    path: Path
    """Path to the downloaded replay record."""

    format: estm.Format
    """Audio format of the downloaded replay record."""


@dataclass
class ReserveRequest:
    """Request to reserve a stream."""

    event: UUID
    """Identifier of the event."""

    format: estm.Format
    """Audio format to stream."""


@dataclass
class ReserveResponse:
    """Results of the reserve operation."""

    credentials: estm.Credentials
    """Credentials to access the stream."""
