from pyqueues.asyncio import AsyncioQueue
from pyscheduler.protocols import queue as q


class Queue(AsyncioQueue, q.Queue):
    pass
