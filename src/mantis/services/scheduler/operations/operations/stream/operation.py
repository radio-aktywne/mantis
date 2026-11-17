import asyncio
from collections.abc import Mapping
from contextlib import suppress
from datetime import timedelta
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

from pyscheduler.models import types as t
from pyscheduler.protocols import operation as o
from pystreams.base import Stream

from mantis.config.models import Config
from mantis.services.apis.beaver import models as bm
from mantis.services.apis.beaver.service import BeaverService
from mantis.services.apis.gecko.service import GeckoService
from mantis.services.apis.numbat.service import NumbatService
from mantis.services.apis.octopus import models as om
from mantis.services.apis.octopus.service import OctopusService
from mantis.services.scheduler.operations.operations.stream import (
    errors as e,
    models as m,
)
from mantis.services.scheduler.operations.operations.stream.downloader import Downloader
from mantis.services.scheduler.operations.operations.stream.finder import Finder
from mantis.services.scheduler.operations.operations.stream.reserver import Reserver
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
        self._finder = Finder(beaver=beaver)
        self._downloader = Downloader(
            config=config, beaver=beaver, gecko=gecko, numbat=numbat
        )
        self._reserver = Reserver(config=config, octopus=octopus)
        self._runner = Runner(config=config)

    async def _find_instance(self, params: m.Parameters) -> bm.InstanceWithEvent:
        find_request = m.FindRequest(event=params.event, start=params.start)

        find_response = await self._finder.find(find_request)

        return find_response.instance

    def _validate_instance(self, instance: bm.InstanceWithEvent) -> None:
        if instance.event.type not in {bm.EventType.replay, bm.EventType.prerecorded}:
            raise e.UnexpectedEventTypeError(instance.event)

        if (
            instance.start.replace(tzinfo=instance.event.timezone) + instance.duration
            < awareutcnow()
        ):
            raise e.InstanceAlreadyEndedError(instance)

    async def _download(
        self, instance: bm.InstanceWithEvent, directory: str
    ) -> tuple[Path, om.Format]:
        download_request = m.DownloadRequest(
            instance=instance, directory=Path(directory)
        )

        download_response = await self._downloader.download(download_request)

        return download_response.path, download_response.format

    async def _reserve(
        self, instance: bm.InstanceWithEvent, fmt: om.Format
    ) -> om.Credentials:
        reserve_request = m.ReserveRequest(instance=instance, format=fmt)

        reserve_response = await self._reserver.reserve(reserve_request)

        return reserve_response.credentials

    async def _stop_stream(self, stream: Stream) -> None:
        linger = ceil(self._config.operations.stream.linger.total_seconds())

        for action, timeout in ((stream.terminate, linger + 5), (stream.kill, 5)):
            with suppress(Exception):
                await asyncio.wait_for(action(), timeout=5)

            with suppress(Exception):
                await asyncio.wait_for(stream.wait(), timeout=timeout)
                return

        raise e.StreamStopError

    async def _stream(
        self,
        path: Path,
        fmt: om.Format,
        credentials: om.Credentials,
        metadata: Mapping[str, str] | None,
    ) -> None:
        stream = await self._runner.run(path, fmt, credentials, metadata)

        try:
            await stream.wait()
        except BaseException:
            task = asyncio.create_task(self._stop_stream(stream))

            while not task.done():
                with suppress(asyncio.CancelledError):
                    await asyncio.shield(task)

            await task
            raise

        if code := stream.process.returncode:
            raise e.StreamFailedError(code)

    @override
    async def run(
        self, parameters: dict[str, t.JSON], dependencies: dict[str, t.JSON]
    ) -> t.JSON:
        params = m.Parameters.model_validate(parameters)

        instance = await self._find_instance(params)
        self._validate_instance(instance)

        waiter = Waiter(instance)

        with TemporaryDirectory() as directory:
            path, fmt = await self._download(instance, directory)

            await waiter.wait(timedelta(seconds=10))
            credentials = await self._reserve(instance, fmt)

            await waiter.wait(timedelta(seconds=1))
            await self._stream(path, fmt, credentials, params.metadata)

        return None
