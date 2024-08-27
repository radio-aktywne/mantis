from abc import ABC, abstractmethod


class Synchronizer(ABC):
    """Base class for synchronizers."""

    @abstractmethod
    async def synchronize(self) -> None:
        """Synchronize tasks."""

        pass
