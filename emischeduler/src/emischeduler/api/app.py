from rocketry import Rocketry
from starlite import State, Starlite, WebSocketException, CORSConfig

from emischeduler.api.paths.router import router
from emischeduler.config import Config


def build(config: Config, scheduler: Rocketry) -> Starlite:
    async def setup(state: State) -> None:
        state.scheduler = scheduler
        state.sockets = {}

    async def cleanup(state: State) -> None:
        for uid, socket in state.sockets.items():
            try:
                await socket.close()
            except (ConnectionError, WebSocketException):
                pass
            state.sockets.pop(uid, None)

    return Starlite(
        route_handlers=[router],
        cors_config=CORSConfig(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        on_startup=[setup],
        on_shutdown=[cleanup],
    )
