from pyscheduler import scheduler as s

from mantis.config.models import Config
from mantis.services.beaver.service import BeaverService
from mantis.services.gecko.service import GeckoService
from mantis.services.numbat.service import NumbatService
from mantis.services.octopus.service import OctopusService
from mantis.services.scheduler.cleaning.factory import CleaningStrategyFactory
from mantis.services.scheduler.conditions.factory import ConditionFactory
from mantis.services.scheduler.events import EventFactory
from mantis.services.scheduler.lock import Lock
from mantis.services.scheduler.operations.factory import OperationFactory
from mantis.services.scheduler.queue import Queue
from mantis.services.scheduler.store import Store


class SchedulerService(s.Scheduler):
    """Service to manage the lifecycle of scheduled tasks."""

    def __init__(  # noqa: PLR0913
        self,
        config: Config,
        beaver: BeaverService,
        gecko: GeckoService,
        numbat: NumbatService,
        octopus: OctopusService,
        store: Store,
    ) -> None:
        super().__init__(
            store=store,
            lock=Lock(),
            events=EventFactory(),
            queue=Queue(),
            operations=OperationFactory(
                config=config,
                beaver=beaver,
                gecko=gecko,
                numbat=numbat,
                octopus=octopus,
            ),
            conditions=ConditionFactory(),
            cleaning=CleaningStrategyFactory(),
        )
