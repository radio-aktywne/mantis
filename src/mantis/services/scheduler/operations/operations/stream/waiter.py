import asyncio
from datetime import UTC, timedelta

from zoneinfo import ZoneInfo

from mantis.services.beaver import models as bm
from mantis.utils.time import naiveutcnow


class Waiter:
    """Utility to wait for a time before event start."""

    def __init__(self, event: bm.Event, instance: bm.EventInstance) -> None:
        self._event = event
        self._instance = instance

    async def wait(self, delta: timedelta) -> None:
        """Wait for a time before event start."""

        tz = ZoneInfo(self._event.timezone)

        start = self._instance.start
        start = start.replace(tzinfo=tz).astimezone(UTC).replace(tzinfo=None)

        target = start - delta
        now = naiveutcnow()
        delta = (target - now).total_seconds()
        delta = max(delta, 0)

        await asyncio.sleep(delta)
