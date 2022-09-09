import logging
from logging import Logger
from pathlib import Path
from typing import Dict, List

from pystreams.ffmpeg import FFmpegNode, FFmpegStream
from pystreams.srt import SRTNode
from pystreams.stream import Stream
from rq import get_current_job
from rq.job import Job

from emischeduler.config import config
from emischeduler.jobs.fetch import fetch_internal
from emischeduler.jobs.reserve import reserve_internal
from emischeduler.models.stream import Event, Token
from emischeduler.utils import to_utc, utcnow


def get_logger() -> Logger:
    return logging.getLogger("stream")


def output_format() -> str:
    return "opus"


def input_node(path: str) -> FFmpegNode:
    return FFmpegNode(target=path, options={"re": None})


def metadata_values(metadata: Dict[str, str]) -> List[str]:
    return [f"{key}={value}" for key, value in metadata.items()]


def output_node(event: Event, token: Token) -> FFmpegNode:
    return SRTNode(
        host=config.emistream_host,
        port=config.emistream_port,
        options={
            "acodec": "copy",
            "metadata": metadata_values(event.show.metadata | event.metadata),
            "format": output_format(),
            "passphrase": token.token,
            "pbkeylen": len(token.token),
        },
    )


def create_stream(event: Event, path: str, token: Token) -> Stream:
    return FFmpegStream(
        input=input_node(path), output=output_node(event, token)
    )


def is_fetched(path: str) -> bool:
    return Path(path).exists() and Path(path).stat().st_size > 0


def stream_internal(
    event: Event, path: str, token: Token, logger: Logger = get_logger()
) -> None:
    logger.info(f"Streaming {event.show.label}")
    if not is_fetched(path):
        logger.warning(f"File {path} not fetched!")
        logger.info(f"Re-fetching to {path}.")
        fetch_internal(event, path, logger)
    logger.info("Finding token...")
    if to_utc(token.expires_at) <= utcnow():
        logger.warning("Invalid or expired token!")
        logger.info("Re-reserving stream.")
        token = reserve_internal(event, logger)
    logger.info("Creating stream...")
    event_stream = create_stream(event, path, token)
    logger.info("Starting stream...")
    event_stream.start()
    logger.info("Streaming...")
    event_stream.wait()
    logger.info("Stream complete.")


def stream(event: Event, path: str) -> None:
    reserve_job: Job = get_current_job().fetch_dependencies()[0]
    if reserve_job.get_status() != "finished":
        raise RuntimeError("Dependent job not finished.")
    return stream_internal(event, path, reserve_job.result)
