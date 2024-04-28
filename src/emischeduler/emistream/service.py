from collections.abc import AsyncGenerator

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import AsyncClient

from emischeduler.config.models import EmistreamHTTPConfig
from emischeduler.emistream.models import (
    Availability,
    Event,
    ParsableEvent,
    ReserveRequest,
    ReserveResponse,
)


class EmistreamEndpoint(BaseEndpoint):
    """Endpoints for the emistream API."""

    CHECK = "/check"
    RESERVE = "/reserve"
    SSE = "/sse"


class EmistreamServiceBase(Gracy[EmistreamEndpoint]):
    """Base class for emistream API service."""

    def __init__(self, config: EmistreamHTTPConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = config.url
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


class EmistreamCheckNamespace(GracyNamespace[EmistreamEndpoint]):
    """Namespace for emistream API check endpoint."""

    async def check(self) -> Availability:
        response = await self.get(EmistreamEndpoint.CHECK)
        return Availability.model_validate_json(response.content)


class EmistreamReserveNamespace(GracyNamespace[EmistreamEndpoint]):
    """Namespace for emistream API reserve endpoint."""

    async def reserve(self, request: ReserveRequest) -> ReserveResponse:
        response = await self.post(
            EmistreamEndpoint.RESERVE,
            json=request.model_dump(mode="json", by_alias=True),
        )
        return ReserveResponse.model_validate_json(response.content)


class EmistreamSSENamespace(GracyNamespace[EmistreamEndpoint]):
    """Namespace for emistream API sse endpoint."""

    async def subscribe(self) -> AsyncGenerator[Event, None]:
        url = f"{self.Config.BASE_URL}/{EmistreamEndpoint.SSE}"
        async with AsyncClient(timeout=None) as client:
            async with client.stream("GET", url) as response:
                async for event in response.aiter_lines():
                    event = event.removeprefix("data: ")
                    event = ParsableEvent.model_validate_json(event)
                    yield event.root


class EmistreamService(EmistreamServiceBase):
    """Service for emistream API."""

    check: EmistreamCheckNamespace
    reserve: EmistreamReserveNamespace
    sse: EmistreamSSENamespace
