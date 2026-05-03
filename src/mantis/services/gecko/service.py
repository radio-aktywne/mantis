from collections.abc import AsyncGenerator
from typing import Any, Never, override

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import Response

from mantis.config.models import GeckoConfig
from mantis.models.base import Jsonable, Serializable
from mantis.services.gecko import models as m
from mantis.utils.mime import MimeType


class Endpoint(BaseEndpoint):
    """Endpoints for gecko service."""

    RECORDINGS = "/recordings"


class BaseService(Gracy[Endpoint]):
    """Base class for gecko service."""

    def __init__(self, config: GeckoConfig, *args: Any, **kwargs: Any) -> None:
        self.Config.BASE_URL = config.http.url
        self.Config.SETTINGS = GracyConfig(
            retry=GracefulRetry(delay=1, max_attempts=3, delay_modifier=2)
        )
        super().__init__(*args, **kwargs)
        self._config = config


class RecordingsNamespace(GracyNamespace[Endpoint]):
    """Namespace for gecko recordings endpoint."""

    async def list(self, request: m.RecordingsListRequest) -> m.RecordingsListResponse:
        """List recordings."""
        params = {}
        if request.after is not None:
            params["after"] = Jsonable(request.after).model_dump_json(round_trip=True)
        if request.before is not None:
            params["before"] = Jsonable(request.before).model_dump_json(round_trip=True)
        if request.limit is not None:
            params["limit"] = Jsonable(request.limit).model_dump_json(round_trip=True)
        if request.offset is not None:
            params["offset"] = Jsonable(request.offset).model_dump_json(round_trip=True)

        response = await self.get(
            f"{Endpoint.RECORDINGS}/"
            f"{Serializable(request.event).model_dump(round_trip=True)}",
            params=params,
        )

        return m.RecordingsListResponse(
            results=Serializable[m.RecordingsListResponseResults]
            .model_validate_json(response.content)
            .root
        )

    async def download(
        self, request: m.RecordingsDownloadRequest
    ) -> m.RecordingsDownloadResponse:
        """Download a recording."""

        class Stream(AsyncGenerator[bytes]):
            def __init__(self, response: Response) -> None:
                self.response = response
                self.iterator = response.aiter_bytes()

            @override
            async def asend(self, *args: Any, **kwargs: Any) -> bytes:
                try:
                    return await anext(self.iterator)
                except:
                    await self.response.aclose()
                    raise

            @override
            async def athrow(self, *args: Any, **kwargs: Any) -> Never:
                await self.response.aclose()
                raise StopAsyncIteration

        response = await self._client.send(
            self._client.build_request(
                "GET",
                f"{Endpoint.RECORDINGS}/"
                f"{Serializable(request.event).model_dump(round_trip=True)}/"
                f"{Serializable(request.start).model_dump(round_trip=True)}",
            ),
            stream=True,
        )

        return m.RecordingsDownloadResponse(
            type=MimeType.parse(response.headers["Content-Type"]), data=Stream(response)
        )


class GeckoService(BaseService):
    """Service for gecko service."""

    recordings: RecordingsNamespace
