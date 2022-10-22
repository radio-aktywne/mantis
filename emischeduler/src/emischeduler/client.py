import json
from typing import Dict, Any, AsyncIterable

import httpx
from pystreams.srt import SRTNode
from websockets import connect


class HttpClient:
    def __init__(
        self, host: str, port: int, secure: bool = False, **kwargs
    ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._secure = secure
        self._kwargs = kwargs

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def secure(self) -> bool:
        return self._secure

    @property
    def base_url(self) -> str:
        return f"http{'s' if self.secure else ''}://{self.host}:{self.port}"

    def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(**self._kwargs)

    async def get(self, endpoint: str, *args, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        async with self._get_client() as client:
            response = await client.get(url, *args, **kwargs)
        response.raise_for_status()
        return response.json()

    async def post(
        self, endpoint: str, data: Dict[str, Any], *args, **kwargs
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        async with self._get_client() as client:
            response = await client.post(url, json=data, *args, **kwargs)
        response.raise_for_status()
        return response.json()


class WebsocketClient:
    def __init__(
        self,
        host: str,
        port: int,
        secure: bool = False,
        **kwargs,
    ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._secure = secure
        self._kwargs = kwargs

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def secure(self) -> bool:
        return self._secure

    @property
    def base_url(self) -> str:
        return f"ws{'s' if self.secure else ''}://{self.host}:{self.port}"

    def _get_websocket(self, url: str) -> connect:
        return connect(url, **self._kwargs)

    async def stream(self, endpoint: str) -> AsyncIterable[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        async with self._get_websocket(url) as ws:
            async for message in ws:
                yield json.loads(message)


class SrtClient:
    def __init__(
        self,
        host: str,
        port: int,
        **kwargs,
    ) -> None:
        super().__init__()
        self._host = host
        self._port = port
        self._kwargs = kwargs

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def base_url(self) -> str:
        return f"srt://{self.host}:{self.port}"

    def get_node(self, **kwargs) -> SRTNode:
        options = self._kwargs | kwargs
        return SRTNode(host=self._host, port=str(self._port), options=options)
