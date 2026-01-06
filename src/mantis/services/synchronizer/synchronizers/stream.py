from collections.abc import Collection, Sequence
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from mantis.config.models import StreamSynchronizerConfig
from mantis.services.beaver import models as bm
from mantis.services.beaver.service import BeaverService
from mantis.services.scheduler import errors as se
from mantis.services.scheduler.models import enums as e
from mantis.services.scheduler.models import transfer as t
from mantis.services.scheduler.operations.operations.stream.models import (
    Parameters,
)
from mantis.services.scheduler.service import SchedulerService
from mantis.services.synchronizer.synchronizers.synchronizer import Synchronizer
from mantis.utils.time import naiveutcnow


class StreamSynchronizer(Synchronizer):
    """Synchronizes stream tasks."""

    def __init__(
        self,
        config: StreamSynchronizerConfig,
        beaver: BeaverService,
        scheduler: SchedulerService,
    ) -> None:
        self._config = config
        self._beaver = beaver
        self._scheduler = scheduler

    def _get_time_window(self) -> tuple[datetime, datetime]:
        start = naiveutcnow()
        end = start + self._config.window

        return start, end

    async def _fetch_schedules(
        self, start: datetime, end: datetime
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
                    "OR": [
                        {
                            "type": bm.EventType.replay,
                        },
                        {
                            "type": bm.EventType.prerecorded,
                        },
                    ],
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

    def _filter_schedules(
        self, schedules: Sequence[bm.Schedule], start: datetime, end: datetime
    ) -> Sequence[bm.Schedule]:
        out: list[bm.Schedule] = []

        for schedule in schedules:
            instances: list[bm.EventInstance] = []
            tz = ZoneInfo(schedule.event.timezone)

            for instance in schedule.instances:
                istart = (
                    instance.start.replace(tzinfo=tz)
                    .astimezone(UTC)
                    .replace(tzinfo=None)
                )

                if istart >= start and istart < end:
                    instances = [*instances, instance]

            if len(instances) > 0:
                out = [
                    *out,
                    bm.Schedule(
                        event=schedule.event,
                        instances=instances,
                    ),
                ]

        return out

    async def _get_schedules(
        self, start: datetime, end: datetime
    ) -> Sequence[bm.Schedule]:
        schedules = await self._fetch_schedules(start, end)
        return self._filter_schedules(schedules, start, end)

    async def _fetch_tasks(self) -> Sequence[t.GenericTask]:
        index = await self._scheduler.tasks.list()
        ids = (
            index.pending
            | index.running
            | index.cancelled
            | index.failed
            | index.completed
        )

        tasks: list[t.GenericTask] = []

        for task_id in ids:
            task = await self._scheduler.tasks.get(task_id)
            if task is not None:
                tasks = [*tasks, task]

        return tasks

    async def _get_events(self, ids: Collection[UUID]) -> Sequence[bm.Event]:
        if len(ids) == 0:
            return []

        events: list[bm.Event] = []
        offset = 0

        while True:
            req = bm.EventsListRequest(
                limit=None,
                offset=offset,
                where={
                    "id": {
                        "in": [str(event_id) for event_id in ids],
                    },
                },
                include=None,
                order=None,
            )

            res = await self._beaver.events.list(req)

            new = res.results.events
            count = res.results.count

            events = events + list(new)
            offset = offset + len(new)

            if offset >= count:
                break

        return events

    async def _filter_tasks(
        self, tasks: Sequence[t.GenericTask], start: datetime, end: datetime
    ) -> tuple[Sequence[tuple[t.GenericTask, Parameters]], Sequence[t.GenericTask]]:
        invalid: list[t.GenericTask] = []
        withparams: list[tuple[t.GenericTask, Parameters]] = []

        for task in tasks:
            if task.status not in {e.Status.PENDING, e.Status.RUNNING}:
                continue

            if task.task.operation.type != "stream":
                continue

            try:
                params = Parameters.model_validate(task.task.operation.parameters)
            except ValidationError:
                invalid = [*invalid, task]
                continue

            withparams = [*withparams, (task, params)]

        ids = {params.id for _, params in withparams}
        events = await self._get_events(ids)
        events = {event.id: event for event in events}

        valid: list[tuple[t.GenericTask, Parameters]] = []

        for task, params in withparams:
            event = events.get(params.id)
            if event is None:
                invalid = [*invalid, task]
                continue

            tz = ZoneInfo(event.timezone)
            istart = (
                params.start.replace(tzinfo=tz).astimezone(UTC).replace(tzinfo=None)
            )

            if istart >= start and istart < end:
                valid = [*valid, (task, params)]

        return valid, invalid

    async def _get_tasks(
        self, start: datetime, end: datetime
    ) -> tuple[Sequence[tuple[t.GenericTask, Parameters]], Sequence[t.GenericTask]]:
        tasks = await self._fetch_tasks()
        return await self._filter_tasks(tasks, start, end)

    async def _cancel(self, task_id: UUID) -> None:
        req = t.CancelRequest(
            id=task_id,
        )

        with suppress(se.ServiceError):
            await self._scheduler.cancel(req)

    async def _cancel_extra_tasks(
        self,
        schedules: Sequence[bm.Schedule],
        tasks: Sequence[tuple[t.GenericTask, Parameters]],
    ) -> None:
        schedulemap = {schedule.event.id: schedule for schedule in schedules}
        cancel = set[UUID]()

        for task, params in tasks:
            schedule = schedulemap.get(params.id)
            if schedule is None:
                cancel = cancel | {task.task.id}
                continue

            instance = next(
                (
                    instance
                    for instance in schedule.instances
                    if instance.start == params.start
                ),
                None,
            )

            if instance is None:
                cancel = cancel | {task.task.id}
                continue

        for task_id in cancel:
            await self._cancel(task_id)

    async def _add(self, event: bm.Event, instance: bm.EventInstance) -> None:
        tz = ZoneInfo(event.timezone)
        utcstart = (
            instance.start.replace(tzinfo=tz).astimezone(UTC).replace(tzinfo=None)
        )
        at = utcstart - timedelta(minutes=15)

        req = t.ScheduleRequest(
            operation=t.Specification(
                type="stream",
                parameters={
                    "id": str(event.id),
                    "start": instance.start.isoformat(),
                },
            ),
            condition=t.Specification(
                type="at",
                parameters={
                    "datetime": at.isoformat(),
                },
            ),
            dependencies={},
        )

        with suppress(se.ServiceError):
            await self._scheduler.schedule(req)

    async def _add_new_tasks(
        self,
        schedules: Sequence[bm.Schedule],
        tasks: Sequence[tuple[t.GenericTask, Parameters]],
    ) -> None:
        add: list[tuple[bm.Event, bm.EventInstance]] = []

        for schedule in schedules:
            ft = filter(lambda tp: tp[1].id == schedule.event.id, tasks)

            for instance in schedule.instances:
                task = next(
                    (task for task, params in ft if params.start == instance.start),
                    None,
                )

                if task is None:
                    add = [*add, (schedule.event, instance)]

        for event, instance in add:
            await self._add(event, instance)

    async def synchronize(self) -> None:
        """Synchronize tasks."""
        start, end = self._get_time_window()

        schedules = await self._get_schedules(start, end)
        valid, invalid = await self._get_tasks(start, end)

        for task in invalid:
            await self._cancel(task.task.id)

        await self._cancel_extra_tasks(schedules, valid)
        await self._add_new_tasks(schedules, valid)
