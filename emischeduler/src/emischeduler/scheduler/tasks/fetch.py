import logging
from pathlib import Path
from typing import Tuple

from rocketry.args import Arg

from emischeduler.archive.client import ArchiveClient
from emischeduler.config import Config
from emischeduler.shows.models.data import Event
from emischeduler.time import stringify

logger = logging.getLogger(__name__)


FORMAT = "opus"


async def get_replay_key(
    bucket: str, event: Event, client: ArchiveClient
) -> str:
    objects = await client.list(bucket, prefix=f"{event.show.label}/")
    latest = max(objects, key=lambda o: o.last_modified)
    return latest.object_name


async def get_pre_recorded_key(
    bucket: str, event: Event, client: ArchiveClient
) -> str:
    return f"{event.show.label}/{stringify(event.params.start)}.{FORMAT}"


async def get_bucket_and_key(
    event: Event, client: ArchiveClient, config: Config
) -> Tuple[str, str]:
    if event.type == 1:
        raise ValueError("Cannot fetch live event.")
    if event.type == 2:
        bucket = config.live_recordings_bucket
        return bucket, await get_replay_key(bucket, event, client)
    elif event.type == 3:
        bucket = config.pre_recorded_bucket
        return bucket, await get_pre_recorded_key(bucket, event, client)
    else:
        raise ValueError(f"Unknown event type {event.type}")


async def fetch(
    event: Event,
    path: str | Path,
    client: ArchiveClient = Arg("archive"),
    config: Config = Arg("config"),
) -> None:
    path = Path(path)

    logger.info(f"Fetching file for {event.show.label} to {path}...")

    try:
        logger.info(f"Resolving bucket and key...")
        bucket, key = await get_bucket_and_key(event, client, config)
        logger.info(f"Resolved bucket to: {bucket}, and key to: {key}")
    except ValueError as e:
        logger.error(f"Could not resolve for {event.show.label}: {e}")
        raise e

    logger.info(f"Downloading file {bucket}/{key} to {path}...")
    await client.download(bucket, key, path)
    logger.info(f"File downloaded.")
