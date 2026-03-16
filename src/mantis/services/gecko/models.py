from collections.abc import AsyncIterator, Sequence
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime


class Recording(SerializableModel):
    """Recording data."""

    event: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""


class RecordingList(SerializableModel):
    """List of recordings."""

    count: int
    """Total number of recordings that match the request."""

    recordings: Sequence[Recording]
    """List of recordings."""


type RecordingsListRequestEvent = UUID

type RecordingsListRequestAfter = NaiveDatetime | None

type RecordingsListRequestBefore = NaiveDatetime | None

type RecordingsListRequestLimit = int | None

type RecordingsListRequestOffset = int | None

type RecordingsListResponseResults = RecordingList

type RecordingsDownloadRequestEvent = UUID

type RecordingsDownloadRequestStart = NaiveDatetime

type RecordingsDownloadResponseType = str

type RecordingsDownloadResponseData = AsyncIterator[bytes]


@datamodel
class RecordingsListRequest:
    """Request to list recordings."""

    event: RecordingsListRequestEvent
    """Identifier of the event to list recordings for."""

    after: RecordingsListRequestAfter
    """Only list recordings after this datetime (in event timezone)."""

    before: RecordingsListRequestBefore
    """Only list recordings before this datetime (in event timezone)."""

    limit: RecordingsListRequestLimit
    """Maximum number of recordings to return."""

    offset: RecordingsListRequestOffset
    """Number of recordings to skip."""


@datamodel
class RecordingsListResponse:
    """Response for listing recordings."""

    results: RecordingsListResponseResults
    """List of recordings."""


@datamodel
class RecordingsDownloadRequest:
    """Request to download a recording."""

    event: RecordingsDownloadRequestEvent
    """Identifier of the event."""

    start: RecordingsDownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class RecordingsDownloadResponse:
    """Response for downloading a recording."""

    type: RecordingsDownloadResponseType
    """Type of the recording data."""

    data: RecordingsDownloadResponseData
    """Data of the recording."""
