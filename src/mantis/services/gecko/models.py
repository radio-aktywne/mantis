from collections.abc import AsyncIterator, Sequence
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime


class ListOrder(StrEnum):
    """Order to list records."""

    ASCENDING = "asc"
    DESCENDING = "desc"


class Record(SerializableModel):
    """Record data."""

    event: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start datetime of the event instance in event timezone."""


class RecordList(SerializableModel):
    """List of records."""

    count: int
    """Total number of records that match the request."""

    limit: int | None
    """Maximum number of returned records."""

    offset: int | None
    """Number of skipped records."""

    records: Sequence[Record]
    """List of records."""


ListRequestEvent = UUID

ListRequestAfter = NaiveDatetime | None

ListRequestBefore = NaiveDatetime | None

ListRequestLimit = int | None

ListRequestOffset = int | None

ListRequestOrder = ListOrder | None

ListResponseResults = RecordList

DownloadRequestEvent = UUID

DownloadRequestStart = NaiveDatetime

DownloadResponseType = str

DownloadResponseSize = int

DownloadResponseTag = str

DownloadResponseModified = datetime

DownloadResponseData = AsyncIterator[bytes]


@datamodel
class ListRequest:
    """Request to list records."""

    event: ListRequestEvent
    """Identifier of the event to list records for."""

    after: ListRequestAfter
    """Only list records after this datetime (in event timezone)."""

    before: ListRequestBefore
    """Only list records before this datetime (in event timezone)."""

    limit: ListRequestLimit
    """Maximum number of records to return."""

    offset: ListRequestOffset
    """Number of records to skip."""

    order: ListRequestOrder
    """Order to apply to the results."""


@datamodel
class ListResponse:
    """Response for listing records."""

    results: ListResponseResults
    """List of records."""


@datamodel
class DownloadRequest:
    """Request to download a record."""

    event: DownloadRequestEvent
    """Identifier of the event."""

    start: DownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class DownloadResponse:
    """Response for downloading a record."""

    type: DownloadResponseType
    """Type of the record data."""

    size: DownloadResponseSize
    """Size of the record in bytes."""

    tag: DownloadResponseTag
    """ETag of the record data."""

    modified: DownloadResponseModified
    """Datetime when the record was last modified."""

    data: DownloadResponseData
    """Data of the record."""
