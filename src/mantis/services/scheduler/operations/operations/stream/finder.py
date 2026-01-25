from collections.abc import Sequence
from datetime import UTC, timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING, cast
from uuid import UUID
from zoneinfo import ZoneInfo

if TYPE_CHECKING:
    from httpx import Response

from mantis.services.beaver import errors as be
from mantis.services.beaver import models as bm
from mantis.services.beaver.service import BeaverService
from mantis.services.scheduler.operations.operations.stream import errors as e
from mantis.services.scheduler.operations.operations.stream import models as m
from mantis.utils.time import NaiveDatetime


class Finder:
    """Utility to find event instances."""

    def __init__(self, beaver: BeaverService) -> None:
        self._beaver = beaver

    async def _get_event(self, event_id: UUID) -> bm.Event:
        req = bm.EventsGetRequest(
            id=event_id,
            include=None,
        )

        try:
            res = await self._beaver.events.mget(req)
        except be.ServiceError as ex:
            if hasattr(ex, "response"):
                response = cast("Response", ex.response)  # type: ignore[attr-defined]
                if response.status_code == HTTPStatus.NOT_FOUND:
                    raise e.EventNotFoundError(event_id) from ex
            raise

        return res.event

    async def _list_schedules(
        self, event: UUID, start: NaiveDatetime, end: NaiveDatetime
    ) -> Sequence[bm.Schedule]:
        schedules: list[bm.Schedule] = []
        offset = 0

        while True:
            req = bm.ScheduleListRequest(
                start=start,
                end=end,
                limit=None,
                offset=offset,
                where={
                    "id": str(event),
                },
                include=None,
                order=None,
            )

            res = await self._beaver.schedule.list(req)

            new = res.results.schedules
            count = res.results.count

            schedules = schedules + list(new)
            offset = offset + len(new)

            if offset >= count:
                break

        return schedules

    async def _get_schedule(self, event: UUID, start: NaiveDatetime) -> bm.Schedule:
        mevent = await self._get_event(event)

        tz = ZoneInfo(mevent.timezone)
        utcstart = (
            start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        utcend = utcstart + timedelta(days=1)

        schedules = await self._list_schedules(mevent.id, utcstart, utcend)

        schedule = next(iter(schedules), None)

        if schedule is None:
            raise e.ScheduleNotFoundError(mevent.id)

        return schedule

    async def _find_instance(
        self, schedule: bm.Schedule, start: NaiveDatetime
    ) -> bm.EventInstance:
        instance = next(
            (instance for instance in schedule.instances if instance.start == start),
            None,
        )

        if instance is None:
            raise e.InstanceNotFoundError(schedule.event.id, start)

        return instance

    async def find(self, request: m.FindRequest) -> m.FindResponse:
        """Find an event instance."""
        schedule = await self._get_schedule(request.event, request.start)
        instance = await self._find_instance(schedule, request.start)

        return m.FindResponse(
            event=schedule.event,
            instance=instance,
        )
