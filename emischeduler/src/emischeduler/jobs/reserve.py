import asyncio
import json
import logging
from logging import Logger

import httpx
from rq.job import Job, get_current_job
from websockets import connect

from emischeduler.config import config
from emischeduler.models.stream import (
    Availability,
    AvailableNotification,
    AvailableResponse,
    Event,
    ReserveRequest,
    ReserveResponse,
    Token,
)


def get_logger() -> Logger:
    return logging.getLogger("reserve")


def emistream_http_url() -> str:
    return f"http://{config.emistream_host}:{config.emistream_port}"


def emistream_ws_url() -> str:
    return f"ws://{config.emistream_host}:{config.emistream_port}"


def available_endpoint() -> str:
    return f"{emistream_http_url()}/available"


def notify_endpoint() -> str:
    return f"{emistream_ws_url()}/available/notify"


def reserve_endpoint() -> str:
    return f"{emistream_http_url()}/reserve"


def get_availability() -> Availability:
    response = httpx.get(available_endpoint())
    response.raise_for_status()
    return AvailableResponse(**response.json()).availability


def wait_for_availability() -> None:
    async def wait():
        async with connect(notify_endpoint()) as websocket:
            while True:
                msg = await websocket.recv()
                notification = AvailableNotification(**json.loads(msg))
                if notification.availability.available:
                    return

    asyncio.run(wait())


def make_reservation(event: Event) -> Token:
    request = ReserveRequest(
        event=event,
        record=False,
    )
    response = httpx.post(reserve_endpoint(), json=json.loads(request.json()))
    response.raise_for_status()
    return ReserveResponse(**response.json()).token


def reserve_internal(event: Event, logger: Logger = get_logger()) -> Token:
    logger.info(f"Reserving stream for {event.show.label}...")
    logger.info(f"Checking availability...")
    if not get_availability().available:
        logger.info(f"Not available!")
        logger.info(f"Waiting for availability...")
        wait_for_availability()
    logger.info(f"Stream available!")
    logger.info(f"Making reservation...")
    token = make_reservation(event)
    logger.info(f"Reservation complete. Expires at {token.expires_at}.")
    return token


def reserve(event: Event) -> Token:
    fetch_job: Job = get_current_job().fetch_dependencies()[0]
    if fetch_job.get_status() != "finished":
        raise RuntimeError("Dependent job not finished.")
    return reserve_internal(event)
