from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from pyscheduler.models import types as t
from pyscheduler.protocols import operation as o
from zoneinfo import ZoneInfo

from emischeduler.config.models import Config
from emischeduler.services.emirecords.service import EmirecordsService
from emischeduler.services.emishows import models as eshm
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream import models as estm
from emischeduler.services.emistream.service import EmistreamService
from emischeduler.services.scheduler.operations.operations.stream import errors as e
from emischeduler.services.scheduler.operations.operations.stream import models as m
from emischeduler.services.scheduler.operations.operations.stream.downloader import (
    Downloader,
)
from emischeduler.services.scheduler.operations.operations.stream.finder import Finder
from emischeduler.services.scheduler.operations.operations.stream.reserver import (
    Reserver,
)
from emischeduler.services.scheduler.operations.operations.stream.runner import Runner
from emischeduler.services.scheduler.operations.operations.stream.waiter import Waiter
from emischeduler.utils.time import awareutcnow


class StreamOperation(o.Operation):
    """Operation for streaming an instance of an event."""

    def __init__(
        self,
        config: Config,
        emirecords: EmirecordsService,
        emishows: EmishowsService,
        emistream: EmistreamService,
    ) -> None:
        self._config = config
        self._finder = Finder(
            emishows=emishows,
        )
        self._downloader = Downloader(
            config=config,
            emirecords=emirecords,
            emishows=emishows,
        )
        self._reserver = Reserver(
            config=config,
            emistream=emistream,
        )
        self._runner = Runner(
            config=config,
        )

    def _parse_parameters(self, parameters: dict[str, t.JSON]) -> m.Parameters:
        return m.Parameters.model_validate(parameters)

    async def _find_instance(
        self, event: UUID, start: datetime
    ) -> tuple[eshm.Event, eshm.EventInstance]:
        req = m.FindRequest(
            event=event,
            start=start,
        )

        res = await self._finder.find(req)

        return res.event, res.instance

    def _validate_instance(
        self, event: eshm.Event, instance: eshm.EventInstance
    ) -> None:
        tz = ZoneInfo(event.timezone)
        if instance.end.replace(tzinfo=tz) < awareutcnow():
            raise e.InstanceAlreadyEndedError(event.id, instance.start, instance.end)

    async def _download(
        self, event: eshm.Event, instance: eshm.EventInstance, directory: str
    ) -> tuple[Path, estm.Format]:
        req = m.DownloadRequest(
            event=event,
            instance=instance,
            directory=Path(directory),
        )

        res = await self._downloader.download(req)

        return res.path, res.format

    async def _reserve(
        self, event: eshm.Event, format: estm.Format
    ) -> estm.Credentials:
        req = m.ReserveRequest(
            event=event.id,
            format=format,
        )

        res = await self._reserver.reserve(req)

        return res.credentials

    async def _stream(
        self, path: Path, format: estm.Format, credentials: estm.Credentials
    ) -> None:
        stream = await self._runner.run(path, format, credentials)
        await stream.wait()

    async def run(
        self, parameters: dict[str, t.JSON], dependencies: dict[str, t.JSON]
    ) -> t.JSON:
        params = self._parse_parameters(parameters)

        event, instance = await self._find_instance(params.id, params.start)
        self._validate_instance(event, instance)

        waiter = Waiter(event, instance)

        with TemporaryDirectory() as directory:
            path, format = await self._download(event, instance, directory)

            await waiter.wait(timedelta(seconds=10))
            credentials = await self._reserve(event, format)

            await waiter.wait(timedelta(seconds=1))
            await self._stream(path, format, credentials)

        return None
