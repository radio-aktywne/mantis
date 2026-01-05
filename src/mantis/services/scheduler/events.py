from typing import override

from pyevents.asyncio import AsyncioEvent
from pyscheduler.protocols import event as e


class EventFactory(e.EventFactory):
    """Factory for creating events."""

    @override
    async def create(self, topic: str) -> e.Event:
        return AsyncioEvent()
