from collections.abc import AsyncIterator
from typing import Any

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import Response

from mantis.config.models import NumbatConfig
from mantis.services.numbat import models as m
from mantis.services.numbat.serializer import Serializer
from mantis.utils.time import httpparse


class Endpoint(BaseEndpoint):
    """Endpoints for numbat service."""

    PRERECORDINGS = "/prerecordings"


class BaseService(Gracy[Endpoint]):
    """Base class for numbat service."""

    def __init__(self, config: NumbatConfig, *args: Any, **kwargs: Any) -> None:
        self.Config.BASE_URL = config.http.url
        self.Config.SETTINGS = GracyConfig(
            retry=GracefulRetry(
                delay=1,
                max_attempts=3,
                delay_modifier=2,
            ),
        )
        super().__init__(*args, **kwargs)
        self._config = config


class PrerecordingsNamespace(GracyNamespace[Endpoint]):
    """Namespace for numbat prerecordings endpoint."""

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List prerecordings."""
        event = request.event
        after = request.after
        before = request.before
        limit = request.limit
        offset = request.offset
        order = request.order

        url = f"{Endpoint.PRERECORDINGS}/{event}"

        params = {}
        if after is not None:
            params["after"] = Serializer[m.ListRequestAfter].serialize(after)
        if before is not None:
            params["before"] = Serializer[m.ListRequestBefore].serialize(before)
        if limit is not None:
            params["limit"] = Serializer[m.ListRequestLimit].serialize(limit)
        if offset is not None:
            params["offset"] = Serializer[m.ListRequestOffset].serialize(offset)
        if order is not None:
            params["order"] = Serializer[m.ListRequestOrder].serialize(order)

        res = await self.get(url, params=params)

        results = m.PrerecordingList.model_validate_json(res.content)

        return m.ListResponse(
            results=results,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download prerecording."""

        async def _stream(response: Response) -> AsyncIterator[bytes]:
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()

        event = request.event
        start = request.start

        start = Serializer[m.DownloadRequestStart].serialize(start)

        url = f"{Endpoint.PRERECORDINGS}/{event}/{start}"

        req = self._client.build_request("GET", url)
        res = await self._client.send(req, stream=True)

        headers = res.headers

        content_type = headers.get("Content-Type")
        size = int(headers.get("Content-Length"))
        tag = headers.get("ETag")
        modified = httpparse(headers.get("Last-Modified"))
        data = _stream(res)

        return m.DownloadResponse(
            type=content_type,
            size=size,
            tag=tag,
            modified=modified,
            data=data,
        )


class NumbatService(BaseService):
    """Service for numbat service."""

    prerecordings: PrerecordingsNamespace
