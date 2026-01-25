from datetime import UTC
from uuid import UUID

from mantis.models.base import SerializableModel, datamodel
from mantis.services.scheduler.models import transfer as sm
from mantis.utils.time import NaiveDatetime


class TaskIndex(SerializableModel):
    """Index of tasks by status."""

    pending: set[UUID]
    """Identifiers of pending tasks."""

    running: set[UUID]
    """Identifiers of running tasks."""

    cancelled: set[UUID]
    """Identifiers of cancelled tasks."""

    failed: set[UUID]
    """Identifiers of failed tasks."""

    completed: set[UUID]
    """Identifiers of completed tasks."""

    @staticmethod
    def map(index: sm.TaskIndex) -> "TaskIndex":
        """Map to internal representation."""
        return TaskIndex(
            pending=index.pending,
            running=index.running,
            cancelled=index.cancelled,
            failed=index.failed,
            completed=index.completed,
        )


class GenericTask(SerializableModel):
    """Data of a task of any status."""

    task: sm.Task
    """Task data."""

    status: sm.Status
    """Task status."""

    @staticmethod
    def map(task: sm.GenericTask) -> "GenericTask":
        """Map to internal representation."""
        return GenericTask(
            task=task.task,
            status=task.status,
        )


class PendingTask(SerializableModel):
    """Data of a pending task."""

    task: sm.Task
    """Task data."""

    scheduled: NaiveDatetime
    """Datetime in UTC when the task was scheduled."""

    @staticmethod
    def map(task: sm.PendingTask) -> "PendingTask":
        """Map to internal representation."""
        return PendingTask(
            task=task.task,
            scheduled=task.scheduled.astimezone(UTC).replace(tzinfo=None),
        )


class RunningTask(SerializableModel):
    """Data of a running task."""

    task: sm.Task
    """Task data."""

    scheduled: NaiveDatetime
    """Datetime in UTC when the task was scheduled."""

    started: NaiveDatetime
    """Datetime in UTC when the task was started."""

    @staticmethod
    def map(task: sm.RunningTask) -> "RunningTask":
        """Map to internal representation."""
        return RunningTask(
            task=task.task,
            scheduled=task.scheduled.astimezone(UTC).replace(tzinfo=None),
            started=task.started.astimezone(UTC).replace(tzinfo=None),
        )


class CancelledTask(SerializableModel):
    """Data of a cancelled task."""

    task: sm.Task
    """Task data."""

    scheduled: NaiveDatetime
    """Datetime in UTC when the task was scheduled."""

    started: NaiveDatetime | None
    """Datetime in UTC when the task was started."""

    cancelled: NaiveDatetime
    """Datetime in UTC when the task was cancelled."""

    @staticmethod
    def map(task: sm.CancelledTask) -> "CancelledTask":
        """Map to internal representation."""
        return CancelledTask(
            task=task.task,
            scheduled=task.scheduled.astimezone(UTC).replace(tzinfo=None),
            started=task.started.astimezone(UTC).replace(tzinfo=None)
            if task.started
            else None,
            cancelled=task.cancelled.astimezone(UTC).replace(tzinfo=None),
        )


class FailedTask(SerializableModel):
    """Data of a failed task."""

    task: sm.Task
    """Task data."""

    scheduled: NaiveDatetime
    """Datetime in UTC when the task was scheduled."""

    started: NaiveDatetime
    """Datetime in UTC when the task was started."""

    failed: NaiveDatetime
    """Datetime in UTC when the task failed."""

    error: str
    """Error message."""

    @staticmethod
    def map(task: sm.FailedTask) -> "FailedTask":
        """Map to internal representation."""
        return FailedTask(
            task=task.task,
            scheduled=task.scheduled.astimezone(UTC).replace(tzinfo=None),
            started=task.started.astimezone(UTC).replace(tzinfo=None),
            failed=task.failed.astimezone(UTC).replace(tzinfo=None),
            error=task.error,
        )


class CompletedTask(SerializableModel):
    """Data of a completed task."""

    task: sm.Task
    """Task data."""

    scheduled: NaiveDatetime
    """Datetime in UTC when the task was scheduled."""

    started: NaiveDatetime
    """Datetime in UTC when the task was started."""

    completed: NaiveDatetime
    """Datetime in UTC when the task was completed."""

    result: sm.JSON
    """Result of the task."""

    @staticmethod
    def map(task: sm.CompletedTask) -> "CompletedTask":
        """Map to internal representation."""
        return CompletedTask(
            task=task.task,
            scheduled=task.scheduled.astimezone(UTC).replace(tzinfo=None),
            started=task.started.astimezone(UTC).replace(tzinfo=None),
            completed=task.completed.astimezone(UTC).replace(tzinfo=None),
            result=task.result,
        )


class ScheduleRequestModel(SerializableModel):
    """Request to schedule a task."""

    operation: sm.Specification
    """Operation specification."""

    condition: sm.Specification
    """Condition specification."""

    dependencies: dict[str, UUID]
    """Dependencies of the task."""

    def map(self) -> sm.ScheduleRequest:
        """Map to external representation."""
        return sm.ScheduleRequest(
            operation=self.operation,
            condition=self.condition,
            dependencies=self.dependencies,
        )


class CleanRequestModel(SerializableModel):
    """Request to clean tasks."""

    strategy: sm.Specification
    """Cleaning strategy specification."""

    def map(self) -> sm.CleanRequest:
        """Map to external representation."""
        return sm.CleanRequest(
            strategy=self.strategy,
        )


class CleaningResult(SerializableModel):
    """Result of cleaning."""

    removed: set[UUID]
    """Identifiers of removed tasks."""

    @staticmethod
    def map(result: sm.CleaningResult) -> "CleaningResult":
        """Map to internal representation."""
        return CleaningResult(
            removed=result.removed,
        )


ListResponseTasks = TaskIndex

GetRequestId = UUID

GetResponseTask = GenericTask

GetPendingRequestId = UUID

GetPendingResponseTask = PendingTask

GetRunningRequestId = UUID

GetRunningResponseTask = RunningTask

GetCancelledRequestId = UUID

GetCancelledResponseTask = CancelledTask

GetFailedRequestId = UUID

GetFailedResponseTask = FailedTask

GetCompletedRequestId = UUID

GetCompletedResponseTask = CompletedTask

ScheduleRequestData = ScheduleRequestModel

ScheduleResponseTask = PendingTask

CancelRequestId = UUID

CancelResponseTask = CancelledTask

CleanRequestData = CleanRequestModel

CleanResponseResults = CleaningResult


@datamodel
class ListRequest:
    """Request to list tasks."""


@datamodel
class ListResponse:
    """Response for listing tasks."""

    tasks: ListResponseTasks
    """Tasks index."""


@datamodel
class GetRequest:
    """Request to get a task."""

    id: GetRequestId
    """Identifier of the task."""


@datamodel
class GetResponse:
    """Response for getting a task."""

    task: GetResponseTask
    """Retrieved task."""


@datamodel
class GetPendingRequest:
    """Request to get a pending task."""

    id: GetPendingRequestId
    """Identifier of the task."""


@datamodel
class GetPendingResponse:
    """Response for getting a pending task."""

    task: GetPendingResponseTask
    """Retrieved pending task."""


@datamodel
class GetRunningRequest:
    """Request to get a running task."""

    id: GetRunningRequestId
    """Identifier of the task."""


@datamodel
class GetRunningResponse:
    """Response for getting a running task."""

    task: GetRunningResponseTask
    """Retrieved running task."""


@datamodel
class GetCancelledRequest:
    """Request to get a cancelled task."""

    id: GetCancelledRequestId
    """Identifier of the task."""


@datamodel
class GetCancelledResponse:
    """Response for getting a cancelled task."""

    task: GetCancelledResponseTask
    """Retrieved cancelled task."""


@datamodel
class GetFailedRequest:
    """Request to get a failed task."""

    id: GetFailedRequestId
    """Identifier of the task."""


@datamodel
class GetFailedResponse:
    """Response for getting a failed task."""

    task: GetFailedResponseTask
    """Retrieved failed task."""


@datamodel
class GetCompletedRequest:
    """Request to get a completed task."""

    id: GetCompletedRequestId
    """Identifier of the task."""


@datamodel
class GetCompletedResponse:
    """Response for getting a completed task."""

    task: GetCompletedResponseTask
    """Retrieved completed task."""


@datamodel
class ScheduleRequest:
    """Request to schedule a task."""

    data: ScheduleRequestData
    """Data to schedule a task."""


@datamodel
class ScheduleResponse:
    """Response for scheduling a task."""

    task: ScheduleResponseTask
    """Scheduled pending task."""


@datamodel
class CancelRequest:
    """Request to cancel a task."""

    id: CancelRequestId
    """Identifier of the task."""


@datamodel
class CancelResponse:
    """Response for cancelling a task."""

    task: CancelResponseTask
    """Cancelled task."""


@datamodel
class CleanRequest:
    """Request to clean tasks."""

    data: CleanRequestData
    """Data to clean tasks."""


@datamodel
class CleanResponse:
    """Response for cleaning tasks."""

    results: CleanResponseResults
    """Cleaning results."""
