import inspect
from uuid import uuid4

from starlite import WebSocket, WebsocketRouteHandler, State
from starlite.types import AsyncAnyCallable
from websockets.exceptions import WebSocketException


class CustomWebsocketRouteHandler(WebsocketRouteHandler):
    def __call__(self, fn: AsyncAnyCallable) -> "WebsocketRouteHandler":
        async def wrapper(*args, state: State, socket: WebSocket, **kwargs):
            uid = uuid4()
            state.sockets[uid] = socket
            await socket.accept()
            try:
                return await fn(*args, state=state, socket=socket, **kwargs)
            except (ConnectionError, WebSocketException, RuntimeError):
                pass
            finally:
                try:
                    await socket.close()
                except (ConnectionError, WebSocketException, RuntimeError):
                    pass
                state.sockets.pop(uid, None)

        wrapper.__signature__ = inspect.signature(fn)
        return super().__call__(wrapper)


websocket = CustomWebsocketRouteHandler
