import logging
from logging import Logger

from minio import Minio

from emischeduler.config import config
from emischeduler.models.sync import Event


def get_logger() -> Logger:
    return logging.getLogger("fetch")


def get_minio() -> Minio:
    return Minio(
        endpoint=f"{config.emiarchive_host}:{config.emiarchive_port}",
        access_key=config.emiarchive_username,
        secret_key=config.emiarchive_password,
        secure=False,
    )


def get_recordings_bucket() -> str:
    return "recordings"


def get_recording_path(client: Minio, event: Event) -> str:
    objects = client.list_objects(
        get_recordings_bucket(), prefix=f"{event.id}/"
    )
    latest = max(
        [o for o in objects if not o.is_dir], key=lambda o: o.last_modified
    )
    return latest.object_name


def fetch_internal(
    event: Event, path: str, logger: Logger = get_logger()
) -> None:
    logger.info(f"Fetching stream file for {event.id}...")
    logger.info("Getting Minio client...")
    client = get_minio()
    logger.info("Resolving bucket...")
    bucket = get_recordings_bucket()
    logger.info("Resolving path...")
    recording_path = get_recording_path(client, event)
    logger.info(f"Downloading file {bucket}/{recording_path} to {path}...")
    client.fget_object(bucket, recording_path, path)
    logger.info("Fetch complete.")


def fetch(event: Event, path: str) -> None:
    return fetch_internal(event, path)
