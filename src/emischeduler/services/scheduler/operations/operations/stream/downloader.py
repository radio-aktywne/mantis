from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

from emischeduler.config.models import Config
from emischeduler.services.emilounge import models as elom
from emischeduler.services.emilounge.service import EmiloungeService
from emischeduler.services.emirecords import models as erem
from emischeduler.services.emirecords.service import EmirecordsService
from emischeduler.services.emishows import models as eshm
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream import models as estm
from emischeduler.services.scheduler.operations.operations.stream import errors as e
from emischeduler.services.scheduler.operations.operations.stream import models as m


class EventDownloader(ABC):
    """Base class for downloading media for events."""

    @abstractmethod
    async def download(
        self, event: eshm.Event, instance: eshm.EventInstance
    ) -> tuple[AsyncIterator[bytes], str]:
        """Download media for an event."""

        pass


class PrerecordedDownloader(EventDownloader):
    """Utility to download media for prerecorded events."""

    def __init__(self, emilounge: EmiloungeService, emishows: EmishowsService) -> None:
        self._emilounge = emilounge
        self._emishows = emishows

    async def _list_prerecordings(
        self, event: UUID, after: datetime, before: datetime
    ) -> list[elom.Prerecording]:
        prerecordings: list[elom.Prerecording] = []
        offset = 0

        while True:
            req = elom.ListRequest(
                event=event,
                after=after,
                before=before,
                limit=None,
                offset=offset,
                order=None,
            )

            res = await self._emilounge.prerecordings.list(req)

            new = res.results.prerecordings
            count = res.results.count

            prerecordings = prerecordings + new
            offset = offset + len(new)

            if offset >= count:
                break

        return prerecordings

    async def _find_prerecording(
        self, event: eshm.Event, instance: eshm.EventInstance
    ) -> erem.Record | None:
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
        self, prerecording: elom.Prerecording
    ) -> tuple[AsyncIterator[bytes], str]:
        req = elom.DownloadRequest(
            event=prerecording.event,
            start=prerecording.start,
        )

        res = await self._emilounge.prerecordings.download(req)

        type = res.type
        data = res.data

        return data, type

    async def download(
        self, event: eshm.Event, instance: eshm.EventInstance
    ) -> tuple[AsyncIterator[bytes], str]:
        prerecording = await self._find_prerecording(event, instance)

        if prerecording is None:
            raise e.DownloadUnavailableError(event.id, instance.start)

        return await self._download_prerecording(prerecording)


class ReplayDownloader(EventDownloader):
    """Utility to download media for replay events."""

    def __init__(
        self, config: Config, emirecords: EmirecordsService, emishows: EmishowsService
    ) -> None:
        self._config = config
        self._emirecords = emirecords
        self._emishows = emishows

    async def _list_live_schedules(
        self, show: UUID, start: datetime, end: datetime
    ) -> list[eshm.Schedule]:
        schedules: list[eshm.Schedule] = []
        offset = 0

        while True:
            req = eshm.ScheduleListRequest(
                start=start,
                end=end,
                limit=None,
                offset=offset,
                where={
                    "show_id": str(show),
                    "type": eshm.EventType.live,
                },
                include=None,
                order=None,
            )

            res = await self._emishows.schedule.list(req)

            new = res.results.schedules
            count = res.results.count

            schedules = schedules + new
            offset = offset + len(new)

            if offset >= count:
                break

        return schedules

    async def _find_past_live_schedules(
        self, show: UUID, before: datetime
    ) -> list[eshm.Schedule]:
        end = before
        start = end - self._config.operations.stream.window

        return await self._list_live_schedules(show, start, end)

    async def _list_records(
        self, event: UUID, after: datetime, before: datetime
    ) -> list[erem.Record]:
        records: list[erem.Record] = []
        offset = 0

        while True:
            req = erem.ListRequest(
                event=event,
                after=after,
                before=before,
                limit=None,
                offset=offset,
                order=None,
            )

            res = await self._emirecords.records.list(req)

            new = res.results.records
            count = res.results.count

            records = records + new
            offset = offset + len(new)

            if offset >= count:
                break

        return records

    async def _list_last_records(
        self, event: UUID, before: datetime
    ) -> list[erem.Record]:
        after = before - self._config.operations.stream.window

        return await self._list_records(event, after, before)

    async def _find_last_record(
        self, schedules: list[eshm.Schedule], before: datetime
    ) -> erem.Record | None:
        records: list[erem.Record] = []

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
        self, event: eshm.Event, instance: eshm.EventInstance
    ) -> erem.Record | None:
        show = event.show_id
        before = instance.start

        schedules = await self._find_past_live_schedules(show, before)
        return await self._find_last_record(schedules, before)

    async def _download_record(
        self, record: erem.Record
    ) -> tuple[AsyncIterator[bytes], str]:
        req = erem.DownloadRequest(
            event=record.event,
            start=record.start,
        )

        res = await self._emirecords.records.download(req)

        type = res.type
        data = res.data

        return data, type

    async def download(
        self, event: eshm.Event, instance: eshm.EventInstance
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
        emilounge: EmiloungeService,
        emirecords: EmirecordsService,
        emishows: EmishowsService,
    ) -> None:
        self._config = config
        self._emilounge = emilounge
        self._emirecords = emirecords
        self._emishows = emishows

    def _create_downloader(self, event: eshm.Event) -> EventDownloader:
        match event.type:
            case eshm.EventType.prerecorded:
                return PrerecordedDownloader(
                    emilounge=self._emilounge,
                    emishows=self._emishows,
                )
            case eshm.EventType.replay:
                return ReplayDownloader(
                    config=self._config,
                    emirecords=self._emirecords,
                    emishows=self._emishows,
                )
            case _:
                raise e.UnexpectedEventTypeError(event.id, event.type)

    def _get_path(
        self, event: eshm.Event, instance: eshm.EventInstance, directory: Path
    ) -> Path:
        directory = directory / str(event.id)
        directory.mkdir(parents=True, exist_ok=True)

        return directory / instance.start.isoformat()

    def _map_format(self, type: str) -> estm.Format:
        match type:
            case "audio/ogg":
                return estm.Format.OGG
            case _:
                raise e.UnexpectedFormatError(type)

    async def _download_record(
        self, event: eshm.Event, instance: eshm.EventInstance, directory: Path
    ) -> tuple[Path, estm.Format]:
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
