class ServiceError(Exception):
    """Base class for mediatunes errors."""

    pass


class NotFoundError(ServiceError):
    """Raised when an object is not found."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Object not found: {name}.")
