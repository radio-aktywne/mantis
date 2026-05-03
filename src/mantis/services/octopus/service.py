from collections.abc import AsyncGenerator
from typing import Any, Never, override

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import Response

from mantis.config.models import OctopusConfig
from mantis.models.base import Jsonable, Serializable
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
            Endpoint.RESERVE,
            json=Serializable(request.data).model_dump(mode="json", round_trip=True),
        )

        return m.ReserveResponse(
            reservation=Serializable[m.ReserveResponseReservation]
            .model_validate_json(response.content)
            .root,
        )


class SSENamespace(GracyNamespace[Endpoint]):
    """Namespace for octopus sse endpoint."""

    async def subscribe(self, request: m.SubscribeRequest) -> m.SubscribeResponse:
        """Get a stream of Server-Sent Events."""

        class Stream(AsyncGenerator[m.EventMessage]):
            def __init__(self, response: Response) -> None:
                self.response = response
                self.iterator = response.aiter_lines()

            @override
            async def asend(self, *args: Any, **kwargs: Any) -> m.EventMessage:
                try:
                    while True:
                        data = await anext(self.iterator)
                        if data.startswith("data:"):
                            return m.EventMessage()
                except:
                    await self.response.aclose()
                    raise

            @override
            async def athrow(self, *args: Any, **kwargs: Any) -> Never:
                await self.response.aclose()
                raise StopAsyncIteration

        params = {}
        if request.types is not None:
            params["types"] = Jsonable(request.types).model_dump_json(round_trip=True)

        response = await self._client.send(
            self._client.build_request(
                "GET", Endpoint.SSE, params=params, timeout=None
            ),
            stream=True,
        )

        return m.SubscribeResponse(messages=Stream(response))


class OctopusService(BaseService):
    """Service for octopus service."""

    reserve: ReserveNamespace
    sse: SSENamespace
