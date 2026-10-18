from collections.abc import Mapping
from http import HTTPMethod, HTTPStatus
from typing import Any

from httpx2 import AsyncClient, HTTPError, HTTPStatusError, Response

from mantis.config.models import BeaverConfig, BeaverHTTPConfig
from mantis.models.base import Jsonable, Serializable
from mantis.services.apis.beaver import errors as e, models as m


class BeaverClient:
    """Client for beaver API."""

    def __init__(self, config: BeaverHTTPConfig) -> None:
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


class BeaverInstancesService:
    """Service for instances in beaver API."""

    def __init__(self, client: BeaverClient) -> None:
        self.client = client

    def _dump(self, value: Serializable) -> Any:
        return value.model_dump(mode="json", round_trip=True)

    def _dump_json(self, value: Jsonable) -> str:
        return value.model_dump_json(round_trip=True)

    async def list(self, request: m.InstancesListRequest) -> m.InstancesListResponse:
        """List instances."""
        start = self._dump_json(Jsonable[m.InstancesListRequestStart](request.start))
        end = self._dump_json(Jsonable[m.InstancesListRequestEnd](request.end))
        where = self._dump_json(Jsonable[m.InstancesListRequestWhere](request.where))
        include = self._dump_json(
            Jsonable[m.InstancesListRequestInclude](request.include)
        )

        response = await self.client.request(
            HTTPMethod.GET,
            "/instances",
            params={"start": start, "end": end, "where": where, "include": include},
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as ex:
            raise e.ServiceError from ex

        return m.InstancesListResponse(
            results=Serializable[m.InstancesListResponseResults]
            .model_validate_json(response.content)
            .root
        )

    async def get(self, request: m.InstancesGetRequest) -> m.InstancesGetResponse:
        """Get instance."""
        event_id = self._dump(
            Serializable[m.InstancesGetRequestEventId](request.event_id)
        )
        start = self._dump(Serializable[m.InstancesGetRequestStart](request.start))
        include = self._dump_json(
            Jsonable[m.InstancesGetRequestInclude](request.include)
        )

        response = await self.client.request(
            HTTPMethod.GET,
            f"/instances/{event_id}/{start}",
            params={"include": include},
        )

        try:
            response.raise_for_status()
        except HTTPStatusError as ex:
            if ex.response.status_code == HTTPStatus.NOT_FOUND:
                raise e.NotFoundError from ex
            raise e.ServiceError from ex

        return m.InstancesGetResponse(
            instance=Serializable[m.InstancesGetResponseInstance]
            .model_validate_json(response.content)
            .root
        )


class BeaverService:
    """Service for beaver API."""

    def __init__(self, config: BeaverConfig) -> None:
        self.client = BeaverClient(config.http)

    @property
    def instances(self) -> BeaverInstancesService:
        """Service for instances in beaver API."""
        return BeaverInstancesService(self.client)
