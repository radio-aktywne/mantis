import logging
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import cast, override

from litestar import Litestar

from mantis.state import State


class Lifespan(AbstractAsyncContextManager):
    """Base class for lifespans."""

    def __init__(self, app: Litestar) -> None:
        self.app = app

    @property
    def state(self) -> State:
        """App state."""
        return cast("State", self.app.state)


class TestLifespan(Lifespan):
    """Lifespan for testing purposes."""

    @override
    async def __aenter__(self) -> None:
        return

    @override
    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return


class SuppressHTTPXLoggingLifespan(Lifespan):
    """Lifespan that suppresses httpx logging."""

    @property
    def logger(self) -> logging.Logger:
        """Httpx logger."""
        return logging.getLogger("httpx")

    @override
    async def __aenter__(self) -> None:
        self.previously_disabled = self.logger.disabled
        self.logger.disabled = True

    @override
    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.logger.disabled = self.previously_disabled


class StoreLifespan(Lifespan):
    """Lifespan for store."""

    @override
    async def __aenter__(self) -> None:
        await self.state.store.__aenter__()

    @override
    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.state.store.__aexit__(exception_type, exception, traceback)


class SchedulerLifespan(Lifespan):
    """Lifespan for scheduler."""

    @override
    async def __aenter__(self) -> None:
        self.context = self.state.scheduler.run()
        await self.context.__aenter__()

    @override
    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.context.__aexit__(exception_type, exception, traceback)


class CleanerLifespan(Lifespan):
    """Lifespan for cleaner."""

    @override
    async def __aenter__(self) -> None:
        self.context = self.state.cleaner.run()
        await self.context.__aenter__()

    @override
    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.context.__aexit__(exception_type, exception, traceback)


class SynchronizerLifespan(Lifespan):
    """Lifespan for synchronizer."""

    @override
    async def __aenter__(self) -> None:
        self.context = self.state.synchronizer.run()
        await self.context.__aenter__()

    @override
    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.context.__aexit__(exception_type, exception, traceback)
