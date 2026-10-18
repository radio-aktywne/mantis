from collections.abc import AsyncGenerator
from uuid import UUID

from mantis.models.base import datamodel
from mantis.utils.mime import MimeType
from mantis.utils.time import NaiveDatetime


type PrerecordingsDownloadRequestEvent = UUID

type PrerecordingsDownloadRequestStart = NaiveDatetime

type PrerecordingsDownloadResponseType = MimeType

type PrerecordingsDownloadResponseData = AsyncGenerator[bytes]


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
