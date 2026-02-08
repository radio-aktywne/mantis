from collections.abc import AsyncIterator, Sequence
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.utils.time import NaiveDatetime


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

    records: Sequence[Record]
    """List of records."""


type RecordsListRequestEvent = UUID

type RecordsListRequestAfter = NaiveDatetime | None

type RecordsListRequestBefore = NaiveDatetime | None

type RecordsListRequestLimit = int | None

type RecordsListRequestOffset = int | None

type RecordsListResponseResults = RecordList

type RecordsDownloadRequestEvent = UUID

type RecordsDownloadRequestStart = NaiveDatetime

type RecordsDownloadResponseType = str

type RecordsDownloadResponseData = AsyncIterator[bytes]


@datamodel
class RecordsListRequest:
    """Request to list records."""

    event: RecordsListRequestEvent
    """Identifier of the event to list records for."""

    after: RecordsListRequestAfter
    """Only list records after this datetime (in event timezone)."""

    before: RecordsListRequestBefore
    """Only list records before this datetime (in event timezone)."""

    limit: RecordsListRequestLimit
    """Maximum number of records to return."""

    offset: RecordsListRequestOffset
    """Number of records to skip."""


@datamodel
class RecordsListResponse:
    """Response for listing records."""

    results: RecordsListResponseResults
    """List of records."""


@datamodel
class RecordsDownloadRequest:
    """Request to download a record."""

    event: RecordsDownloadRequestEvent
    """Identifier of the event."""

    start: RecordsDownloadRequestStart
    """Start datetime of the event instance in event timezone."""


@datamodel
class RecordsDownloadResponse:
    """Response for downloading a record."""

    type: RecordsDownloadResponseType
    """Type of the record data."""

    data: RecordsDownloadResponseData
    """Data of the record."""
