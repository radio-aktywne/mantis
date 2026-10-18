from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from http import HTTPMethod, HTTPStatus
from typing import Any

from httpx2 import AsyncClient, HTTPError, HTTPStatusError, Response

from mantis.config.models import NumbatConfig, NumbatHTTPConfig
from mantis.models.base import Jsonable, Serializable
from mantis.services.apis.numbat import errors as e, models as m


class NumbatClient:
    """Client for numbat API."""

    def __init__(self, config: NumbatHTTPConfig) -> None:
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


class NumbatPrerecordingsService:
    """Service for prerecordings in numbat API."""

    def __init__(self, client: NumbatClient) -> None:
        self.client = client

    def _dump(self, value: Serializable) -> Any:
        return value.model_dump(mode="json", round_trip=True)

    def _dump_json(self, value: Jsonable) -> str:
        return value.model_dump_json(round_trip=True)

    async def download(
        self, request: m.PrerecordingsDownloadRequest
    ) -> m.PrerecordingsDownloadResponse:
        """Download a prerecording."""
        event = self._dump(
            Serializable[m.PrerecordingsDownloadRequestEvent](request.event)
        )
        start = self._dump(
            Serializable[m.PrerecordingsDownloadRequestStart](request.start)
        )

        response = await self.client.request(
            HTTPMethod.HEAD, f"/prerecordings/{event}/{start}"
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as ex:
            if ex.response.status_code == HTTPStatus.NOT_FOUND:
                raise e.NotFoundError from ex
            raise e.ServiceError from ex

        async def stream() -> AsyncGenerator[bytes]:
            async with self.client.stream(
                HTTPMethod.GET, f"/prerecordings/{event}/{start}"
            ) as response:
                try:
                    response.raise_for_status()
                except HTTPStatusError as ex:
                    if ex.response.status_code == HTTPStatus.NOT_FOUND:
                        raise e.NotFoundError from ex
                    raise e.ServiceError from ex

                async for chunk in response.aiter_bytes():
                    yield chunk

        return m.PrerecordingsDownloadResponse(
            type=Serializable[m.PrerecordingsDownloadResponseType]
            .model_validate(response.headers["Content-Type"])
            .root,
            data=stream(),
        )


class NumbatService:
    """Service for numbat API."""

    def __init__(self, config: NumbatConfig) -> None:
        self.client = NumbatClient(config.http)

    @property
    def prerecordings(self) -> NumbatPrerecordingsService:
        """Service for prerecordings in numbat API."""
        return NumbatPrerecordingsService(self.client)
