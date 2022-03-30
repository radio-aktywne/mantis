from typing import Collection

from pydantic import BaseModel
from rq import Queue

from emischeduler.scheduling import PatchedQueue


class QueueKeys(BaseModel):
    sync: str
    fetch: str
    reserve: str
    stream: str
    cleanup: str


class QueueRegistry:
    def __init__(self, *args, **kwargs) -> None:
        self.sync_queue = PatchedQueue("sync", *args, **kwargs)
        self.fetch_queue = PatchedQueue("fetch", *args, **kwargs)
        self.reserve_queue = PatchedQueue("reserve", *args, **kwargs)
        self.stream_queue = PatchedQueue("stream", *args, **kwargs)
        self.cleanup_queue = PatchedQueue("cleanup", *args, **kwargs)

    def all(self) -> Collection[Queue]:
        return (
            self.sync_queue,
            self.fetch_queue,
            self.reserve_queue,
            self.stream_queue,
            self.cleanup_queue,
        )

    def keys(self) -> QueueKeys:
        return QueueKeys(
            sync=self.sync_queue.key,
            fetch=self.fetch_queue.key,
            reserve=self.reserve_queue.key,
            stream=self.stream_queue.key,
            cleanup=self.cleanup_queue.key,
        )
