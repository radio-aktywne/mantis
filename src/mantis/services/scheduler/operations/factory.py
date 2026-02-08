from typing import override

from pyscheduler.protocols import operation as o

from mantis.config.models import Config
from mantis.services.beaver.service import BeaverService
from mantis.services.gecko.service import GeckoService
from mantis.services.numbat.service import NumbatService
from mantis.services.octopus.service import OctopusService
from mantis.services.scheduler.operations.operations.stream import StreamOperation
from mantis.services.scheduler.operations.operations.test import TestOperation


class OperationFactory(o.OperationFactory):
    """Factory for creating operations."""

    def __init__(
        self,
        config: Config,
        beaver: BeaverService,
        gecko: GeckoService,
        numbat: NumbatService,
        octopus: OctopusService,
    ) -> None:
        self._config = config
        self._beaver = beaver
        self._gecko = gecko
        self._numbat = numbat
        self._octopus = octopus

    @override
    async def create(self, operation_type: str) -> o.Operation | None:
        match operation_type:
            case "test":
                return TestOperation()
            case "stream":
                return StreamOperation(
                    config=self._config,
                    beaver=self._beaver,
                    gecko=self._gecko,
                    numbat=self._numbat,
                    octopus=self._octopus,
                )
            case _:
                return None
