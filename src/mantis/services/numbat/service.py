from collections.abc import AsyncIterator
from typing import Any

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import Response

from mantis.config.models import NumbatConfig
from mantis.models.base import Jsonable, Serializable
from mantis.services.numbat import models as m


class Endpoint(BaseEndpoint):
    """Endpoints for numbat service."""

    PRERECORDINGS = "/prerecordings"


class BaseService(Gracy[Endpoint]):
    """Base class for numbat service."""

    def __init__(self, config: NumbatConfig, *args: Any, **kwargs: Any) -> None:
        self.Config.BASE_URL = config.http.url
        self.Config.SETTINGS = GracyConfig(
            retry=GracefulRetry(delay=1, max_attempts=3, delay_modifier=2)
        )
        super().__init__(*args, **kwargs)
        self._config = config


class PrerecordingsNamespace(GracyNamespace[Endpoint]):
    """Namespace for numbat prerecordings endpoint."""

    async def list(
        self, request: m.PrerecordingsListRequest
    ) -> m.PrerecordingsListResponse:
        """List prerecordings."""
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
            f"{Endpoint.PRERECORDINGS}/"
            f"{Serializable(request.event).model_dump(round_trip=True)}",
            params=params,
        )

        return m.PrerecordingsListResponse(
            results=Serializable[m.PrerecordingsListResponseResults]
            .model_validate_json(response.content)
            .root
        )

    async def download(
        self, request: m.PrerecordingsDownloadRequest
    ) -> m.PrerecordingsDownloadResponse:
        """Download a prerecording."""

        async def stream(response: Response) -> AsyncIterator[bytes]:
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()

        response = await self._client.send(
            self._client.build_request(
                "GET",
                f"{Endpoint.PRERECORDINGS}/"
                f"{Serializable(request.event).model_dump(round_trip=True)}/"
                f"{Serializable(request.start).model_dump(round_trip=True)}",
            ),
            stream=True,
        )

        return m.PrerecordingsDownloadResponse(
            type=response.headers["Content-Type"], data=stream(response)
        )


class NumbatService(BaseService):
    """Service for numbat service."""

    prerecordings: PrerecordingsNamespace
