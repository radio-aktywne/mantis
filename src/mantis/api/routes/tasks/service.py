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
            raise e.ValidationError from ex
        except se.InvalidConditionError as ex:
            raise e.ValidationError from ex
        except se.InvalidCleaningStrategyError as ex:
            raise e.ValidationError from ex
        except se.TaskNotFoundError as ex:
            raise e.TaskNotFoundError(ex.id) from ex
        except se.ServiceError as ex:
            raise e.ServiceError from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List tasks."""
        with self._handle_errors():
            tasks = await self._scheduler.tasks.list()

        return m.ListResponse(tasks=m.TaskIndex.map(tasks))

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get a task."""
        with self._handle_errors():
            task = await self._scheduler.tasks.get(request.id)

        if task is None:
            raise e.TaskNotFoundError(request.id)

        return m.GetResponse(task=m.GenericTask.map(task))

    async def get_pending(self, request: m.GetPendingRequest) -> m.GetPendingResponse:
        """Get a pending task."""
        with self._handle_errors():
            task = await self._scheduler.tasks.pending.get(request.id)

        if task is None:
            raise e.TaskNotFoundError(request.id)

        return m.GetPendingResponse(task=m.PendingTask.map(task))

    async def get_running(self, request: m.GetRunningRequest) -> m.GetRunningResponse:
        """Get a running task."""
        with self._handle_errors():
            task = await self._scheduler.tasks.running.get(request.id)

        if task is None:
            raise e.TaskNotFoundError(request.id)

        return m.GetRunningResponse(task=m.RunningTask.map(task))

    async def get_cancelled(
        self, request: m.GetCancelledRequest
    ) -> m.GetCancelledResponse:
        """Get a cancelled task."""
        with self._handle_errors():
            task = await self._scheduler.tasks.cancelled.get(request.id)

        if task is None:
            raise e.TaskNotFoundError(request.id)

        return m.GetCancelledResponse(task=m.CancelledTask.map(task))

    async def get_failed(self, request: m.GetFailedRequest) -> m.GetFailedResponse:
        """Get a failed task."""
        with self._handle_errors():
            task = await self._scheduler.tasks.failed.get(request.id)

        if task is None:
            raise e.TaskNotFoundError(request.id)

        return m.GetFailedResponse(task=m.FailedTask.map(task))

    async def get_completed(
        self, request: m.GetCompletedRequest
    ) -> m.GetCompletedResponse:
        """Get a completed task."""
        with self._handle_errors():
            task = await self._scheduler.tasks.completed.get(request.id)

        if task is None:
            raise e.TaskNotFoundError(request.id)

        return m.GetCompletedResponse(task=m.CompletedTask.map(task))

    async def schedule(self, request: m.ScheduleRequest) -> m.ScheduleResponse:
        """Schedule a task."""
        with self._handle_errors():
            task = await self._scheduler.schedule(request.data.map())

        return m.ScheduleResponse(task=m.PendingTask.map(task))

    async def cancel(self, request: m.CancelRequest) -> m.CancelResponse:
        """Cancel a task."""
        cancel_request = sm.CancelRequest(id=request.id)

        with self._handle_errors():
            task = await self._scheduler.cancel(cancel_request)

        return m.CancelResponse(task=m.CancelledTask.map(task))

    async def clean(self, request: m.CleanRequest) -> m.CleanResponse:
        """Clean tasks."""
        with self._handle_errors():
            results = await self._scheduler.clean(request.data.map())

        return m.CleanResponse(results=m.CleaningResult.map(results))
