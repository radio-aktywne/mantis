from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override
from uuid import UUID
from zoneinfo import ZoneInfo

from pyscheduler.models import types as t
from pyscheduler.protocols import operation as o

from mantis.config.models import Config
from mantis.services.beaver import models as bm
from mantis.services.beaver.service import BeaverService
from mantis.services.gecko.service import GeckoService
from mantis.services.numbat.service import NumbatService
from mantis.services.octopus import models as om
from mantis.services.octopus.service import OctopusService
from mantis.services.scheduler.operations.operations.stream import errors as e
from mantis.services.scheduler.operations.operations.stream import models as m
from mantis.services.scheduler.operations.operations.stream.downloader import (
    Downloader,
)
from mantis.services.scheduler.operations.operations.stream.finder import Finder
from mantis.services.scheduler.operations.operations.stream.reserver import (
    Reserver,
)
from mantis.services.scheduler.operations.operations.stream.runner import Runner
from mantis.services.scheduler.operations.operations.stream.waiter import Waiter
from mantis.utils.time import awareutcnow


class StreamOperation(o.Operation):
    """Operation for streaming an instance of an event."""

    def __init__(
        self,
        config: Config,
        beaver: BeaverService,
        gecko: GeckoService,
        numbat: NumbatService,
        octopus: OctopusService,
    ) -> None:
        self._config = config
        self._finder = Finder(
            beaver=beaver,
        )
        self._downloader = Downloader(
            config=config,
            beaver=beaver,
            gecko=gecko,
            numbat=numbat,
        )
        self._reserver = Reserver(
            config=config,
            octopus=octopus,
        )
        self._runner = Runner(
            config=config,
        )

    def _parse_parameters(self, parameters: dict[str, t.JSON]) -> m.Parameters:
        return m.Parameters.model_validate(parameters)

    async def _find_instance(
        self, event: UUID, start: datetime
    ) -> tuple[bm.Event, bm.EventInstance]:
        req = m.FindRequest(
            event=event,
            start=start,
        )

        res = await self._finder.find(req)

        return res.event, res.instance

    def _validate_instance(self, event: bm.Event, instance: bm.EventInstance) -> None:
        if event.type not in {bm.EventType.replay, bm.EventType.prerecorded}:
            raise e.UnexpectedEventTypeError(event.id, event.type)

        tz = ZoneInfo(event.timezone)
        if instance.end.replace(tzinfo=tz) < awareutcnow():
            raise e.InstanceAlreadyEndedError(event.id, instance.start, instance.end)

    async def _download(
        self, event: bm.Event, instance: bm.EventInstance, directory: str
    ) -> tuple[Path, om.Format]:
        req = m.DownloadRequest(
            event=event,
            instance=instance,
            directory=Path(directory),
        )

        res = await self._downloader.download(req)

        return res.path, res.format

    async def _reserve(self, event: bm.Event, fmt: om.Format) -> om.Credentials:
        req = m.ReserveRequest(
            event=event.id,
            format=fmt,
        )

        res = await self._reserver.reserve(req)

        return res.credentials

    async def _stream(
        self, path: Path, fmt: om.Format, credentials: om.Credentials
    ) -> None:
        stream = await self._runner.run(path, fmt, credentials)
        await stream.wait()

    @override
    async def run(
        self, parameters: dict[str, t.JSON], dependencies: dict[str, t.JSON]
    ) -> t.JSON:
        params = self._parse_parameters(parameters)

        event, instance = await self._find_instance(params.id, params.start)
        self._validate_instance(event, instance)

        waiter = Waiter(event, instance)

        with TemporaryDirectory() as directory:
            path, fmt = await self._download(event, instance, directory)

            await waiter.wait(timedelta(seconds=10))
            credentials = await self._reserve(event, fmt)

            await waiter.wait(timedelta(seconds=1))
            await self._stream(path, fmt, credentials)

        return None
