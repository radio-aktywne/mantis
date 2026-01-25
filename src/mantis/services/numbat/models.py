from collections.abc import AsyncIterator, Sequence
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime


class ListOrder(StrEnum):
    """Order to list prerecordings."""

    ASCENDING = "asc"
    DESCENDING = "desc"


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

    limit: int | None
    """Maximum number of returned prerecordings."""

    offset: int | None
    """Number of skipped prerecordings."""

    prerecordings: Sequence[Prerecording]
    """List of prerecordings."""


ListRequestEvent = UUID

ListRequestAfter = NaiveDatetime | None

ListRequestBefore = NaiveDatetime | None

ListRequestLimit = int | None

ListRequestOffset = int | None

ListRequestOrder = ListOrder | None

ListResponseResults = PrerecordingList

DownloadRequestEvent = UUID

DownloadRequestStart = NaiveDatetime

DownloadResponseType = str

DownloadResponseSize = int

DownloadResponseTag = str

DownloadResponseModified = datetime

DownloadResponseData = AsyncIterator[bytes]


@datamodel
class ListRequest:
    """Request to list prerecordings."""

    event: ListRequestEvent
    """Identifier of the event to list prerecordings for."""

    after: ListRequestAfter
    """Only list prerecordings after this datetime (in event timezone)."""

    before: ListRequestBefore
    """Only list prerecordings before this datetime (in event timezone)."""

    limit: ListRequestLimit
    """Maximum number of prerecordings to return."""

    offset: ListRequestOffset
    """Number of prerecordings to skip."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing prerecordings."""

    results: ListResponseResults
    """List of prerecordings."""


@datamodel
class DownloadRequest:
    """Request to download a prerecording."""

    event: DownloadRequestEvent
    """Identifier of the event."""

    start: DownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a prerecording."""

    type: DownloadResponseType
    """Type of the prerecording data."""

    size: DownloadResponseSize
    """Size of the prerecording in bytes."""

    tag: DownloadResponseTag
    """ETag of the prerecording data."""

    modified: DownloadResponseModified
    """Datetime when the prerecording was last modified."""

    data: DownloadResponseData
    """Data of the prerecording."""
