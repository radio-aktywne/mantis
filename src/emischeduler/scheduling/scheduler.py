from pyscheduler import scheduler as s

from emischeduler.config.models import Config
from emischeduler.emiarchive.service import EmiarchiveService
from emischeduler.emishows.service import EmishowsService
from emischeduler.emistream.service import EmistreamService
from emischeduler.scheduling.cleaning.factory import CleaningStrategyFactory
from emischeduler.scheduling.conditions.factory import ConditionFactory
from emischeduler.scheduling.events import EventFactory
from emischeduler.scheduling.lock import Lock
from emischeduler.scheduling.operations.factory import OperationFactory
from emischeduler.scheduling.queue import Queue
from emischeduler.scheduling.store import Store


class Scheduler(s.Scheduler):
    def __init__(
        self,
        config: Config,
        emiarchive: EmiarchiveService,
        emishows: EmishowsService,
        emistream: EmistreamService,
    ) -> None:
        super().__init__(
            store=Store(),
            lock=Lock(),
            events=EventFactory(),
            queue=Queue(),
            operations=OperationFactory(config, emiarchive, emishows, emistream),
            conditions=ConditionFactory(),
            cleaning=CleaningStrategyFactory(),
        )
