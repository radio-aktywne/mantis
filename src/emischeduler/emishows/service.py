from typing import TypeVar

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig, GracyNamespace
from pydantic import TypeAdapter

from emischeduler.config.models import EmishowsConfig
from emischeduler.emishows.models import (
    Event,
    EventsGetByIdIdParameter,
    EventsGetByIdIncludeParameter,
    EventsListIncludeParameter,
    EventsListLimitParameter,
    EventsListOffsetParameter,
    EventsListOrderParameter,
    EventsListResponse,
    EventsListWhereParameter,
    ScheduleListEndParameter,
    ScheduleListIncludeParameter,
    ScheduleListLimitParameter,
    ScheduleListOffsetParameter,
    ScheduleListOrderParameter,
    ScheduleListResponse,
    ScheduleListStartParameter,
    ScheduleListWhereParameter,
)

T = TypeVar("T")


class EmishowsEndpoint(BaseEndpoint):
    """Endpoints for emishows API."""

    EVENTS = "/events"
    SCHEDULE = "/schedule"


class EmishowsServiceBase(Gracy[EmishowsEndpoint]):
    """Base class for emishows API service."""

    def __init__(self, config: EmishowsConfig, *args, **kwargs) -> None:
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


class EmishowsEventsNamespace(GracyNamespace[EmishowsEndpoint]):
    """Namespace for emishows API events endpoint."""

    def _dump_param(self, t: type[T], v: T) -> str:
        value = TypeAdapter(t).dump_json(v, by_alias=True).decode()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value

    async def get_by_id(
        self,
        id: EventsGetByIdIdParameter,
        include: EventsGetByIdIncludeParameter = None,
    ) -> Event:
        params = {}
        if include is not None:
            params["include"] = self._dump_param(EventsGetByIdIncludeParameter, include)

        response = await self.get(f"{EmishowsEndpoint.EVENTS}/{id}", params=params)
        return Event.model_validate_json(response.content)

    async def list(
        self,
        limit: EventsListLimitParameter = None,
        offset: EventsListOffsetParameter = None,
        where: EventsListWhereParameter = None,
        include: EventsListIncludeParameter = None,
        order: EventsListOrderParameter = None,
    ) -> EventsListResponse:
        params = {}
        if limit is not None:
            params["limit"] = self._dump_param(EventsListLimitParameter, limit)
        if offset is not None:
            params["offset"] = self._dump_param(EventsListOffsetParameter, offset)
        if where is not None:
            params["where"] = self._dump_param(EventsListWhereParameter, where)
        if include is not None:
            params["include"] = self._dump_param(EventsListIncludeParameter, include)
        if order is not None:
            params["order"] = self._dump_param(EventsListOrderParameter, order)

        response = await self.get(EmishowsEndpoint.EVENTS, params=params)
        return EventsListResponse.model_validate_json(response.content)


class EmishowsScheduleNamespace(GracyNamespace[EmishowsEndpoint]):
    """Namespace for emishows API schedule endpoint."""

    def _dump_param(self, t: type[T], v: T) -> str:
        value = TypeAdapter(t).dump_json(v, by_alias=True).decode()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value

    async def list(
        self,
        start: ScheduleListStartParameter = None,
        end: ScheduleListEndParameter = None,
        limit: ScheduleListLimitParameter = None,
        offset: ScheduleListOffsetParameter = None,
        where: ScheduleListWhereParameter = None,
        include: ScheduleListIncludeParameter = None,
        order: ScheduleListOrderParameter = None,
    ) -> ScheduleListResponse:
        params = {}
        if start is not None:
            params["start"] = self._dump_param(ScheduleListStartParameter, start)
        if end is not None:
            params["end"] = self._dump_param(ScheduleListEndParameter, end)
        if limit is not None:
            params["limit"] = self._dump_param(ScheduleListLimitParameter, limit)
        if offset is not None:
            params["offset"] = self._dump_param(ScheduleListOffsetParameter, offset)
        if where is not None:
            params["where"] = self._dump_param(ScheduleListWhereParameter, where)
        if include is not None:
            params["include"] = self._dump_param(ScheduleListIncludeParameter, include)
        if order is not None:
            params["order"] = self._dump_param(ScheduleListOrderParameter, order)

        response = await self.get(EmishowsEndpoint.SCHEDULE, params=params)
        return ScheduleListResponse.model_validate_json(response.content)


class EmishowsService(EmishowsServiceBase):
    """Service for emishows API."""

    events: EmishowsEventsNamespace
    schedule: EmishowsScheduleNamespace
