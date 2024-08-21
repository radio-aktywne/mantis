from pyscheduler import scheduler as s

from emischeduler.config.models import Config
from emischeduler.services.datarecords.service import DatarecordsService
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream.service import EmistreamService
from emischeduler.services.scheduler.cleaning.factory import CleaningStrategyFactory
from emischeduler.services.scheduler.conditions.factory import ConditionFactory
from emischeduler.services.scheduler.events import EventFactory
from emischeduler.services.scheduler.lock import Lock
from emischeduler.services.scheduler.operations.factory import OperationFactory
from emischeduler.services.scheduler.queue import Queue
from emischeduler.services.scheduler.store import Store


class SchedulerService(s.Scheduler):
    """Service to manage the lifecycle of scheduled tasks."""

    def __init__(
        self,
        config: Config,
        datarecords: DatarecordsService,
        emishows: EmishowsService,
        emistream: EmistreamService,
        store: Store,
    ) -> None:
        super().__init__(
            store=store,
            lock=Lock(),
            events=EventFactory(),
            queue=Queue(),
            operations=OperationFactory(config, datarecords, emishows, emistream),
            conditions=ConditionFactory(),
            cleaning=CleaningStrategyFactory(),
        )
