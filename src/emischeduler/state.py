from litestar.datastructures import State as LitestarState

from emischeduler.config.models import Config
from emischeduler.emiarchive.service import EmiarchiveService
from emischeduler.emishows.service import EmishowsService
from emischeduler.emistream.service import EmistreamService
from emischeduler.scheduling.cleaning.cleaner import Cleaner
from emischeduler.scheduling.scheduler import Scheduler
from emischeduler.scheduling.synchronizer import Synchronizer


class State(LitestarState):
    """Use this class as a type hint for the state of your application.

    Attributes:
        config: Configuration for the application.
        emiarchive: Service for emiarchive.
        emishows: Service for emishows API.
        emistream: Service for emistream API.
        scheduler: Scheduler that manages the lifecycle of scheduled tasks.
        cleaner: Cleaner that removes finished tasks from scheduler's state.
        synchronizer: Synchronizer that synchronizes scheduler's tasks with expected ones.
    """

    config: Config
    emiarchive: EmiarchiveService
    emishows: EmishowsService
    emistream: EmistreamService
    scheduler: Scheduler
    cleaner: Cleaner
    synchronizer: Synchronizer
