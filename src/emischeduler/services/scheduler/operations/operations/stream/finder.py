from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID

from zoneinfo import ZoneInfo

from emischeduler.services.emishows import errors as eshe
from emischeduler.services.emishows import models as eshm
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.scheduler.operations.operations.stream import errors as e
from emischeduler.services.scheduler.operations.operations.stream import models as m


class Finder:
    """Utility to find event instances."""

    def __init__(self, emishows: EmishowsService) -> None:
        self._emishows = emishows

    async def _get_event(self, id: UUID) -> eshm.Event:
        req = eshm.EventsGetRequest(
            id=id,
            include=None,
        )

        try:
            res = await self._emishows.events.mget(req)
        except eshe.ServiceError as ex:
            if hasattr(ex, "response"):
                if ex.response.status_code == HTTPStatus.NOT_FOUND:
                    raise e.EventNotFoundError(id) from ex
            raise

        return res.event

    async def _list_schedules(
        self, event: UUID, start: datetime, end: datetime
    ) -> list[eshm.Schedule]:
        schedules: list[eshm.Schedule] = []
        offset = 0

        while True:
            req = eshm.ScheduleListRequest(
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

            res = await self._emishows.schedule.list(req)

            new = res.results.schedules
            count = res.results.count

            schedules = schedules + new
            offset = offset + len(new)

            if offset >= count:
                break

        return schedules

    async def _get_schedule(self, event: UUID, start: datetime) -> eshm.Schedule:
        mevent = await self._get_event(event)

        tz = ZoneInfo(mevent.timezone)
        utcstart = start.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)
        utcstart = utcstart.astimezone(UTC).replace(tzinfo=None)
        utcend = utcstart + timedelta(days=1)

        schedules = await self._list_schedules(mevent.id, utcstart, utcend)

        schedule = next(iter(schedules), None)

        if schedule is None:
            raise e.ScheduleNotFoundError(mevent.id)

        return schedule

    async def _find_instance(
        self, schedule: eshm.Schedule, start: datetime
    ) -> eshm.EventInstance:
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
