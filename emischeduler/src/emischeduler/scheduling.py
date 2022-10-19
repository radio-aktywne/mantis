from typing import Optional

from redis.client import Pipeline
from rq import Queue, scheduler, worker
from rq.job import Job, JobStatus


class PatchedQueue(Queue):
    """Queue that respects dependencies in enqueue_job.

    See: https://github.com/rq/rq/issues/1404.
    """

    def setup_dependencies(
        self, job: Job, pipeline: Optional[Pipeline] = None
    ):
        if (
            len(job._dependency_ids) == 0
            and pipeline is not None
            and pipeline.explicit_transaction
        ):
            return job
        return super().setup_dependencies(job, pipeline)

    def enqueue_job(
        self,
        job: Job,
        pipeline: Optional[Pipeline] = None,
        at_front: bool = False,
    ) -> Job:
        job = self.setup_dependencies(job, pipeline=pipeline)
        # If we do not depend on an unfinished job, enqueue the job.
        if job.get_status(refresh=False) != JobStatus.DEFERRED:
            return super().enqueue_job(job, pipeline, at_front)
        return job


class PatchedScheduler(scheduler.RQScheduler):
    scheduler.Queue = PatchedQueue


class PatchedWorker(worker.Worker):
    worker.RQScheduler = PatchedScheduler
