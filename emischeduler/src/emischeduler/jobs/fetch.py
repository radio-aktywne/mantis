import logging

from minio import Minio

from emischeduler.config.models import EmiarchiveConfig, Config
from emischeduler.models.stream import Event


def get_logger() -> logging.Logger:
    return logging.getLogger("fetch")


def get_minio(config: EmiarchiveConfig) -> Minio:
    return Minio(
        endpoint=f"{config.host}:{config.port}",
        access_key=config.username,
        secret_key=config.password,
        secure=False,
    )


def get_recordings_bucket() -> str:
    return "recordings"


def get_recording_path(client: Minio, event: Event) -> str:
    objects = client.list_objects(
        get_recordings_bucket(), prefix=f"{event.show.label}/"
    )
    latest = max(
        [o for o in objects if not o.is_dir], key=lambda o: o.last_modified
    )
    return latest.object_name


def fetch_internal(
    config: Config,
    event: Event,
    path: str,
    logger: logging.Logger = get_logger(),
) -> None:
    logger.info(f"Fetching stream file for {event.show.label}...")
    logger.info("Getting Minio client...")
    client = get_minio(config.emiarchive)
    logger.info("Resolving bucket...")
    bucket = get_recordings_bucket()
    logger.info("Resolving path...")
    recording_path = get_recording_path(client, event)
    logger.info(f"Downloading file {bucket}/{recording_path} to {path}...")
    client.fget_object(bucket, recording_path, path)
    logger.info("Fetch complete.")


def fetch(config: Config, event: Event, path: str) -> None:
    return fetch_internal(config, event, path)
