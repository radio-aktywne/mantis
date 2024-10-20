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
from emischeduler.services.cleaner.service import CleanerService
from emischeduler.services.emilounge.service import EmiloungeService
from emischeduler.services.emirecords.service import EmirecordsService
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream.service import EmistreamService
from emischeduler.services.scheduler.service import SchedulerService
from emischeduler.services.scheduler.store import Store
from emischeduler.services.synchronizer.service import SynchronizerService
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

    def _get_debug(self) -> bool:
        return self._config.debug

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None]:
        logger = logging.getLogger("httpx")
        disabled = logger.disabled
        logger.disabled = True

        try:
            yield
        finally:
            logger.disabled = disabled

    @asynccontextmanager
    async def _store_lifespan(self, app: Litestar) -> AsyncGenerator[None]:
        state: State = app.state

        async with state.store:
            yield

    @asynccontextmanager
    async def _scheduler_lifespan(self, app: Litestar) -> AsyncGenerator[None]:
        state: State = app.state

        async with state.scheduler.run():
            yield

    @asynccontextmanager
    async def _cleaner_lifespan(self, app: Litestar) -> AsyncGenerator[None]:
        state: State = app.state

        async with state.cleaner.run():
            yield

    @asynccontextmanager
    async def _synchronizer_lifespan(self, app: Litestar) -> AsyncGenerator[None]:
        state: State = app.state

        async with state.synchronizer.run():
            yield

    def _build_lifespan(
        self,
    ) -> list[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            self._suppress_httpx_logging_lifespan,
            self._store_lifespan,
            self._scheduler_lifespan,
            self._cleaner_lifespan,
            self._synchronizer_lifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            # Title of the service
            title="emischeduler",
            # Version of the service
            version=metadata.version("emischeduler"),
            # Description of the service
            summary="Broadcast scheduling 📅",
            # Use handler docstrings as operation descriptions
            use_handler_docstrings=True,
            # Endpoint to serve the OpenAPI docs from
            path="/schema",
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            # Use aliases for serialization
            prefer_alias=True,
            # Allow type coercion
            validate_strict=False,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_pydantic_plugin(),
        ]

    def _build_emilounge(self) -> EmiloungeService:
        return EmiloungeService(
            config=self._config.emilounge,
        )

    def _build_emirecords(self) -> EmirecordsService:
        return EmirecordsService(
            config=self._config.emirecords,
        )

    def _build_emishows(self) -> EmishowsService:
        return EmishowsService(
            config=self._config.emishows,
        )

    def _build_emistream(self) -> EmistreamService:
        return EmistreamService(
            config=self._config.emistream,
        )

    def _build_store(self) -> Store:
        return Store(
            config=self._config.store,
        )

    def _build_scheduler(
        self,
        emilounge: EmiloungeService,
        emirecords: EmirecordsService,
        emishows: EmishowsService,
        emistream: EmistreamService,
        store: Store,
    ) -> SchedulerService:
        return SchedulerService(
            config=self._config,
            emilounge=emilounge,
            emirecords=emirecords,
            emishows=emishows,
            emistream=emistream,
            store=store,
        )

    def _build_cleaner(self, scheduler: SchedulerService) -> CleanerService:
        return CleanerService(
            config=self._config.cleaner,
            scheduler=scheduler,
        )

    def _build_synchronizer(
        self, emishows: EmishowsService, scheduler: SchedulerService
    ) -> SynchronizerService:
        return SynchronizerService(
            config=self._config.synchronizer,
            emishows=emishows,
            scheduler=scheduler,
        )

    def _build_initial_state(self) -> State:
        emilounge = self._build_emilounge()
        emirecords = self._build_emirecords()
        emishows = self._build_emishows()
        emistream = self._build_emistream()

        config = self._config
        store = self._build_store()
        scheduler = self._build_scheduler(
            emilounge, emirecords, emishows, emistream, store
        )
        cleaner = self._build_cleaner(scheduler)
        synchronizer = self._build_synchronizer(emishows, scheduler)

        return State(
            {
                "config": config,
                "store": store,
                "scheduler": scheduler,
                "cleaner": cleaner,
                "synchronizer": synchronizer,
            }
        )

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            debug=self._get_debug(),
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
