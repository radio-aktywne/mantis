from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from mantis.api.lifespans import (
    CleanerLifespan,
    SchedulerLifespan,
    StoreLifespan,
    SuppressHTTPXLoggingLifespan,
    SynchronizerLifespan,
    TestLifespan,
)
from mantis.api.openapi import OpenAPIConfigBuilder
from mantis.api.plugins.pydantic import PydanticPlugin
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

    def _build_lifespan(
        self,
    ) -> Sequence[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            TestLifespan,
            SuppressHTTPXLoggingLifespan,
            StoreLifespan,
            SchedulerLifespan,
            CleanerLifespan,
            SynchronizerLifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfigBuilder().build()

    def _build_plugins(self) -> Sequence[PluginProtocol]:
        return [
            ChannelsPlugin(backend=MemoryChannelsBackend(), channels=["events"]),
            PydanticPlugin(),
        ]

    def _build_initial_state(self) -> State:
        beaver = BeaverService(config=self._config.beaver)
        gecko = GeckoService(config=self._config.gecko)
        numbat = NumbatService(config=self._config.numbat)
        octopus = OctopusService(config=self._config.octopus)

        store = Store(config=self._config.store)
        scheduler = SchedulerService(
            config=self._config,
            beaver=beaver,
            gecko=gecko,
            numbat=numbat,
            octopus=octopus,
            store=store,
        )
        cleaner = CleanerService(config=self._config.cleaner, scheduler=scheduler)
        synchronizer = SynchronizerService(
            config=self._config.synchronizer, beaver=beaver, scheduler=scheduler
        )

        return State(
            {
                "config": self._config,
                "store": store,
                "scheduler": scheduler,
                "cleaner": cleaner,
                "synchronizer": synchronizer,
            }
        )

    def build(self) -> Litestar:
        """Build the app."""
        return Litestar(
            route_handlers=[router],
            debug=self._config.debug,
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
