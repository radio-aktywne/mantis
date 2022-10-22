import logging
from pathlib import Path
from typing import Dict, List

from pystreams.ffmpeg import FFmpegNode, FFmpegStream
from rocketry import Session
from rocketry.args import Arg, Session as SessionArg

from emischeduler.models.utils import map_event
from emischeduler.scheduler.tasks.fetch import fetch
from emischeduler.scheduler.tasks.reserve import reserve
from emischeduler.shows.models.data import Event
from emischeduler.stream.client import StreamClient
from emischeduler.stream.models.data import Token
from emischeduler.time import to_utc, utcnow
from emischeduler.utils import background

logger = logging.getLogger(__name__)


def is_fetched(path: Path) -> bool:
    return Path(path).exists() and Path(path).stat().st_size > 0


def is_expired(token: Token) -> bool:
    return to_utc(token.expires_at) <= utcnow()


def map_metadata(metadata: Dict[str, str]) -> List[str]:
    return [f"{key}={value}" for key, value in metadata.items()]


def __stream(s: FFmpegStream) -> None:
    s.start()
    s.wait()


async def _stream(
    event: Event, token: Token, path: Path, client: StreamClient
) -> None:
    event = map_event(event)
    input = FFmpegNode(target=str(path), options={"re": None})
    options = {
        "metadata": map_metadata(event.show.metadata | event.metadata),
        "passphrase": token.token,
        "pbkeylen": len(token.token),
    }
    output = client.get_stream_node(**options)
    await background(__stream, FFmpegStream(input, output))


async def stream(
    event: Event,
    path: str | Path,
    reservation_task_name: str,
    client: StreamClient = Arg("stream"),
    session: Session = SessionArg(),
) -> None:
    path = Path(path)

    logger.info(f"Starting stream for {event.show.label}...")

    reservation_task = session[reservation_task_name]
    token = session.returns[reservation_task]

    if not is_fetched(path):
        logger.warning(
            f"Stream for {event.show.label} not fetched, fetching..."
        )
        await fetch(
            event,
            path,
            session.parameters["archive"],
            session.parameters["config"],
        )
        logger.info(f"Stream for {event.show.label} fetched.")

    if is_expired(token):
        logger.warning(
            f"Stream for {event.show.label} token expired, renewing..."
        )
        token = await reserve(event, client)
        logger.info(f"Stream for {event.show.label} renewed.")

    logger.info(f"Streaming {event.show.label}...")
    await _stream(event, token, path, client)
    logger.info(f"Stream for {event.show.label} ended.")
