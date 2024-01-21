import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from importlib import metadata

from litestar import Litestar, Router
from litestar.contrib.pydantic import PydanticPlugin
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from emischeduler.api.routes.router import router
from emischeduler.config.models import Config
from emischeduler.emiarchive.service import EmiarchiveService
from emischeduler.emishows.service import EmishowsService
from emischeduler.emistream.service import EmistreamService
from emischeduler.scheduling.cleaning.cleaner import Cleaner
from emischeduler.scheduling.scheduler import Scheduler
from emischeduler.scheduling.synchronizer import Synchronizer
from emischeduler.state import State


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _get_route_handlers(self) -> list[Router]:
        return [router]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            title="emischeduler app",
            version=metadata.version("emischeduler"),
            description="Emission scheduling 📅",
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            prefer_alias=True,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_pydantic_plugin(),
        ]

    def _build_emiarchive(self) -> EmiarchiveService:
        return EmiarchiveService(config=self._config.emiarchive)

    def _build_emishows(self) -> EmishowsService:
        return EmishowsService(config=self._config.emishows)

    def _build_emistream(self) -> EmistreamService:
        return EmistreamService(config=self._config.emistream)

    def _build_scheduler(
        self,
        emiarchive: EmiarchiveService,
        emishows: EmishowsService,
        emistream: EmistreamService,
    ) -> Scheduler:
        return Scheduler(
            config=self._config,
            emiarchive=emiarchive,
            emishows=emishows,
            emistream=emistream,
        )

    def _build_cleaner(self, scheduler: Scheduler) -> Cleaner:
        return Cleaner(config=self._config.cleaner, scheduler=scheduler)

    def _build_synchronizer(
        self, emishows: EmishowsService, scheduler: Scheduler
    ) -> Synchronizer:
        return Synchronizer(
            config=self._config.synchronizer, emishows=emishows, scheduler=scheduler
        )

    def _build_initial_state(self) -> State:
        emiarchive = self._build_emiarchive()
        emishows = self._build_emishows()
        emistream = self._build_emistream()
        scheduler = self._build_scheduler(emiarchive, emishows, emistream)
        cleaner = self._build_cleaner(scheduler)
        synchronizer = self._build_synchronizer(emishows, scheduler)

        return State(
            {
                "config": self._config,
                "emiarchive": emiarchive,
                "emishows": emishows,
                "emistream": emistream,
                "scheduler": scheduler,
                "cleaner": cleaner,
                "synchronizer": synchronizer,
            }
        )

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None, None]:
        logger = logging.getLogger("httpx")
        disabled = logger.disabled
        logger.disabled = True

        try:
            yield
        finally:
            logger.disabled = disabled

    @asynccontextmanager
    async def _scheduler_lifespan(self, app: Litestar) -> AsyncGenerator[None, None]:
        state: State = app.state

        async with state.scheduler.run():
            yield

    @asynccontextmanager
    async def _cleaner_lifespan(self, app: Litestar) -> AsyncGenerator[None, None]:
        state: State = app.state

        async with state.cleaner.run():
            yield

    @asynccontextmanager
    async def _synchronizer_lifespan(self, app: Litestar) -> AsyncGenerator[None, None]:
        state: State = app.state

        async with state.synchronizer.run():
            yield

    def _build_lifespan(
        self,
    ) -> list[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            self._suppress_httpx_logging_lifespan,
            self._scheduler_lifespan,
            self._cleaner_lifespan,
            self._synchronizer_lifespan,
        ]

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
            lifespan=self._build_lifespan(),
            debug=True,
        )
