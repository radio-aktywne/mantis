from typing import AsyncIterable, Dict, Optional, Any

from pystreams.ffmpeg import FFmpegNode

from emischeduler.client import (
    HttpClient,
    SrtClient,
    WebsocketClient,
)
from emischeduler.stream.models.api import (
    ReserveRequest,
    ReserveResponse,
    AvailableResponse,
    AvailableStreamResponse,
)
from emischeduler.stream.models.data import Event, Token, Availability


class RawStreamClient:
    def __init__(
        self,
        host: str,
        port: int,
        secure: bool = False,
        http_kwargs: Optional[Dict[str, Any]] = None,
        ws_kwargs: Optional[Dict[str, Any]] = None,
        srt_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._http_client = HttpClient(
            host, port, secure, **(http_kwargs or {})
        )
        self._ws_client = WebsocketClient(
            host, port, secure, **(ws_kwargs or {})
        )
        self._srt_client = SrtClient(host, port, **(srt_kwargs or {}))

    async def reserve(self, request: ReserveRequest) -> ReserveResponse:
        response = await self._http_client.post("reserve", request.json_dict())
        return ReserveResponse(**response)

    async def available(self) -> AvailableResponse:
        response = await self._http_client.get("available")
        return AvailableResponse(**response)

    async def watch_available(
        self,
    ) -> AsyncIterable[AvailableStreamResponse]:
        async for message in self._ws_client.stream("available/watch"):
            yield AvailableStreamResponse(**message)

    def get_stream_node(self, **kwargs) -> FFmpegNode:
        options = {"acodec": "copy", "format": "opus"}
        return self._srt_client.get_node(**(options | kwargs))


class StreamClient:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._client = RawStreamClient(*args, **kwargs)

    async def reserve(self, event: Event, record: bool = False) -> Token:
        request = ReserveRequest(event=event, record=record)
        response = await self._client.reserve(request)
        return response.token

    async def available(self) -> Availability:
        response = await self._client.available()
        return response.availability

    async def watch_available(self) -> AsyncIterable[Availability]:
        async for response in self._client.watch_available():
            yield response.availability

    def get_stream_node(self, **kwargs) -> FFmpegNode:
        return self._client.get_stream_node(**kwargs)
