from litestar.datastructures import State as LitestarState

from emischeduler.config.models import Config
from emischeduler.datarecords.service import DatarecordsService
from emischeduler.emishows.service import EmishowsService
from emischeduler.emistream.service import EmistreamService
from emischeduler.scheduling.cleaning.cleaner import Cleaner
from emischeduler.scheduling.scheduler import Scheduler
from emischeduler.scheduling.store import Store
from emischeduler.scheduling.synchronizer import Synchronizer


class State(LitestarState):
    """Use this class as a type hint for the state of your application.

    Attributes:
        config: Configuration for the application.
        datarecords: Service for datarecords database.
        emishows: Service for emishows API.
        emistream: Service for emistream API.
        store: Store for scheduler's state.
        scheduler: Scheduler that manages the lifecycle of scheduled tasks.
        cleaner: Cleaner that removes finished tasks from scheduler's state.
        synchronizer: Synchronizer that synchronizes scheduler's tasks with expected ones.
    """

    config: Config
    datarecords: DatarecordsService
    emishows: EmishowsService
    emistream: EmistreamService
    store: Store
    scheduler: Scheduler
    cleaner: Cleaner
    synchronizer: Synchronizer
