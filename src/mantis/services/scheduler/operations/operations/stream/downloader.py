from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import override
from uuid import UUID

from mantis.config.models import Config
from mantis.services.apis.beaver import models as bm
from mantis.services.apis.beaver.service import BeaverService
from mantis.services.apis.gecko import errors as ge, models as gm
from mantis.services.apis.gecko.service import GeckoService
from mantis.services.apis.numbat import errors as ne, models as nm
from mantis.services.apis.numbat.service import NumbatService
from mantis.services.apis.octopus import models as om
from mantis.services.scheduler.operations.operations.stream import (
    errors as e,
    models as m,
)
from mantis.utils.mime import MimeType
from mantis.utils.time import isostringify


class EventDownloader(ABC):
    """Base class for downloading media for instances."""

    @abstractmethod
    async def download(
        self, instance: bm.InstanceWithEvent
    ) -> tuple[AsyncGenerator[bytes], MimeType]:
        """Download media for an instance."""


class PrerecordedDownloader(EventDownloader):
    """Utility to download media for prerecorded instances."""

    def __init__(self, beaver: BeaverService, numbat: NumbatService) -> None:
        self._beaver = beaver
        self._numbat = numbat

    async def _download_prerecording(
        self, event: UUID, start: datetime
    ) -> tuple[AsyncGenerator[bytes], MimeType] | None:
        prerecordings_download_request = nm.PrerecordingsDownloadRequest(
            event=event, start=start
        )

        try:
            prerecordings_download_response = await self._numbat.prerecordings.download(
                prerecordings_download_request
            )
        except ne.NotFoundError:
            return None

        return (
            prerecordings_download_response.data,
            prerecordings_download_response.type,
        )

    @override
    async def download(
        self, instance: bm.InstanceWithEvent
    ) -> tuple[AsyncGenerator[bytes], MimeType]:
        result = await self._download_prerecording(instance.event.id, instance.start)

        if result is None:
            raise e.DownloadUnavailableError(instance)

        return result


class ReplayDownloader(EventDownloader):
    """Utility to download media for replay instances."""

    def __init__(
        self, config: Config, beaver: BeaverService, gecko: GeckoService
    ) -> None:
        self._config = config
        self._beaver = beaver
        self._gecko = gecko

    async def _list_live_instances(
        self, show: UUID, start: datetime, end: datetime
    ) -> Sequence[bm.InstanceWithEvent]:
        instances_list_request = bm.InstancesListRequest(
            start=start,
            end=end,
            where={"event": {"is": {"show_id": show, "type": bm.EventType.live}}},
            include={"event": True},
        )

        instances_list_response = await self._beaver.instances.list(
            instances_list_request
        )

        return [
            instance
            for instance in instances_list_response.results.instances
            if isinstance(instance, bm.InstanceWithEvent)
        ]

    async def _find_past_live_instances(
        self, instance: bm.InstanceWithEvent
    ) -> Sequence[bm.InstanceWithEvent] | None:
        end = instance.start.replace(tzinfo=instance.event.timezone).astimezone(UTC)
        start = end - self._config.operations.stream.window

        if instance.event.show_id is None:
            return None

        return await self._list_live_instances(instance.event.show_id, start, end)

    async def _list_recordings(
        self, event: UUID, after: datetime, before: datetime
    ) -> Sequence[gm.Recording]:
        recordings_list_request = gm.RecordingsListRequest(
            event=event, after=after, before=before, limit=None, offset=None
        )

        recordings_list_response = await self._gecko.recordings.list(
            recordings_list_request
        )

        return recordings_list_response.results.recordings

    async def _list_last_recordings(
        self, event: bm.Event, before: datetime
    ) -> Sequence[gm.Recording]:
        before = before.astimezone(event.timezone).replace(tzinfo=None)
        after = before - self._config.operations.stream.window

        return await self._list_recordings(event.id, after, before)

    async def _find_last_recording(
        self, instances: Sequence[bm.InstanceWithEvent], before: datetime
    ) -> gm.Recording | None:
        recordings: list[gm.Recording] = []
        events = {instance.event_id: instance.event for instance in instances}

        for event in events.values():
            last = await self._list_last_recordings(event, before)

            times = {
                instance.start
                for instance in instances
                if instance.event.id == event.id
            }

            recordings = recordings + [
                recording for recording in last if recording.start in times
            ]

        if not recordings:
            return None

        def get_recording_start_in_utc(recording: gm.Recording) -> datetime:
            event = events[recording.event]
            return recording.start.replace(tzinfo=event.timezone).astimezone(UTC)

        return max(recordings, key=get_recording_start_in_utc)

    async def _find_recording(
        self, instance: bm.InstanceWithEvent
    ) -> gm.Recording | None:
        instances = await self._find_past_live_instances(instance)

        if not instances:
            return None

        before = instance.start.replace(tzinfo=instance.event.timezone).astimezone(UTC)
        return await self._find_last_recording(instances, before)

    async def _download_recording(
        self, event: UUID, start: datetime
    ) -> tuple[AsyncGenerator[bytes], MimeType] | None:
        recordings_download_request = gm.RecordingsDownloadRequest(
            event=event, start=start
        )

        try:
            recordings_download_response = await self._gecko.recordings.download(
                recordings_download_request
            )
        except ge.NotFoundError:
            return None

        return recordings_download_response.data, recordings_download_response.type

    @override
    async def download(
        self, instance: bm.InstanceWithEvent
    ) -> tuple[AsyncGenerator[bytes], MimeType]:
        recording = await self._find_recording(instance)

        if recording is None:
            raise e.DownloadUnavailableError(instance)

        result = await self._download_recording(recording.event, recording.start)

        if result is None:
            raise e.DownloadUnavailableError(instance)

        return result


class Downloader:
    """Utility to download media to stream."""

    def __init__(
        self,
        config: Config,
        beaver: BeaverService,
        gecko: GeckoService,
        numbat: NumbatService,
    ) -> None:
        self._config = config
        self._beaver = beaver
        self._gecko = gecko
        self._numbat = numbat

    def _create_downloader(self, instance: bm.InstanceWithEvent) -> EventDownloader:
        match instance.event.type:
            case bm.EventType.prerecorded:
                return PrerecordedDownloader(beaver=self._beaver, numbat=self._numbat)
            case bm.EventType.replay:
                return ReplayDownloader(
                    config=self._config, beaver=self._beaver, gecko=self._gecko
                )
            case _:
                raise e.UnexpectedEventTypeError(instance.event)

    def _get_path(self, instance: bm.InstanceWithEvent, directory: Path) -> Path:
        directory = directory / str(instance.event.id)
        directory.mkdir(parents=True, exist_ok=True)

        return directory / isostringify(instance.start)

    def _map_format(self, content_type: MimeType) -> om.Format:
        match content_type:
            case MimeType(type="audio", subtype="ogg"):
                return om.Format.OGG
            case _:
                raise e.UnexpectedFormatError(content_type)

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download media for an instance."""
        downloader = self._create_downloader(request.instance)

        data, content_type = await downloader.download(request.instance)

        try:
            path = self._get_path(request.instance, Path(request.directory))
            fmt = self._map_format(content_type)

            with path.open("wb") as file:
                async for chunk in data:
                    file.write(chunk)
        finally:
            await data.aclose()

        return m.DownloadResponse(path=path, format=fmt)
