import logging
from logging import Logger
from pathlib import Path

from rq.job import Job, get_current_job

from emischeduler.models.stream import Event


def get_logger() -> Logger:
    return logging.getLogger("cleanup")


def cleanup_internal(
    event: Event, path: str, logger: Logger = get_logger()
) -> None:
    logger.info(f"Cleaning up after {event.show.label}...")
    logger.info(f"Deleting stream file {path}...")
    Path(path).unlink(missing_ok=True)
    logger.info("Cleanup complete.")


def cleanup(event: Event, path: str) -> None:
    stream_job: Job = get_current_job().fetch_dependencies()[0]
    if stream_job.get_status() != "finished":
        raise RuntimeError("Dependent job not finished.")
    return cleanup_internal(event, path)
