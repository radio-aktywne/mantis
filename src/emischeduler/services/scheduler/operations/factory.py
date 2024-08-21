from pyscheduler.protocols import operation as o

from emischeduler.config.models import Config
from emischeduler.services.datarecords.service import DatarecordsService
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
        datarecords: DatarecordsService,
        emishows: EmishowsService,
        emistream: EmistreamService,
    ) -> None:
        self._config = config
        self._datarecords = datarecords
        self._emishows = emishows
        self._emistream = emistream

    async def create(self, type: str) -> o.Operation | None:
        match type:
            case "test":
                return TestOperation()
            case "stream":
                return StreamOperation(
                    config=self._config,
                    datarecords=self._datarecords,
                    emishows=self._emishows,
                    emistream=self._emistream,
                )
            case _:
                return None
