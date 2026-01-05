from typing import Any

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace

from mantis.config.models import BeaverConfig
from mantis.services.beaver import models as m
from mantis.services.beaver.serializer import Serializer


class Endpoint(BaseEndpoint):
    """Endpoints for beaver service."""

    EVENTS = "/events"
    SCHEDULE = "/schedule"


class BaseService(Gracy[Endpoint]):
    """Base class for beaver service."""

    def __init__(self, config: BeaverConfig, *args: Any, **kwargs: Any) -> None:
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


class EventsNamespace(GracyNamespace[Endpoint]):
    """Namespace for beaver events endpoint."""

    async def mget(self, request: m.EventsGetRequest) -> m.EventsGetResponse:
        """Get an event by ID."""
        event_id = request.id
        include = request.include

        params = {}
        if include is not None:
            params["include"] = Serializer[m.EventsGetRequestInclude].serialize_json(
                include
            )

        path = f"{Endpoint.EVENTS}/{event_id}"

        res = await self.get(path, params=params)

        event = m.Event.model_validate_json(res.content)

        return m.EventsGetResponse(
            event=event,
        )

    async def list(self, request: m.EventsListRequest) -> m.EventsListResponse:
        """List events that match the request."""
        limit = request.limit
        offset = request.offset
        where = request.where
        include = request.include
        order = request.order

        params = {}
        if limit is not None:
            params["limit"] = Serializer[m.EventsListRequestLimit].serialize_json(limit)
        if offset is not None:
            params["offset"] = Serializer[m.EventsListRequestOffset].serialize_json(
                offset
            )
        if where is not None:
            params["where"] = Serializer[m.EventsListRequestWhere].serialize_json(where)
        if include is not None:
            params["include"] = Serializer[m.EventsListRequestInclude].serialize_json(
                include
            )
        if order is not None:
            params["order"] = Serializer[m.EventsListRequestOrder].serialize_json(order)

        res = await self.get(Endpoint.EVENTS, params=params)

        results = m.EventList.model_validate_json(res.content)

        return m.EventsListResponse(
            results=results,
        )


class ScheduleNamespace(GracyNamespace[Endpoint]):
    """Namespace for beaver schedule endpoint."""

    async def list(self, request: m.ScheduleListRequest) -> m.ScheduleListResponse:
        """List schedules."""
        start = request.start
        end = request.end
        limit = request.limit
        offset = request.offset
        where = request.where
        include = request.include
        order = request.order

        params = {}
        if start is not None:
            params["start"] = Serializer[m.ScheduleListRequestStart].serialize_json(
                start
            )
        if end is not None:
            params["end"] = Serializer[m.ScheduleListRequestEnd].serialize_json(end)
        if limit is not None:
            params["limit"] = Serializer[m.ScheduleListRequestLimit].serialize_json(
                limit
            )
        if offset is not None:
            params["offset"] = Serializer[m.ScheduleListRequestOffset].serialize_json(
                offset
            )
        if where is not None:
            params["where"] = Serializer[m.ScheduleListRequestWhere].serialize_json(
                where
            )
        if include is not None:
            params["include"] = Serializer[m.ScheduleListRequestInclude].serialize_json(
                include
            )
        if order is not None:
            params["order"] = Serializer[m.ScheduleListRequestOrder].serialize_json(
                order
            )

        res = await self.get(Endpoint.SCHEDULE, params=params)

        results = m.ScheduleList.model_validate_json(res.content)

        return m.ScheduleListResponse(
            results=results,
        )


class BeaverService(BaseService):
    """Service for beaver service."""

    events: EventsNamespace
    schedule: ScheduleNamespace
