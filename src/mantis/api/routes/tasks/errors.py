from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class TaskNotFoundError(ServiceError):
    """Raised when task is not found."""

    def __init__(self, task_id: UUID) -> None:
        super().__init__(f"Task not found: {task_id}.")
