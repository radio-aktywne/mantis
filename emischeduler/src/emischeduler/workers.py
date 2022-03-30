import os
import signal
from multiprocessing import Process
from typing import Collection, List, Optional

from rq import Queue, Worker
from rq.defaults import DEFAULT_LOGGING_DATE_FORMAT, DEFAULT_LOGGING_FORMAT

from emischeduler.queues import QueueRegistry
from emischeduler.scheduling import PatchedWorker


class WorkerPool:
    def __init__(
        self,
        queues: Collection[Queue],
        n: int = 1,
        *args,
        burst: bool = False,
        logging_level: str = "INFO",
        date_format: str = DEFAULT_LOGGING_DATE_FORMAT,
        log_format: str = DEFAULT_LOGGING_FORMAT,
        max_jobs: Optional[int] = None,
        with_scheduler: bool = True,
        **kwargs,
    ) -> None:
        self.queues: Collection[Queue] = queues
        self.n: int = n
        self.args = args
        self.kwargs = kwargs
        self.work_args = (
            burst,
            logging_level,
            date_format,
            log_format,
            max_jobs,
            with_scheduler,
        )
        self.processes: List[Process] = []

    def _spawn_worker(self) -> Process:
        def _work(queues, args, kwargs, work_args) -> Worker:
            return PatchedWorker(queues, *args, **kwargs).work(*work_args)

        process = Process(
            target=_work,
            args=(self.queues, self.args, self.kwargs, self.work_args),
        )
        process.start()
        return process

    def start(self) -> None:
        if len(self.processes) > 0:
            raise RuntimeError("Already started.")
        for _ in range(self.n):
            self.processes.append(self._spawn_worker())

    def _shutdown(self, sig: int) -> None:
        for process in self.processes:
            try:
                os.kill(process.pid, sig)
            except ProcessLookupError:
                pass

    def end(self) -> None:
        self._shutdown(signal.SIGINT)

    def kill(self) -> None:
        self._shutdown(signal.SIGKILL)

    def wait(self) -> None:
        for process in self.processes:
            process.join()
        self.processes = []


class WorkerPoolRegistry:
    def __init__(self, queues: QueueRegistry, *args, **kwargs) -> None:
        self.sync_pool = WorkerPool([queues.sync_queue], n=1, *args, **kwargs)
        self.reserve_pool = WorkerPool(
            [queues.reserve_queue], n=4, *args, **kwargs
        )
        self.stream_pool = WorkerPool(
            [queues.stream_queue], n=1, *args, **kwargs
        )
        self.helpers_pool = WorkerPool(
            [queues.fetch_queue, queues.cleanup_queue], n=4, *args, **kwargs
        )

    def all(self) -> Collection[WorkerPool]:
        return (
            self.sync_pool,
            self.reserve_pool,
            self.stream_pool,
            self.helpers_pool,
        )

    def start(self) -> None:
        for pool in self.all():
            pool.start()

    def wait(self) -> None:
        for pool in self.all():
            pool.wait()
