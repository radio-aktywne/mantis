from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

from mantis.config.models import Config
from mantis.services.beaver import models as bm
from mantis.services.beaver.service import BeaverService
from mantis.services.gecko import models as gm
from mantis.services.gecko.service import GeckoService
from mantis.services.numbat import models as nm
from mantis.services.numbat.service import NumbatService
from mantis.services.octopus import models as om
from mantis.services.scheduler.operations.operations.stream import errors as e
from mantis.services.scheduler.operations.operations.stream import models as m


class EventDownloader(ABC):
    """Base class for downloading media for events."""

    @abstractmethod
    async def download(
        self, event: bm.Event, instance: bm.EventInstance
    ) -> tuple[AsyncIterator[bytes], str]:
        """Download media for an event."""

        pass


class PrerecordedDownloader(EventDownloader):
    """Utility to download media for prerecorded events."""

    def __init__(self, beaver: BeaverService, numbat: NumbatService) -> None:
        self._beaver = beaver
        self._numbat = numbat

    async def _list_prerecordings(
        self, event: UUID, after: datetime, before: datetime
    ) -> list[nm.Prerecording]:
        prerecordings: list[nm.Prerecording] = []
        offset = 0

        while True:
            req = nm.ListRequest(
                event=event,
                after=after,
                before=before,
                limit=None,
                offset=offset,
                order=None,
            )

            res = await self._numbat.prerecordings.list(req)

            new = res.results.prerecordings
            count = res.results.count

            prerecordings = prerecordings + new
            offset = offset + len(new)

            if offset >= count:
                break

        return prerecordings

    async def _find_prerecording(
        self, event: bm.Event, instance: bm.EventInstance
    ) -> gm.Record | None:
        after = instance.start - timedelta(seconds=1)
        before = instance.end + timedelta(seconds=1)

        prerecordings = await self._list_prerecordings(event.id, after, before)
        return next(
            (
                prerecording
                for prerecording in prerecordings
                if prerecording.start == instance.start
            ),
            None,
        )

    async def _download_prerecording(
        self, prerecording: nm.Prerecording
    ) -> tuple[AsyncIterator[bytes], str]:
        req = nm.DownloadRequest(
            event=prerecording.event,
            start=prerecording.start,
        )

        res = await self._numbat.prerecordings.download(req)

        type = res.type
        data = res.data

        return data, type

    async def download(
        self, event: bm.Event, instance: bm.EventInstance
    ) -> tuple[AsyncIterator[bytes], str]:
        prerecording = await self._find_prerecording(event, instance)

        if prerecording is None:
            raise e.DownloadUnavailableError(event.id, instance.start)

        return await self._download_prerecording(prerecording)


class ReplayDownloader(EventDownloader):
    """Utility to download media for replay events."""

    def __init__(
        self, config: Config, beaver: BeaverService, gecko: GeckoService
    ) -> None:
        self._config = config
        self._beaver = beaver
        self._gecko = gecko

    async def _list_live_schedules(
        self, show: UUID, start: datetime, end: datetime
    ) -> list[bm.Schedule]:
        schedules: list[bm.Schedule] = []
        offset = 0

        while True:
            req = bm.ScheduleListRequest(
                start=start,
                end=end,
                limit=None,
                offset=offset,
                where={
                    "show_id": str(show),
                    "type": bm.EventType.live,
                },
                include=None,
                order=None,
            )

            res = await self._beaver.schedule.list(req)

            new = res.results.schedules
            count = res.results.count

            schedules = schedules + new
            offset = offset + len(new)

            if offset >= count:
                break

        return schedules

    async def _find_past_live_schedules(
        self, show: UUID, before: datetime
    ) -> list[bm.Schedule]:
        end = before
        start = end - self._config.operations.stream.window

        return await self._list_live_schedules(show, start, end)

    async def _list_records(
        self, event: UUID, after: datetime, before: datetime
    ) -> list[gm.Record]:
        records: list[gm.Record] = []
        offset = 0

        while True:
            req = gm.ListRequest(
                event=event,
                after=after,
                before=before,
                limit=None,
                offset=offset,
                order=None,
            )

            res = await self._gecko.records.list(req)

            new = res.results.records
            count = res.results.count

            records = records + new
            offset = offset + len(new)

            if offset >= count:
                break

        return records

    async def _list_last_records(
        self, event: UUID, before: datetime
    ) -> list[gm.Record]:
        after = before - self._config.operations.stream.window

        return await self._list_records(event, after, before)

    async def _find_last_record(
        self, schedules: list[bm.Schedule], before: datetime
    ) -> gm.Record | None:
        records: list[gm.Record] = []

        for schedule in schedules:
            times = {instance.start for instance in schedule.instances}
            last = await self._list_last_records(schedule.event.id, before)

            for record in last:
                if record.start in times:
                    records.append(record)

        if not records:
            return None

        return max(records, key=lambda record: record.start)

    async def _find_record(
        self, event: bm.Event, instance: bm.EventInstance
    ) -> gm.Record | None:
        show = event.show_id
        before = instance.start

        schedules = await self._find_past_live_schedules(show, before)
        return await self._find_last_record(schedules, before)

    async def _download_record(
        self, record: gm.Record
    ) -> tuple[AsyncIterator[bytes], str]:
        req = gm.DownloadRequest(
            event=record.event,
            start=record.start,
        )

        res = await self._gecko.records.download(req)

        type = res.type
        data = res.data

        return data, type

    async def download(
        self, event: bm.Event, instance: bm.EventInstance
    ) -> tuple[AsyncIterator[bytes], str]:
        record = await self._find_record(event, instance)

        if record is None:
            raise e.DownloadUnavailableError(event.id, instance.start)

        return await self._download_record(record)


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

    def _create_downloader(self, event: bm.Event) -> EventDownloader:
        match event.type:
            case bm.EventType.prerecorded:
                return PrerecordedDownloader(
                    beaver=self._beaver,
                    numbat=self._numbat,
                )
            case bm.EventType.replay:
                return ReplayDownloader(
                    config=self._config,
                    beaver=self._beaver,
                    gecko=self._gecko,
                )
            case _:
                raise e.UnexpectedEventTypeError(event.id, event.type)

    def _get_path(
        self, event: bm.Event, instance: bm.EventInstance, directory: Path
    ) -> Path:
        directory = directory / str(event.id)
        directory.mkdir(parents=True, exist_ok=True)

        return directory / instance.start.isoformat()

    def _map_format(self, type: str) -> om.Format:
        match type:
            case "audio/ogg":
                return om.Format.OGG
            case _:
                raise e.UnexpectedFormatError(type)

    async def _download_record(
        self, event: bm.Event, instance: bm.EventInstance, directory: Path
    ) -> tuple[Path, om.Format]:
        downloader = self._create_downloader(event)

        data, type = await downloader.download(event, instance)

        path = self._get_path(event, instance, directory)

        with open(path, "wb") as file:
            async for chunk in data:
                file.write(chunk)

        format = self._map_format(type)

        return path, format

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a replay record."""

        event = request.event
        instance = request.instance
        directory = Path(request.directory)

        path, format = await self._download_record(event, instance, directory)

        return m.DownloadResponse(
            path=path,
            format=format,
        )
