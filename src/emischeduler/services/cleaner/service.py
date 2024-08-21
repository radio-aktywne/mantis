import asyncio
import math
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from emischeduler.config.models import CleanerConfig
from emischeduler.services.scheduler.models import transfer as t
from emischeduler.services.scheduler.service import SchedulerService
from emischeduler.utils.time import naiveutcnow


class CleanerService:
    """Service to remove finished tasks from scheduler's state."""

    def __init__(self, config: CleanerConfig, scheduler: SchedulerService) -> None:
        self._config = config
        self._scheduler = scheduler

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

    async def _clean(self) -> None:
        strategy = t.Specification(
            type="all",
            parameters={},
        )
        req = t.CleanRequest(
            strategy=strategy,
        )
        await self._scheduler.clean(req)

    async def _run(self) -> None:
        try:
            while True:
                await self._wait()
                await self._clean()
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
