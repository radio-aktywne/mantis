import asyncio
from datetime import timedelta, timezone
from pathlib import Path
from socket import gethostbyname
from tempfile import TemporaryDirectory
from uuid import UUID

from pydantic import NaiveDatetime
from pyscheduler.models import types as t
from pyscheduler.protocols import operation as o
from pystreams.ffmpeg import FFmpegNode, FFmpegStreamMetadata
from pystreams.process import ProcessBasedStreamFactory
from zoneinfo import ZoneInfo

from emischeduler.config.models import Config
from emischeduler.datarecords import models as am
from emischeduler.datarecords.service import DatarecordsService
from emischeduler.emishows import errors as she
from emischeduler.emishows import models as shm
from emischeduler.emishows.service import EmishowsService
from emischeduler.emistream import errors as ste
from emischeduler.emistream import models as stm
from emischeduler.emistream.service import EmistreamService
from emischeduler.models.base import SerializableModel
from emischeduler.time import awareutcnow, naiveutcnow


class EventNotFoundError(Exception):
    """Raised when an event cannot be found."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"No event found for id {id}")


class ScheduleNotFoundError(Exception):
    """Raised when a schedule cannot be found."""

    def __init__(self, event: UUID) -> None:
        super().__init__(f"No schedule found for event {event}")


class InstanceNotFoundError(Exception):
    """Raised when an instance cannot be found."""

    def __init__(self, event: UUID, start: NaiveDatetime) -> None:
        super().__init__(
            f"No instance found for event {event} and start {start.isoformat()}"
        )


class InstanceAlreadyEndedError(Exception):
    """Raised when an instance has already ended."""

    def __init__(self, event: UUID, start: NaiveDatetime, end: NaiveDatetime) -> None:
        super().__init__(
            f"Instance for event {event} and start {start.isoformat()} has already ended at {end.isoformat()}"
        )


class UnexpectedEventTypeError(Exception):
    """Raised when an unexpected event type is encountered."""

    def __init__(self, event: UUID, type: shm.EventType) -> None:
        super().__init__(f"Event {event} has unexpected type {type}")


class DownloadUnavailableError(Exception):
    """Raised when a download is unavailable."""

    def __init__(self, event: UUID, start: NaiveDatetime) -> None:
        super().__init__(f"No download available for event {event} and start {start}")


class Parameters(SerializableModel):
    """Parameters for the stream operation."""

    id: UUID
    start: NaiveDatetime


class StreamOperation(o.Operation):
    """Streams an instance of an event."""

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

    async def _get_event(self, id: UUID) -> shm.Event:
        try:
            return await self._emishows.events.get_by_id(id)
        except she.EmishowsError as e:
            if not hasattr(e, "response") or e.response.status_code != 404:
                raise

            raise EventNotFoundError(id) from e

    async def _get_schedule(
        self, event: shm.Event, start: NaiveDatetime
    ) -> shm.EventSchedule:
        tz = ZoneInfo(event.timezone)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
        start = start.astimezone(timezone.utc).replace(tzinfo=None)
        end = start + timedelta(days=1)

        response = await self._emishows.schedule.list(
            start=start, end=end, where={"id": str(event.id)}
        )

        schedule = next(
            (
                schedule
                for schedule in response.schedules
                if schedule.event.id == event.id
            ),
            None,
        )

        if schedule is None:
            raise ScheduleNotFoundError(event.id)

        return schedule

    async def _find_instance(
        self, schedule: shm.EventSchedule, start: NaiveDatetime
    ) -> shm.EventInstance:
        instance = next(
            (instance for instance in schedule.instances if instance.start == start),
            None,
        )

        if instance is None:
            raise InstanceNotFoundError(schedule.event.id, start)

        return instance

    async def _find_replay_key(
        self, event: shm.Event, instance: shm.EventInstance
    ) -> str | None:
        tz = ZoneInfo(event.timezone)
        start = (
            instance.start.replace(tzinfo=tz)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

        response = await self._emishows.schedule.list(
            start=start - timedelta(weeks=4),
            end=start,
            where={"showId": str(event.show_id), "type": "live"},
        )

        pool = (
            (schedule.event, instance)
            for schedule in response.schedules
            for instance in schedule.instances
        )
        pool = sorted(pool, key=lambda item: item[1].start, reverse=True)

        for event, instance in pool:
            request = am.ListRequest(prefix=f"{event.id}/{instance.start.isoformat()}")
            response = await self._datarecords.live.list(request)

            object = next(iter(response.objects), None)
            if object is not None:
                return object.name

        return None

    async def _find_prerecorded_key(
        self, event: shm.Event, instance: shm.EventInstance
    ) -> str | None:
        request = am.ListRequest(prefix=f"{event.id}/{instance.start.isoformat()}")
        response = await self._datarecords.prerecorded.list(request)

        object = next(iter(response.objects), None)

        if object is None:
            return None

        return object.name

    async def _download(
        self, event: shm.Event, instance: shm.EventInstance, directory: str
    ) -> Path:
        match event.type:
            case shm.EventType.replay:
                key = await self._find_replay_key(event, instance)
                reader = self._datarecords.live
            case shm.EventType.prerecorded:
                key = await self._find_prerecorded_key(event, instance)
                reader = self._datarecords.prerecorded
            case _:
                raise UnexpectedEventTypeError(event.id, event.type)

        if key is None:
            raise DownloadUnavailableError(event.id, instance.start)

        path = Path(directory) / Path(key).name
        request = am.DownloadRequest(name=key, path=path)
        await reader.download(request)

        return path

    def _get_format(self, path: str) -> str:
        return Path(path).suffix[1:]

    async def _wait(
        self, event: shm.Event, instance: shm.EventInstance, delta: timedelta
    ) -> None:
        tz = ZoneInfo(event.timezone)
        start = (
            instance.start.replace(tzinfo=tz)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )
        target = start - delta
        now = naiveutcnow()
        delta = (target - now).total_seconds()
        delta = max(delta, 0)
        await asyncio.sleep(delta)

    async def _reserve(self, event: shm.Event, format: str) -> stm.ReserveResponse:
        request = stm.ReserveRequest(event=event.id, format=format, record=False)

        deadline = naiveutcnow() + self._config.stream.timeout

        while naiveutcnow() < deadline:
            sse = asyncio.create_task(anext(self._emistream.sse.subscribe()))

            try:
                return await self._emistream.reserve.reserve(request)
            except ste.EmistreamError as e:
                if not hasattr(e, "response") or e.response.status_code != 409:
                    raise

                timeout = deadline - naiveutcnow()
                await asyncio.wait_for(sse, timeout=timeout.total_seconds())
            finally:
                sse.cancel()

    def _build_stream_target(self) -> str:
        host = gethostbyname(self._config.emistream.srt.host)
        port = self._config.emistream.srt.port
        return f"srt://{host}:{port}"

    def _build_stream_input(self, path: Path, format: str) -> FFmpegNode:
        return FFmpegNode(
            target=str(path),
            options={
                "f": format,
                "re": True,
            },
        )

    def _build_stream_output(
        self, format: str, reservation: stm.ReserveResponse
    ) -> FFmpegNode:
        return FFmpegNode(
            target=self._build_stream_target(),
            options={
                "acodec": "copy",
                "f": format,
                "passphrase": reservation.credentials.token,
            },
        )

    def _build_stream_metadata(
        self, path: Path, format: str, reservation: stm.ReserveResponse
    ) -> FFmpegStreamMetadata:
        return FFmpegStreamMetadata(
            input=self._build_stream_input(path, format),
            output=self._build_stream_output(format, reservation),
        )

    async def _stream(
        self, path: Path, format: str, reservation: stm.ReserveResponse
    ) -> None:
        metadata = self._build_stream_metadata(path, format, reservation)
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
            reservation = await self._reserve(schedule.event, format)

            await self._wait(schedule.event, instance, timedelta(seconds=1))
            await self._stream(path, format, reservation)

        return None
