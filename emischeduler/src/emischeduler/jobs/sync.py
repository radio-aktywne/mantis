import logging
from datetime import datetime, timedelta
from logging import Logger
from tempfile import mkstemp

from rq import Queue, get_current_job

from emischeduler.jobs.cleanup import cleanup
from emischeduler.jobs.fetch import fetch
from emischeduler.jobs.reserve import reserve
from emischeduler.jobs.stream import stream
from emischeduler.models.sync import Event, Timetable
from emischeduler.queues import QueueKeys
from emischeduler.utils import ExponentialBackoffRetry, to_utc


def get_logger() -> Logger:
    return logging.getLogger("sync")


def get_timetable() -> Timetable:
    # TODO: fill after making emitimes
    return Timetable(events=[])


def get_queue(key: str) -> Queue:
    return Queue.from_queue_key(key)


def enqueue_replay(event: Event, keys: QueueKeys) -> None:
    _, path = mkstemp()
    fetch_job = get_queue(keys.fetch).enqueue_at(
        to_utc(event.start) - timedelta(minutes=30),
        fetch,
        event,
        path,
        retry=ExponentialBackoffRetry(max=5, delay=60),
    )
    reserve_job = get_queue(keys.reserve).enqueue_at(
        to_utc(event.start) - timedelta(seconds=5),
        reserve,
        event,
        depends_on=[fetch_job],
        retry=ExponentialBackoffRetry(max=10, delay=1),
    )
    stream_job = get_queue(keys.stream).enqueue_at(
        to_utc(event.start),
        stream,
        event,
        path,
        depends_on=[reserve_job],
        retry=ExponentialBackoffRetry(max=5, delay=5),
    )
    get_queue(keys.cleanup).enqueue_at(
        to_utc(event.end) + timedelta(minutes=30),
        cleanup,
        event,
        path,
        depends_on=[stream_job],
        retry=ExponentialBackoffRetry(max=5, delay=60),
    )


def enqueue_sync_at(keys: QueueKeys, dt: datetime) -> None:
    get_queue(keys.sync).enqueue_at(
        dt,
        sync,
        keys,
        retry=ExponentialBackoffRetry(max=5, delay=60),
    )


def enqueue_next_sync(keys: QueueKeys) -> None:
    enqueue_sync_at(
        keys, to_utc(get_current_job().enqueued_at) + timedelta(days=1)
    )


def sync_internal(keys: QueueKeys, logger: Logger = get_logger()) -> None:
    logger.info("Syncing events...")
    timetable = get_timetable()
    logger.info("Got timetable.")
    logger.info("Enqueueing events...")
    for event in timetable.events:
        if event.type == "replay":
            enqueue_replay(event, keys)
    logger.info("Events enqueued.")
    logger.info("Enqueueing next sync...")
    enqueue_next_sync(keys)
    logger.info("Next sync enqueued.")


def sync(keys: QueueKeys) -> None:
    return sync_internal(keys)
