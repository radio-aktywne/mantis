import asyncio
import math
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from emischeduler.config.models import SynchronizerConfig
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.scheduler.service import SchedulerService
from emischeduler.services.synchronizer.synchronizers.stream import StreamSynchronizer
from emischeduler.utils.time import naiveutcnow


class SynchronizerService:
    """Service to synchronize scheduled tasks with expected ones."""

    def __init__(
        self,
        config: SynchronizerConfig,
        emishows: EmishowsService,
        scheduler: SchedulerService,
    ) -> None:
        self._config = config
        self._synchronizers = [
            StreamSynchronizer(
                config=config.synchronizers.stream,
                emishows=emishows,
                scheduler=scheduler,
            )
        ]

    def _find_next_time(self, dt: datetime) -> datetime:
        reference = self._config.reference
        interval = self._config.interval

        return reference + math.ceil((dt - reference) / interval) * interval

    async def _wait(self) -> None:
        now = naiveutcnow()
        target = self._find_next_time(now)

        delta = target - now
        delta = delta.total_seconds()
        delta = max(delta, 0)

        await asyncio.sleep(delta)

    async def _synchronize(self) -> None:
        for synchronizer in self._synchronizers:
            await synchronizer.synchronize()

    async def _run(self) -> None:
        try:
            while True:
                await self._wait()
                try:
                    await self._synchronize()
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass
        except asyncio.CancelledError:
            pass

    @asynccontextmanager
    async def run(self) -> AsyncGenerator[None]:
        """Run in the context."""

        task = asyncio.create_task(self._run())

        try:
            yield
        finally:
            task.cancel()
            await task
