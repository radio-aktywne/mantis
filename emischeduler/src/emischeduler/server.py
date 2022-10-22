import asyncio
from signal import Signals
from types import FrameType

import uvicorn
from rocketry import Rocketry
from starlite import Starlite
from uvicorn import Server

from emischeduler.config import Config


class CustomServer(Server):
    def __init__(self, scheduler: Rocketry, config: Config) -> None:
        super().__init__(config)
        self._scheduler = scheduler

    def handle_exit(self, sig: Signals, frame: FrameType) -> None:
        self._scheduler.session.shut_down()
        return super().handle_exit(sig, frame)


async def _run(scheduler: Rocketry, server: CustomServer) -> None:
    server_task = asyncio.create_task(server.serve())
    scheduler_task = asyncio.create_task(scheduler.serve())

    await asyncio.wait([server_task, scheduler_task])


def run(scheduler: Rocketry, api: Starlite, config: Config) -> None:
    cfg = uvicorn.Config(api, host=config.api.host, port=config.api.port)
    server = CustomServer(scheduler, cfg)

    asyncio.run(_run(scheduler, server))
