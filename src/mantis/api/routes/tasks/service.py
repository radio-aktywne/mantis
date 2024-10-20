from collections.abc import Generator
from contextlib import contextmanager

from mantis.api.routes.tasks import errors as e
from mantis.api.routes.tasks import models as m
from mantis.services.scheduler import errors as se
from mantis.services.scheduler.models import transfer as sm
from mantis.services.scheduler.service import SchedulerService


class Service:
    """Service for the tasks endpoint."""

    def __init__(self, scheduler: SchedulerService) -> None:
        self._scheduler = scheduler

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.InvalidOperationError as ex:
            raise e.ValidationError(str(ex)) from ex
        except se.InvalidConditionError as ex:
            raise e.ValidationError(str(ex)) from ex
        except se.InvalidCleaningStrategyError as ex:
            raise e.ValidationError(str(ex)) from ex
        except se.TaskNotFoundError as ex:
            raise e.TaskNotFoundError(ex.id) from ex
        except se.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List tasks."""

        with self._handle_errors():
            tasks = await self._scheduler.tasks.list()

        tasks = m.TaskIndex.map(tasks)
        return m.ListResponse(
            tasks=tasks,
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get a task."""

        id = request.id

        with self._handle_errors():
            task = await self._scheduler.tasks.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        task = m.GenericTask.map(task)
        return m.GetResponse(
            task=task,
        )

    async def get_pending(self, request: m.GetPendingRequest) -> m.GetPendingResponse:
        """Get a pending task."""

        id = request.id

        with self._handle_errors():
            task = await self._scheduler.tasks.pending.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        task = m.PendingTask.map(task)
        return m.GetPendingResponse(
            task=task,
        )

    async def get_running(self, request: m.GetRunningRequest) -> m.GetRunningResponse:
        """Get a running task."""

        id = request.id

        with self._handle_errors():
            task = await self._scheduler.tasks.running.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        task = m.RunningTask.map(task)
        return m.GetRunningResponse(
            task=task,
        )

    async def get_cancelled(
        self, request: m.GetCancelledRequest
    ) -> m.GetCancelledResponse:
        """Get a cancelled task."""

        id = request.id

        with self._handle_errors():
            task = await self._scheduler.tasks.cancelled.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        task = m.CancelledTask.map(task)
        return m.GetCancelledResponse(
            task=task,
        )

    async def get_failed(self, request: m.GetFailedRequest) -> m.GetFailedResponse:
        """Get a failed task."""

        id = request.id

        with self._handle_errors():
            task = await self._scheduler.tasks.failed.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        task = m.FailedTask.map(task)
        return m.GetFailedResponse(
            task=task,
        )

    async def get_completed(
        self, request: m.GetCompletedRequest
    ) -> m.GetCompletedResponse:
        """Get a completed task."""

        id = request.id

        with self._handle_errors():
            task = await self._scheduler.tasks.completed.get(id)

        if task is None:
            raise e.TaskNotFoundError(id)

        task = m.CompletedTask.map(task)
        return m.GetCompletedResponse(
            task=task,
        )

    async def schedule(self, request: m.ScheduleRequest) -> m.ScheduleResponse:
        """Schedule a task."""

        data = request.data

        with self._handle_errors():
            task = await self._scheduler.schedule(data.map())

        task = m.PendingTask.map(task)
        return m.ScheduleResponse(
            task=task,
        )

    async def cancel(self, request: m.CancelRequest) -> m.CancelResponse:
        """Cancel a task."""

        id = request.id

        req = sm.CancelRequest(
            id=id,
        )

        with self._handle_errors():
            task = await self._scheduler.cancel(req)

        task = m.CancelledTask.map(task)
        return m.CancelResponse(
            task=task,
        )

    async def clean(self, request: m.CleanRequest) -> m.CleanResponse:
        """Clean tasks."""

        data = request.data

        with self._handle_errors():
            results = await self._scheduler.clean(data.map())

        results = m.CleaningResult.map(results)
        return m.CleanResponse(
            results=results,
        )
