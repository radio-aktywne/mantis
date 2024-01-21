from pyscheduler import errors as se
from pyscheduler.models import transfer as t

from emischeduler.api.routes.tasks import errors as e
from emischeduler.api.routes.tasks import models as m
from emischeduler.scheduling.scheduler import Scheduler


class Service:
    """Service for the tasks endpoint."""

    def __init__(self, scheduler: Scheduler) -> None:
        self._scheduler = scheduler

    async def get_index(self) -> m.GetIndexResponse:
        """Get tasks index."""

        return await self._scheduler.tasks.list()

    async def get_task(self, id: m.GetTaskIdParameter) -> m.GetTaskResponse:
        """Get a task."""

        task = await self._scheduler.tasks.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        return task

    async def get_pending_task(
        self, id: m.GetPendingTaskIdParameter
    ) -> m.GetPendingTaskResponse:
        """Get a pending task."""

        task = await self._scheduler.tasks.pending.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        return task

    async def get_running_task(
        self, id: m.GetRunningTaskIdParameter
    ) -> m.GetRunningTaskResponse:
        """Get a running task."""

        task = await self._scheduler.tasks.running.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        return task

    async def get_cancelled_task(
        self, id: m.GetCancelledTaskIdParameter
    ) -> m.GetCancelledTaskResponse:
        """Get a cancelled task."""

        task = await self._scheduler.tasks.cancelled.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        return task

    async def get_failed_task(
        self, id: m.GetFailedTaskIdParameter
    ) -> m.GetFailedTaskResponse:
        """Get a failed task."""

        task = await self._scheduler.tasks.failed.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        return task

    async def get_completed_task(
        self, id: m.GetCompletedTaskIdParameter
    ) -> m.GetCompletedTaskResponse:
        """Get a completed task."""

        task = await self._scheduler.tasks.completed.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        return task

    async def schedule_task(
        self, request: m.ScheduleTaskRequest
    ) -> m.ScheduleTaskResponse:
        """Schedule a task."""

        try:
            return await self._scheduler.schedule(request)
        except se.InvalidOperationError as ex:
            message = f"Invalid operation: {ex.type}."
            raise e.InvalidRequestError(message) from ex
        except se.InvalidConditionError as ex:
            message = f"Invalid condition: {ex.type}."
            raise e.InvalidRequestError(message) from ex
        except se.DependencyNotFoundError as ex:
            message = f"Dependency not found: {ex.id}."
            raise e.InvalidRequestError(message) from ex

    async def cancel_task(self, id: m.CancelTaskIdParameter) -> m.CancelTaskResponse:
        """Cancel a task."""

        try:
            return await self._scheduler.cancel(t.CancelRequest(id=id))
        except se.TaskNotFoundError as ex:
            raise e.TaskNotFoundError(ex.id) from ex

    async def clean_tasks(self, request: m.CleanTasksRequest) -> m.CleanTasksResponse:
        """Clean tasks."""

        try:
            return await self._scheduler.clean(request)
        except se.InvalidCleaningStrategyError as ex:
            message = f"Invalid cleaning strategy: {ex.type}."
            raise e.InvalidRequestError(message) from ex
