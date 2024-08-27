from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from zoneinfo import ZoneInfo

from emischeduler.config.models import Config
from emischeduler.services.emirecords import models as erem
from emischeduler.services.emirecords.service import EmirecordsService
from emischeduler.services.emishows import models as eshm
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream import models as estm
from emischeduler.services.scheduler.operations.operations.stream import models as m


class Downloader:
    """Utility to download replay records."""

    def __init__(
        self, config: Config, emirecords: EmirecordsService, emishows: EmishowsService
    ) -> None:
        self._config = config
        self._emirecords = emirecords
        self._emishows = emishows

    async def _list_schedules(
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

        return await self._list_schedules(show, start, end)

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
    ) -> erem.Record:
        records = [
            record
            for schedule in schedules
            for record in await self._list_last_records(schedule.event.id, before)
        ]

        return max(records, key=lambda record: record.start)

    def _map_format(self, type: str) -> estm.Format:
        match type:
            case "audio/ogg":
                return estm.Format.OGG

    async def _download_record(
        self, record: erem.Record, directory: Path
    ) -> tuple[Path, estm.Format]:
        req = erem.DownloadRequest(
            event=record.event,
            start=record.start,
        )

        res = await self._emirecords.records.download(req)

        type = res.type
        data = res.data

        directory = directory / str(record.event)
        directory.mkdir(parents=True, exist_ok=True)

        path = directory / record.start.isoformat()

        with open(path, "wb") as file:
            async for chunk in data:
                file.write(chunk)

        format = self._map_format(type)

        return path, format

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download a replay record."""

        event = request.event
        instance = request.instance
        directory = request.directory

        show = event.show_id
        tz = ZoneInfo(event.timezone)
        before = instance.start.replace(tzinfo=tz).astimezone(UTC).replace(tzinfo=None)

        schedules = await self._find_past_live_schedules(show, before)
        record = await self._find_last_record(schedules, before)
        directory = Path(directory)
        path, format = await self._download_record(record, directory)

        return m.DownloadResponse(
            path=path,
            format=format,
        )
