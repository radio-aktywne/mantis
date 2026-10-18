import asyncio
from collections.abc import Sequence
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from typing import override
from uuid import UUID

from pydantic import ValidationError

from mantis.config.models import StreamSynchronizerConfig
from mantis.services.apis.beaver import models as bm
from mantis.services.apis.beaver.service import BeaverService
from mantis.services.scheduler import errors as se
from mantis.services.scheduler.models import enums as e, transfer as t
from mantis.services.scheduler.operations.operations.stream.models import Parameters
from mantis.services.scheduler.service import SchedulerService
from mantis.services.synchronizer.synchronizers.synchronizer import Synchronizer
from mantis.utils.time import awareutcnow, isostringify


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
        now = awareutcnow()
        start = now - self._config.window / 2
        end = now + self._config.window / 2

        return start, end

    async def _get_instances(
        self, start: datetime, end: datetime
    ) -> Sequence[bm.InstanceWithEvent]:
        instances_list_request = bm.InstancesListRequest(
            start=start,
            end=end,
            where={
                "event": {
                    "is": {
                        "OR": [
                            {"type": bm.EventType.replay},
                            {"type": bm.EventType.prerecorded},
                        ]
                    }
                }
            },
            include={"event": True},
        )

        instances_list_response = await self._beaver.instances.list(
            instances_list_request
        )

        return [
            instance
            for instance in instances_list_response.results.instances
            if isinstance(instance, bm.InstanceWithEvent)
        ]

    async def _fetch_tasks(self) -> Sequence[t.GenericTask]:
        index = await self._scheduler.tasks.list()
        ids = (
            index.queued
            | index.waiting
            | index.sleeping
            | index.running
            | index.cancelled
            | index.failed
            | index.completed
        )

        tasks = await asyncio.gather(
            *(self._scheduler.tasks.get(task_id) for task_id in ids)
        )
        return [task for task in tasks if task is not None]

    async def _filter_tasks(
        self, tasks: Sequence[t.GenericTask]
    ) -> Sequence[tuple[t.GenericTask, Parameters]]:
        filtered: list[tuple[t.GenericTask, Parameters]] = []

        for task in tasks:
            if task.task.operation.type != "stream":
                continue

            try:
                params = Parameters.model_validate(task.task.operation.parameters)
            except ValidationError:
                continue

            filtered = [*filtered, (task, params)]

        return filtered

    async def _get_stream_tasks(self) -> Sequence[tuple[t.GenericTask, Parameters]]:
        tasks = await self._fetch_tasks()
        return await self._filter_tasks(tasks)

    async def _cancel(self, task_id: UUID) -> None:
        cancel_request = t.CancelRequest(id=task_id)

        with suppress(se.ServiceError):
            await self._scheduler.cancel(cancel_request)

    async def _cancel_extra_tasks(
        self,
        instances: Sequence[bm.InstanceWithEvent],
        tasks: Sequence[tuple[t.GenericTask, Parameters]],
    ) -> None:
        cancel = set[UUID]()

        for task, params in tasks:
            if task.status in {e.Status.CANCELLED, e.Status.FAILED, e.Status.COMPLETED}:
                continue

            instance = next(
                (
                    instance
                    for instance in instances
                    if instance.event.id == params.event
                    and instance.start == params.start
                ),
                None,
            )

            if instance is None:
                cancel = cancel | {task.task.id}

        await asyncio.gather(*(self._cancel(task_id) for task_id in cancel))

    async def _add(self, instance: bm.InstanceWithEvent) -> None:
        start = instance.start.replace(tzinfo=instance.event.timezone).astimezone(UTC)
        at = start - timedelta(minutes=15)

        schedule_request = t.ScheduleRequest(
            operation=t.Specification(
                type="stream",
                parameters={
                    "event": str(instance.event.id),
                    "start": isostringify(instance.start),
                },
            ),
            condition=t.Specification(
                type="at", parameters={"datetime": isostringify(at)}
            ),
            dependencies={},
        )

        with suppress(se.ServiceError):
            await self._scheduler.schedule(schedule_request)

    async def _add_new_tasks(
        self,
        instances: Sequence[bm.InstanceWithEvent],
        tasks: Sequence[tuple[t.GenericTask, Parameters]],
    ) -> None:
        add: list[bm.InstanceWithEvent] = []

        for instance in instances:
            if (
                instance.start.replace(tzinfo=instance.event.timezone).astimezone(UTC)
                < awareutcnow()
            ):
                continue

            task = next(
                (
                    task
                    for task, params in tasks
                    if params.event == instance.event.id
                    and params.start == instance.start
                    and task.status != e.Status.FAILED
                ),
                None,
            )

            if task is None:
                add = [*add, instance]

        await asyncio.gather(*(self._add(instance) for instance in add))

    @override
    async def synchronize(self) -> None:
        start, end = self._get_time_window()

        instances = await self._get_instances(start, end)
        tasks = await self._get_stream_tasks()

        await self._cancel_extra_tasks(instances, tasks)
        await self._add_new_tasks(instances, tasks)
