from collections.abc import AsyncGenerator

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import AsyncClient

from mantis.config.models import OctopusConfig
from mantis.services.octopus import models as m


class Endpoint(BaseEndpoint):
    """Endpoints for octopus service."""

    CHECK = "/check"
    RESERVE = "/reserve"
    SSE = "/sse"


class BaseService(Gracy[Endpoint]):
    """Base class for octopus service."""

    def __init__(self, config: OctopusConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = config.http.url
            SETTINGS = GracyConfig(
                retry=GracefulRetry(
                    delay=1,
                    max_attempts=3,
                    delay_modifier=2,
                ),
            )

        self.Config = Config

        super().__init__(*args, **kwargs)

        self._config = config


class CheckNamespace(GracyNamespace[Endpoint]):
    """Namespace for octopus check endpoint."""

    async def check(self, request: m.CheckRequest) -> m.CheckResponse:
        """Check the availability of the stream."""

        res = await self.get(Endpoint.CHECK)

        availability = m.Availability.model_validate_json(res.content)

        return m.CheckResponse(
            availability=availability,
        )


class ReserveNamespace(GracyNamespace[Endpoint]):
    """Namespace for octopus reserve endpoint."""

    async def reserve(self, request: m.ReserveRequest) -> m.ReserveResponse:
        """Reserve a stream."""

        data = request.data

        json = data.model_dump(mode="json", by_alias=True)

        res = await self.post(
            Endpoint.RESERVE,
            json=json,
        )

        data = m.ReserveResponseData.model_validate_json(res.content)

        return m.ReserveResponse(
            data=data,
        )


class SSENamespace(GracyNamespace[Endpoint]):
    """Namespace for octopus sse endpoint."""

    def _parse_event(self, data: str) -> m.Event:
        data = data.removeprefix("data: ")
        event = m.ParsableEvent.model_validate_json(data)
        return event.root

    async def _subscribe(self) -> AsyncGenerator[m.Event]:
        url = f"{self.Config.BASE_URL}/{Endpoint.SSE}"
        client = AsyncClient(timeout=None)

        async with client as client:
            async with client.stream("GET", url) as res:
                async for data in res.aiter_lines():
                    yield self._parse_event(data)

    async def subscribe(self, request: m.SubscribeRequest) -> m.SubscribeResponse:
        """Get a stream of Server-Sent Events."""

        events = self._subscribe()

        return m.SubscribeResponse(
            events=events,
        )


class OctopusService(BaseService):
    """Service for octopus service."""

    check: CheckNamespace
    reserve: ReserveNamespace
    sse: SSENamespace
