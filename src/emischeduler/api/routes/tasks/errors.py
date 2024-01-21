from uuid import UUID


class ServiceError(Exception):
    """Base class for service errors."""

    pass


class TaskNotFoundError(ServiceError):
    """Raised when a task is not found."""

    def __init__(self, id: UUID) -> None:
        super().__init__(f"Task not found: {id}.")
        self._id = id

    @property
    def id(self) -> UUID:
        return self._id


class InvalidRequestError(ServiceError):
    """Raised when a request is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self._message = message

    @property
    def message(self) -> str:
        return self._message
