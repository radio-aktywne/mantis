from collections.abc import AsyncIterator, Sequence
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime


class Prerecording(SerializableModel):
    """Prerecording data."""

    event: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""


class PrerecordingList(SerializableModel):
    """List of prerecordings."""

    count: int
    """Total number of prerecordings that match the request."""

    prerecordings: Sequence[Prerecording]
    """List of prerecordings."""


type PrerecordingsListRequestEvent = UUID

type PrerecordingsListRequestAfter = NaiveDatetime | None

type PrerecordingsListRequestBefore = NaiveDatetime | None

type PrerecordingsListRequestLimit = int | None

type PrerecordingsListRequestOffset = int | None

type PrerecordingsListResponseResults = PrerecordingList

type PrerecordingsDownloadRequestEvent = UUID

type PrerecordingsDownloadRequestStart = NaiveDatetime

type PrerecordingsDownloadResponseType = str

type PrerecordingsDownloadResponseData = AsyncIterator[bytes]


@datamodel
class PrerecordingsListRequest:
    """Request to list prerecordings."""

    event: PrerecordingsListRequestEvent
    """Identifier of the event to list prerecordings for."""

    after: PrerecordingsListRequestAfter
    """Only list prerecordings after this datetime (in event timezone)."""

    before: PrerecordingsListRequestBefore
    """Only list prerecordings before this datetime (in event timezone)."""

    limit: PrerecordingsListRequestLimit
    """Maximum number of prerecordings to return."""

    offset: PrerecordingsListRequestOffset
    """Number of prerecordings to skip."""


@datamodel
class PrerecordingsListResponse:
    """Response for listing prerecordings."""

    results: PrerecordingsListResponseResults
    """List of prerecordings."""


@datamodel
class PrerecordingsDownloadRequest:
    """Request to download a prerecording."""

    event: PrerecordingsDownloadRequestEvent
    """Identifier of the event."""

    start: PrerecordingsDownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class PrerecordingsDownloadResponse:
    """Response for downloading a prerecording."""

    type: PrerecordingsDownloadResponseType
    """Type of the prerecording data."""

    data: PrerecordingsDownloadResponseData
    """Data of the prerecording."""
