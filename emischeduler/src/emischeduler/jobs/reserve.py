import asyncio
import json
import logging

import httpx
from rq.job import Job, get_current_job
from websockets import connect

from emischeduler.config.models import EmistreamConfig, Config
from emischeduler.models.stream import (
    Availability,
    AvailableNotification,
    AvailableResponse,
    Event,
    ReserveRequest,
    ReserveResponse,
    Token,
)


def get_logger() -> logging.Logger:
    return logging.getLogger("reserve")


def emistream_http_url(host: str, port: int) -> str:
    return f"http://{host}:{port}"


def emistream_ws_url(host: str, port: int) -> str:
    return f"ws://{host}:{port}"


def available_endpoint(host: str, port: int) -> str:
    return f"{emistream_http_url(host, port)}/available"


def notify_endpoint(host: str, port: int) -> str:
    return f"{emistream_ws_url(host, port)}/available/notify"


def reserve_endpoint(host: str, port: int) -> str:
    return f"{emistream_http_url(host, port)}/reserve"


def get_availability(config: EmistreamConfig) -> Availability:
    response = httpx.get(available_endpoint(config.host, config.port))
    response.raise_for_status()
    return AvailableResponse(**response.json()).availability


def wait_for_availability(config: EmistreamConfig) -> None:
    async def wait():
        endpoint = notify_endpoint(config.host, config.port)
        async with connect(endpoint) as websocket:
            while True:
                msg = await websocket.recv()
                notification = AvailableNotification(**json.loads(msg))
                if notification.availability.available:
                    return

    asyncio.run(wait())


def make_reservation(config: EmistreamConfig, event: Event) -> Token:
    endpoint = reserve_endpoint(config.host, config.port)
    request = ReserveRequest(event=event, record=False)
    response = httpx.post(endpoint, json=json.loads(request.json()))
    response.raise_for_status()
    return ReserveResponse(**response.json()).token


def reserve_internal(
    config: Config, event: Event, logger: logging.Logger = get_logger()
) -> Token:
    logger.info(f"Reserving stream for {event.show.label}...")
    logger.info(f"Checking availability...")
    if not get_availability(config.emistream).available:
        logger.info(f"Not available!")
        logger.info(f"Waiting for availability...")
        wait_for_availability(config.emistream)
    logger.info(f"Stream available!")
    logger.info(f"Making reservation...")
    token = make_reservation(config.emistream, event)
    logger.info(f"Reservation complete. Expires at {token.expires_at}.")
    return token


def reserve(config: Config, event: Event) -> Token:
    fetch_job: Job = get_current_job().fetch_dependencies()[0]
    if fetch_job.get_status() != "finished":
        raise RuntimeError("Dependent job not finished.")
    return reserve_internal(config, event)
