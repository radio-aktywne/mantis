from uuid import UUID

from pyqueues.asyncio import AsyncioQueue
from pyscheduler.protocols import queue as q


class Queue(AsyncioQueue[UUID], q.Queue[UUID]):
    """Queue implementation for scheduler."""
