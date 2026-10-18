from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from http import HTTPMethod, HTTPStatus
from typing import Any

from httpx2 import AsyncClient, HTTPError, HTTPStatusError, Response

from mantis.config.models import OctopusConfig, OctopusHTTPConfig
from mantis.models.base import Jsonable, Serializable
from mantis.services.apis.octopus import errors as e, models as m


class OctopusClient:
    """Client for octopus API."""

    def __init__(self, config: OctopusHTTPConfig) -> None:
        self.config = config

    async def request(
        self,
        method: HTTPMethod,
        path: str,
        *,
        data: Any | None = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Response:
        """Make a request and return the response."""
        try:
            async with AsyncClient(base_url=self.config.url) as client:
                return await client.request(
                    method,
                    path,
                    json=data,
                    params=params,
                    headers=headers,
                )
        except HTTPError as ex:
            raise e.ServiceError from ex

    @asynccontextmanager
    async def stream(
        self,
        method: HTTPMethod,
        path: str,
        *,
        data: Any | None = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> AsyncGenerator[Response]:
        """Make a request and stream the response."""
        try:
            async with (
                AsyncClient(timeout=None, base_url=self.config.url) as client,
                client.stream(
                    method,
                    path,
                    json=data,
                    params=params,
                    headers=headers,
                ) as response,
            ):
                yield response
        except HTTPError as ex:
            raise e.ServiceError from ex


class OctopusService:
    """Service for octopus API."""

    def __init__(self, config: OctopusConfig) -> None:
        self.client = OctopusClient(config.http)

    def _dump(self, value: Serializable) -> Any:
        return value.model_dump(mode="json", round_trip=True)

    def _dump_json(self, value: Jsonable) -> str:
        return value.model_dump_json(round_trip=True)

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        data = self._dump(Serializable[m.ReserveRequestData](request.data))

        response = await self.client.request(HTTPMethod.POST, "/reserve", data=data)

        try:
            response.raise_for_status()
        except HTTPStatusError as ex:
            if ex.response.status_code == HTTPStatus.CONFLICT:
                raise e.ConflictError from ex
            raise e.ServiceError from ex

        return m.ReserveResponse(
            reservation=Serializable[m.Reservation]
            .model_validate_json(response.content)
            .root
        )

    async def subscribe(self, request: m.SubscribeRequest) -> m.SubscribeResponse:
        """Get a stream of Server-Sent Events."""
        types = self._dump_json(Jsonable[m.SubscribeRequestTypes](request.types))

        async def stream() -> AsyncGenerator[m.EventMessage]:
            async with self.client.stream(
                HTTPMethod.GET, "/sse", params={"types": types}
            ) as response:
                try:
                    response.raise_for_status()
                except HTTPStatusError as ex:
                    raise e.ServiceError from ex

                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        yield m.EventMessage()

        return m.SubscribeResponse(messages=stream())
