import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from importlib import metadata

from litestar import Litestar, Router
from litestar.contrib.pydantic import PydanticPlugin
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from mantis.api.routes.router import router
from mantis.config.models import Config
from mantis.services.beaver.service import BeaverService
from mantis.services.cleaner.service import CleanerService
from mantis.services.gecko.service import GeckoService
from mantis.services.numbat.service import NumbatService
from mantis.services.octopus.service import OctopusService
from mantis.services.scheduler.service import SchedulerService
from mantis.services.scheduler.store import Store
from mantis.services.synchronizer.service import SynchronizerService
from mantis.state import State


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
            title="mantis",
            # Version of the service
            version=metadata.version("mantis"),
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

    def _build_beaver(self) -> BeaverService:
        return BeaverService(
            config=self._config.beaver,
        )

    def _build_gecko(self) -> GeckoService:
        return GeckoService(
            config=self._config.gecko,
        )

    def _build_numbat(self) -> NumbatService:
        return NumbatService(
            config=self._config.numbat,
        )

    def _build_octopus(self) -> OctopusService:
        return OctopusService(
            config=self._config.octopus,
        )

    def _build_store(self) -> Store:
        return Store(
            config=self._config.store,
        )

    def _build_scheduler(
        self,
        beaver: BeaverService,
        gecko: GeckoService,
        numbat: NumbatService,
        octopus: OctopusService,
        store: Store,
    ) -> SchedulerService:
        return SchedulerService(
            config=self._config,
            beaver=beaver,
            gecko=gecko,
            numbat=numbat,
            octopus=octopus,
            store=store,
        )

    def _build_cleaner(self, scheduler: SchedulerService) -> CleanerService:
        return CleanerService(
            config=self._config.cleaner,
            scheduler=scheduler,
        )

    def _build_synchronizer(
        self, beaver: BeaverService, scheduler: SchedulerService
    ) -> SynchronizerService:
        return SynchronizerService(
            config=self._config.synchronizer,
            beaver=beaver,
            scheduler=scheduler,
        )

    def _build_initial_state(self) -> State:
        beaver = self._build_beaver()
        gecko = self._build_gecko()
        numbat = self._build_numbat()
        octopus = self._build_octopus()

        config = self._config
        store = self._build_store()
        scheduler = self._build_scheduler(beaver, gecko, numbat, octopus, store)
        cleaner = self._build_cleaner(scheduler)
        synchronizer = self._build_synchronizer(beaver, scheduler)

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
