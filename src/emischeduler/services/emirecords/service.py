from collections.abc import AsyncIterator

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from httpx import Response

from emischeduler.config.models import EmirecordsConfig
from emischeduler.services.emirecords import models as m
from emischeduler.services.emirecords.serializer import Serializer
from emischeduler.utils.time import httpparse


class Endpoint(BaseEndpoint):
    """Endpoints for emirecords service."""

    RECORDS = "/records"


class BaseService(Gracy[Endpoint]):
    """Base class for emirecords service."""

    def __init__(self, config: EmirecordsConfig, *args, **kwargs) -> None:
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


class RecordsNamespace(GracyNamespace[Endpoint]):
    """Namespace for emirecords records endpoint."""

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List records."""

        event = request.event
        after = request.after
        before = request.before
        limit = request.limit
        offset = request.offset
        order = request.order

        url = f"{Endpoint.RECORDS}/{event}"

        params = {}
        if after is not None:
            params["after"] = Serializer(m.ListRequestAfter).json(after)
        if before is not None:
            params["before"] = Serializer(m.ListRequestBefore).json(before)
        if limit is not None:
            params["limit"] = Serializer(m.ListRequestLimit).json(limit)
        if offset is not None:
            params["offset"] = Serializer(m.ListRequestOffset).json(offset)
        if order is not None:
            params["order"] = Serializer(m.ListRequestOrder).json(order)

        res = await self.get(url, params=params)

        results = m.RecordList.model_validate_json(res.content)

        return m.ListResponse(
            results=results,
        )

    async def download(self, request: m.DownloadRequest) -> m.DownloadResponse:
        """Download record."""

        async def _stream(response: Response) -> AsyncIterator[bytes]:
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()

        event = request.event
        start = request.start

        start = Serializer(m.DownloadRequestStart).json(start)

        url = f"{Endpoint.RECORDS}/{event}/{start}"

        req = self._client.build_request("GET", url)
        res = await self._client.send(req, stream=True)

        headers = res.headers

        type = headers.get("Content-Type")
        size = int(headers.get("Content-Length"))
        tag = headers.get("ETag")
        modified = httpparse(headers.get("Last-Modified"))
        data = _stream(res)

        return m.DownloadResponse(
            type=type,
            size=size,
            tag=tag,
            modified=modified,
            data=data,
        )


class EmirecordsService(BaseService):
    """Service for emirecords service."""

    records: RecordsNamespace
