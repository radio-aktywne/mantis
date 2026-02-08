from collections.abc import AsyncGenerator
from typing import Any

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import AsyncClient

from mantis.config.models import OctopusConfig
from mantis.models.base import Serializable
from mantis.services.octopus import models as m


class Endpoint(BaseEndpoint):
    """Endpoints for octopus service."""

    RESERVE = "/reserve"
    SSE = "/sse"


class BaseService(Gracy[Endpoint]):
    """Base class for octopus service."""

    def __init__(self, config: OctopusConfig, *args: Any, **kwargs: Any) -> None:
        self.Config.BASE_URL = config.http.url
        self.Config.SETTINGS = GracyConfig(
            retry=GracefulRetry(delay=1, max_attempts=3, delay_modifier=2)
        )
        super().__init__(*args, **kwargs)
        self._config = config


class ReserveNamespace(GracyNamespace[Endpoint]):
    """Namespace for octopus reserve endpoint."""

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""
        response = await self.post(
            Endpoint.RESERVE, json=Serializable(request.data).model_dump(mode="json")
        )

        return m.ReserveResponse(
            reservation=Serializable[m.ReserveResponseReservation]
            .model_validate_json(response.content)
            .root,
        )


class SSENamespace(GracyNamespace[Endpoint]):
    """Namespace for octopus sse endpoint."""

    async def _subscribe(self) -> AsyncGenerator[str]:
        url = f"{self.Config.BASE_URL}/{Endpoint.SSE}"
        client = AsyncClient(timeout=None)  # noqa: S113

        async with client as client, client.stream("GET", url) as response:
            async for data in response.aiter_lines():
                yield data.removeprefix("data: ")

    async def subscribe(self, request: m.SubscribeRequest) -> m.SubscribeResponse:
        """Get a stream of Server-Sent Events."""
        return m.SubscribeResponse(messages=self._subscribe())


class OctopusService(BaseService):
    """Service for octopus service."""

    reserve: ReserveNamespace
    sse: SSENamespace
