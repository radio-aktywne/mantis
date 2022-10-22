import asyncio

from rocketry import Rocketry
from starlite import Controller, State, get, WebSocket

from emischeduler.api.paths.status.models import (
    StatusResponse,
    StatusStreamResponse,
)
from emischeduler.api.socket import websocket


class StatusController(Controller):
    path = None

    @get()
    async def status(self, state: State) -> StatusResponse:
        scheduler: Rocketry = state.scheduler
        return StatusResponse(alive=scheduler.session.scheduler.is_alive)

    @websocket("/watch")
    async def watch_status(self, state: State, socket: WebSocket) -> None:
        scheduler: Rocketry = state.scheduler

        while True:
            response = StatusStreamResponse(
                alive=scheduler.session.scheduler.is_alive
            )
            await socket.send_json(response.json_dict())
            await asyncio.sleep(5)
