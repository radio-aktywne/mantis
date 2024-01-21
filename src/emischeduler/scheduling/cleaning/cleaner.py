import asyncio
import math
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pydantic import NaiveDatetime
from pyscheduler.models import transfer as t

from emischeduler.config.models import CleanerConfig
from emischeduler.scheduling.scheduler import Scheduler
from emischeduler.time import naiveutcnow


class Cleaner:
    """Removes finished tasks from scheduler's state."""

    def __init__(self, config: CleanerConfig, scheduler: Scheduler) -> None:
        self._config = config
        self._scheduler = scheduler

    def _find_next_time(self, dt: NaiveDatetime) -> NaiveDatetime:
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
        request = t.CleanRequest()
        await self._scheduler.clean(request)

    async def _run(self) -> None:
        try:
            while True:
                await self._wait()
                await self._clean()
        except asyncio.CancelledError:
            pass

    @asynccontextmanager
    async def run(self) -> AsyncGenerator[None, None]:
        """Run in the context."""

        task = asyncio.create_task(self._run())

        try:
            yield
        finally:
            task.cancel()
            await task
