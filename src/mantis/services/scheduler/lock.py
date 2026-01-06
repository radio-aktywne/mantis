from pylocks.asyncio import AsyncioLock
from pyscheduler.protocols import lock as l


class Lock(AsyncioLock, l.Lock):
    """Lock implementation for scheduler."""
