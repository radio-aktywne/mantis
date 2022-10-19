import logging
from datetime import datetime, timedelta
from tempfile import mkstemp
from typing import List

import httpx
from pydantic import parse_obj_as
from rq import Queue, get_current_job

from emischeduler.config.models import EmishowsConfig, Config
from emischeduler.jobs.cleanup import cleanup
from emischeduler.jobs.fetch import fetch
from emischeduler.jobs.reserve import reserve
from emischeduler.jobs.stream import stream
from emischeduler.models import stream as stream_models, sync as sync_models
from emischeduler.queues import QueueKeys
from emischeduler.utils import ExponentialBackoffRetry, to_utc, utcnow


def get_logger() -> logging.Logger:
    return logging.getLogger("sync")


def timetable_endpoint(host: str, port: int) -> str:
    return f"http://{host}:{port}/timetable/"


def get_timetable(config: EmishowsConfig) -> List[sync_models.Event]:
    from_date = utcnow()
    to_date = from_date + timedelta(days=1)
    response = httpx.get(
        timetable_endpoint(config.host, config.port),
        params={
            "from": from_date.replace(tzinfo=None).isoformat(),
            "to": to_date.replace(tzinfo=None).isoformat(),
        },
    )
    return parse_obj_as(List[sync_models.Event], response.json())


def get_queue(key: str) -> Queue:
    return Queue.from_queue_key(key)


def map_event(event: sync_models.Event) -> stream_models.Event:
    return stream_models.Event(
        show=stream_models.Show(
            label=str(event.show.label),
            metadata={
                "title": event.show.title,
                "description": event.show.description,
            },
        ),
        start=to_utc(event.params.start),
        end=to_utc(event.params.end),
    )


def enqueue_replay(
    config: Config, event: sync_models.Event, keys: QueueKeys
) -> None:
    event = map_event(event)
    _, path = mkstemp()
    fetch_job = get_queue(keys.fetch).enqueue_at(
        to_utc(event.start) - timedelta(minutes=30),
        fetch,
        config,
        event,
        path,
        retry=ExponentialBackoffRetry(max=5, delay=60),
    )
    reserve_job = get_queue(keys.reserve).enqueue_at(
        to_utc(event.start) - timedelta(seconds=5),
        reserve,
        config,
        event,
        depends_on=[fetch_job],
        retry=ExponentialBackoffRetry(max=10, delay=1),
    )
    stream_job = get_queue(keys.stream).enqueue_at(
        to_utc(event.start),
        stream,
        config,
        event,
        path,
        depends_on=[reserve_job],
        retry=ExponentialBackoffRetry(max=5, delay=5),
    )
    get_queue(keys.cleanup).enqueue_at(
        to_utc(event.end) + timedelta(minutes=30),
        cleanup,
        config,
        event,
        path,
        depends_on=[stream_job],
        retry=ExponentialBackoffRetry(max=5, delay=60),
    )


def enqueue_sync_at(config: Config, keys: QueueKeys, dt: datetime) -> None:
    get_queue(keys.sync).enqueue_at(
        dt,
        sync,
        config,
        keys,
        retry=ExponentialBackoffRetry(max=5, delay=60),
    )


def enqueue_next_sync(config: Config, keys: QueueKeys) -> None:
    enqueue_sync_at(
        config, keys, to_utc(get_current_job().enqueued_at) + timedelta(days=1)
    )


def sync_internal(
    config: Config, keys: QueueKeys, logger: logging.Logger = get_logger()
) -> None:
    logger.info("Syncing events...")
    timetable = get_timetable(config.emishows)
    logger.info("Got timetable.")
    logger.info("Enqueueing events...")
    for event in timetable:
        if event.type == 2:
            enqueue_replay(config, event, keys)
    logger.info("Events enqueued.")
    logger.info("Enqueueing next sync...")
    enqueue_next_sync(config, keys)
    logger.info("Next sync enqueued.")


def sync(config: Config, keys: QueueKeys) -> None:
    return sync_internal(config, keys)
