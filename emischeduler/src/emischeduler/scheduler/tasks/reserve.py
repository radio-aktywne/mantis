import logging

from rocketry.args import Arg

from emischeduler.models.utils import map_event
from emischeduler.shows.models.data import Event
from emischeduler.stream.client import StreamClient
from emischeduler.stream.models.data import Token
from emischeduler.time import stringify

logger = logging.getLogger(__name__)


async def reserve(event: Event, client: StreamClient = Arg("stream")) -> Token:
    logger.info(f"Reserving stream for {event.show.label}...")
    stream_event = map_event(event)
    token = await client.reserve(stream_event)
    logger.info(f"Stream reserved until {stringify(token.expires_at)}.")
    return token
