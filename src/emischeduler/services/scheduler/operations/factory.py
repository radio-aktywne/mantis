from pyscheduler.protocols import operation as o

from emischeduler.config.models import Config
from emischeduler.services.emilounge.service import EmiloungeService
from emischeduler.services.emirecords.service import EmirecordsService
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream.service import EmistreamService
from emischeduler.services.scheduler.operations.operations.stream import (
    StreamOperation,
)
from emischeduler.services.scheduler.operations.operations.test import TestOperation


class OperationFactory(o.OperationFactory):
    def __init__(
        self,
        config: Config,
        emilounge: EmiloungeService,
        emirecords: EmirecordsService,
        emishows: EmishowsService,
        emistream: EmistreamService,
    ) -> None:
        self._config = config
        self._emilounge = emilounge
        self._emirecords = emirecords
        self._emishows = emishows
        self._emistream = emistream

    async def create(self, type: str) -> o.Operation | None:
        match type:
            case "test":
                return TestOperation()
            case "stream":
                return StreamOperation(
                    config=self._config,
                    emilounge=self._emilounge,
                    emirecords=self._emirecords,
                    emishows=self._emishows,
                    emistream=self._emistream,
                )
            case _:
                return None
