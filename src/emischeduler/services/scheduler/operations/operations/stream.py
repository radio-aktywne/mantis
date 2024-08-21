import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from pyscheduler.models import types as t
from pyscheduler.protocols import operation as o
from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.process import ProcessBasedStreamFactory
from zoneinfo import ZoneInfo

from emischeduler.config.models import Config
from emischeduler.models.base import SerializableModel
from emischeduler.services.datarecords import models as drm
from emischeduler.services.datarecords.service import DatarecordsService
from emischeduler.services.emishows import errors as eshe
from emischeduler.services.emishows import models as eshm
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream import errors as este
from emischeduler.services.emistream import models as estm
from emischeduler.services.emistream.service import EmistreamService
from emischeduler.utils.time import NaiveDatetime, awareutcnow, naiveutcnow


class EventNotFoundError(Exception):
    """Raised when an event cannot be found."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"No event found for id {id}.")


class ScheduleNotFoundError(Exception):
    """Raised when a schedule cannot be found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No schedule found for event {event}.")


class InstanceNotFoundError(Exception):
    """Raised when an instance cannot be found."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(
            f"No instance found for event {event} and start {start.isoformat()}."
        )


class InstanceAlreadyEndedError(Exception):
    """Raised when an instance has already ended."""

    def __init__(self, event: UUID, start: datetime, end: datetime) -> None:
        super().__init__(
            f"Instance for event {event} and start {start.isoformat()} has already ended at {end.isoformat()}."
        )


class UnexpectedEventTypeError(Exception):
    """Raised when an unexpected event type is encountered."""

    def __init__(self, event: UUID, type: eshm.EventType) -> None:
        super().__init__(f"Event {event} has unexpected type {type}.")


class DownloadUnavailableError(Exception):
    """Raised when a download is unavailable."""

    def __init__(self, event: UUID, start: datetime) -> None:
        super().__init__(f"No download available for event {event} and start {start}.")


class Parameters(SerializableModel):
    """Parameters for the stream operation."""

    id: UUID
    """Identifier of the event."""

    start: NaiveDatetime
    """Start date and time of the instance of the event."""


class StreamOperation(o.Operation):
    """Operation for streaming an instance of an event."""

    def __init__(
        self,
        config: Config,
        datarecords: DatarecordsService,
        emishows: EmishowsService,
        emistream: EmistreamService,
    ) -> None:
        self._config = config
        self._datarecords = datarecords
        self._emishows = emishows
        self._emistream = emistream

    def _parse_parameters(self, parameters: dict[str, t.JSON]) -> Parameters:
        return Parameters.model_validate(parameters)

    async def _get_event(self, id: UUID) -> eshm.Event:
        req = eshm.EventsGetRequest(
            id=id,
            include=None,
        )

        try:
            res = await self._emishows.events.mget(req)
        except eshe.ServiceError as ex:
            if not hasattr(ex, "response") or ex.response.status_code != 404:
                raise

            raise EventNotFoundError(id) from ex

        return res.event

    async def _get_schedule(self, event: eshm.Event, start: datetime) -> eshm.Schedule:
        tz = ZoneInfo(event.timezone)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
        start = start.astimezone(UTC).replace(tzinfo=None)
        end = start + timedelta(days=1)

        req = eshm.ScheduleListRequest(
            start=start,
            end=end,
            limit=None,
            offset=None,
            where={
                "id": str(event.id),
            },
            include=None,
            order=None,
        )

        res = await self._emishows.schedule.list(req)

        schedules = res.results.schedules

        schedule = next(
            (schedule for schedule in schedules if schedule.event.id == event.id),
            None,
        )

        if schedule is None:
            raise ScheduleNotFoundError(event.id)

        return schedule

    async def _find_instance(
        self, schedule: eshm.Schedule, start: datetime
    ) -> eshm.EventInstance:
        instance = next(
            (instance for instance in schedule.instances if instance.start == start),
            None,
        )

        if instance is None:
            raise InstanceNotFoundError(schedule.event.id, start)

        return instance

    async def _find_replay_key(
        self, event: eshm.Event, instance: eshm.EventInstance
    ) -> str | None:
        tz = ZoneInfo(event.timezone)
        start = instance.start.replace(tzinfo=tz).astimezone(UTC).replace(tzinfo=None)

        req = eshm.ScheduleListRequest(
            start=start - timedelta(weeks=4),
            end=start,
            limit=None,
            offset=None,
            where={
                "showId": str(event.show_id),
                "type": "live",
            },
            include=None,
            order=None,
        )

        res = await self._emishows.schedule.list(req)

        schedules = res.results.schedules

        pool = (
            (schedule.event, instance)
            for schedule in schedules
            for instance in schedule.instances
        )
        pool = sorted(pool, key=lambda item: item[1].start, reverse=True)

        for event, instance in pool:
            req = drm.ListRequest(
                prefix=f"{event.id}/{instance.start.isoformat()}",
            )
            res = await self._datarecords.live.list(req)

            objects = res.objects

            object = await anext(objects, None)

            if object is not None:
                return object.name

        return None

    async def _find_prerecorded_key(
        self, event: eshm.Event, instance: eshm.EventInstance
    ) -> str | None:
        req = drm.ListRequest(
            prefix=f"{event.id}/{instance.start.isoformat()}",
        )
        res = await self._datarecords.prerecorded.list(req)

        objects = res.objects

        object = await anext(objects, None)

        if object is None:
            return None

        return object.name

    async def _download(
        self, event: eshm.Event, instance: eshm.EventInstance, directory: str
    ) -> Path:
        match event.type:
            case eshm.EventType.replay:
                key = await self._find_replay_key(event, instance)
                reader = self._datarecords.live
            case eshm.EventType.prerecorded:
                key = await self._find_prerecorded_key(event, instance)
                reader = self._datarecords.prerecorded
            case _:
                raise UnexpectedEventTypeError(event.id, event.type)

        if key is None:
            raise DownloadUnavailableError(event.id, instance.start)

        path = Path(directory) / Path(key).name

        req = drm.DownloadRequest(
            name=key,
        )
        res = await reader.download(req)

        data = res.content.data

        with open(path, "wb") as file:
            async for chunk in data:
                file.write(chunk)

        return path

    def _get_format(self, path: str) -> str:
        return Path(path).suffix[1:]

    async def _wait(
        self, event: eshm.Event, instance: eshm.EventInstance, delta: timedelta
    ) -> None:
        tz = ZoneInfo(event.timezone)
        start = instance.start.replace(tzinfo=tz).astimezone(UTC).replace(tzinfo=None)
        target = start - delta
        now = naiveutcnow()
        delta = (target - now).total_seconds()
        delta = max(delta, 0)
        await asyncio.sleep(delta)

    async def _reserve(self, event: eshm.Event, format: str) -> estm.Credentials:
        data = estm.ReserveRequestData(
            event=event.id,
            format=estm.Format(format),
            record=False,
        )

        deadline = naiveutcnow() + self._config.stream.timeout

        while naiveutcnow() < deadline:
            req = estm.SubscribeRequest()
            res = await self._emistream.sse.subscribe(req)
            sse = asyncio.create_task(anext(res.events))

            req = estm.ReserveRequest(
                data=data,
            )

            try:
                res = await self._emistream.reserve.reserve(req)
            except este.ServiceError as ex:
                if not hasattr(ex, "response") or ex.response.status_code != 409:
                    raise

                timeout = deadline - naiveutcnow()
                await asyncio.wait_for(sse, timeout=timeout.total_seconds())
            else:
                return res.data.credentials
            finally:
                sse.cancel()

    def _build_stream_target(self) -> str:
        return self._config.emistream.srt.url

    def _build_stream_input(self, path: Path, format: str) -> FFmpegNode:
        return FFmpegNode(
            target=str(path),
            options={
                "f": format,
                "re": True,
            },
        )

    def _build_stream_output(
        self, format: str, credentials: estm.Credentials
    ) -> FFmpegNode:
        return FFmpegNode(
            target=self._build_stream_target(),
            options={
                "acodec": "copy",
                "f": format,
                "passphrase": credentials.token,
            },
        )

    def _build_stream_metadata(
        self, path: Path, format: str, credentials: estm.Credentials
    ) -> FFmpegStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_stream_input(path, format),
            output=self._build_stream_output(format, credentials),
        )

    async def _stream(
        self, path: Path, format: str, credentials: estm.Credentials
    ) -> None:
        metadata = self._build_stream_metadata(path, format, credentials)
        stream = await ProcessBasedStreamFactory().create(metadata)
        await stream.wait()

    async def run(
        self, parameters: dict[str, t.JSON], dependencies: dict[str, t.JSON]
    ) -> t.JSON:
        params = self._parse_parameters(parameters)

        event = await self._get_event(params.id)
        schedule = await self._get_schedule(event, params.start)
        instance = await self._find_instance(schedule, params.start)

        tz = ZoneInfo(schedule.event.timezone)
        if instance.end.replace(tzinfo=tz) < awareutcnow():
            raise InstanceAlreadyEndedError(
                schedule.event.id, instance.start, instance.end
            )

        with TemporaryDirectory() as directory:
            path = await self._download(schedule.event, instance, directory)
            format = self._get_format(path)

            await self._wait(schedule.event, instance, timedelta(seconds=10))
            credentials = await self._reserve(schedule.event, format)

            await self._wait(schedule.event, instance, timedelta(seconds=1))
            await self._stream(path, format, credentials)

        return None
