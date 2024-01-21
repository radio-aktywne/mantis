from pyscheduler.protocols import operation as o

from emischeduler.config.models import Config
from emischeduler.emiarchive.service import EmiarchiveService
from emischeduler.emishows.service import EmishowsService
from emischeduler.emistream.service import EmistreamService
from emischeduler.scheduling.operations.operations.stream import StreamOperation
from emischeduler.scheduling.operations.operations.test import TestOperation


class OperationFactory(o.OperationFactory):
    def __init__(
        self,
        config: Config,
        emiarchive: EmiarchiveService,
        emishows: EmishowsService,
        emistream: EmistreamService,
    ) -> None:
        self._config = config
        self._emiarchive = emiarchive
        self._emishows = emishows
        self._emistream = emistream

    async def create(self, type: str) -> o.Operation | None:
        match type:
            case "test":
                return TestOperation()
            case "stream":
                return StreamOperation(
                    config=self._config,
                    emiarchive=self._emiarchive,
                    emishows=self._emishows,
                    emistream=self._emistream,
                )
            case _:
                return None
