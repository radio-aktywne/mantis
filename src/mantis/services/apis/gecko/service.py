from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from http import HTTPMethod, HTTPStatus
from typing import Any

from httpx2 import AsyncClient, HTTPError, HTTPStatusError, Response

from mantis.config.models import GeckoConfig, GeckoHTTPConfig
from mantis.models.base import Jsonable, Serializable
from mantis.services.apis.gecko import errors as e, models as m


class GeckoClient:
    """Client for gecko API."""

    def __init__(self, config: GeckoHTTPConfig) -> None:
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


class GeckoRecordingsService:
    """Service for recordings in gecko API."""

    def __init__(self, client: GeckoClient) -> None:
        self.client = client

    def _dump(self, value: Serializable) -> Any:
        return value.model_dump(mode="json", round_trip=True)

    def _dump_json(self, value: Jsonable) -> str:
        return value.model_dump_json(round_trip=True)

    async def list(self, request: m.RecordingsListRequest) -> m.RecordingsListResponse:
        """List recordings."""
        event = self._dump(Serializable[m.RecordingsListRequestEvent](request.event))
        after = self._dump_json(Jsonable[m.RecordingsListRequestAfter](request.after))
        before = self._dump_json(
            Jsonable[m.RecordingsListRequestBefore](request.before)
        )
        limit = self._dump_json(Jsonable[m.RecordingsListRequestLimit](request.limit))
        offset = self._dump_json(
            Jsonable[m.RecordingsListRequestOffset](request.offset)
        )

        response = await self.client.request(
            HTTPMethod.GET,
            f"/recordings/{event}",
            params={
                "event": event,
                "after": after,
                "before": before,
                "limit": limit,
                "offset": offset,
            },
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as ex:
            raise e.ServiceError from ex

        return m.RecordingsListResponse(
            results=Serializable[m.RecordingsListResponseResults]
            .model_validate_json(response.content)
            .root
        )

    async def download(
        self, request: m.RecordingsDownloadRequest
    ) -> m.RecordingsDownloadResponse:
        """Download a recording."""
        event = self._dump(
            Serializable[m.RecordingsDownloadRequestEvent](request.event)
        )
        start = self._dump(
            Serializable[m.RecordingsDownloadRequestStart](request.start)
        )

        response = await self.client.request(
            HTTPMethod.HEAD, f"/recordings/{event}/{start}"
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as ex:
            if ex.response.status_code == HTTPStatus.NOT_FOUND:
                raise e.NotFoundError from ex
            raise e.ServiceError from ex

        async def stream() -> AsyncGenerator[bytes]:
            async with self.client.stream(
                HTTPMethod.GET, f"/recordings/{event}/{start}"
            ) as response:
                try:
                    response.raise_for_status()
                except HTTPStatusError as ex:
                    if ex.response.status_code == HTTPStatus.NOT_FOUND:
                        raise e.NotFoundError from ex
                    raise e.ServiceError from ex

                async for chunk in response.aiter_bytes():
                    yield chunk

        return m.RecordingsDownloadResponse(
            type=Serializable[m.RecordingsDownloadResponseType]
            .model_validate(response.headers["Content-Type"])
            .root,
            data=stream(),
        )


class GeckoService:
    """Service for gecko API."""

    def __init__(self, config: GeckoConfig) -> None:
        self.client = GeckoClient(config.http)

    @property
    def recordings(self) -> GeckoRecordingsService:
        """Service for recordings in gecko API."""
        return GeckoRecordingsService(self.client)
