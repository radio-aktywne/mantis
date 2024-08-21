from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""

    pass


class TaskNotFoundError(ServiceError):
    """Raised when task is not found."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"Task not found: {id}.")
