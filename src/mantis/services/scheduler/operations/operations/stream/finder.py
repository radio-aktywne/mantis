from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from uuid import UUID

from mantis.services.beaver import errors as be
from mantis.services.beaver import models as bm
from mantis.services.beaver.service import BeaverService
from mantis.services.scheduler.operations.operations.stream import errors as e
from mantis.services.scheduler.operations.operations.stream import models as m


class Finder:
    """Utility to find event instances."""

    def __init__(self, beaver: BeaverService) -> None:
        self._beaver = beaver

    async def _get_event(self, event_id: UUID) -> bm.Event:
        events_get_request = bm.EventsGetRequest(id=event_id)

        try:
            events_get_response = await self._beaver.events.get_by_id(
                events_get_request
            )
        except be.ResponseError as ex:
            if ex.response.status_code == HTTPStatus.NOT_FOUND:
                raise e.EventNotFoundError(event_id) from ex
            raise

        return events_get_response.event

    async def _list_schedules(
        self, event_id: UUID, start: datetime, end: datetime
    ) -> Sequence[bm.Schedule]:
        schedules: list[bm.Schedule] = []
        offset = 0

        while True:
            schedule_list_request = bm.ScheduleListRequest(
                start=start,
                end=end,
                limit=None,
                offset=offset,
                where={"id": str(event_id)},
            )

            schedule_list_response = await self._beaver.schedule.list(
                schedule_list_request
            )

            new = schedule_list_response.results.schedules

            schedules = schedules + list(new)
            offset = offset + len(new)

            if offset >= schedule_list_response.results.count:
                break

        return schedules

    async def _get_schedule(self, event_id: UUID, start: datetime) -> bm.Schedule:
        event = await self._get_event(event_id)

        utcstart = (
            start.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=event.timezone
            )
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        utcend = utcstart + timedelta(days=1)

        schedules = await self._list_schedules(event.id, utcstart, utcend)

        schedule = next(iter(schedules), None)

        if schedule is None:
            raise e.ScheduleNotFoundError(event.id)

        return schedule

    async def _find_instance(
        self, schedule: bm.Schedule, start: datetime
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

        return m.FindResponse(event=schedule.event, instance=instance)
