from litestar.datastructures import State as LitestarState

from emischeduler.config.models import Config
from emischeduler.services.cleaner.service import CleanerService
from emischeduler.services.datarecords.service import DatarecordsService
from emischeduler.services.emishows.service import EmishowsService
from emischeduler.services.emistream.service import EmistreamService
from emischeduler.services.scheduler.service import SchedulerService
from emischeduler.services.scheduler.store import Store
from emischeduler.services.synchronizer.service import SynchronizerService


class State(LitestarState):
    """Use this class as a type hint for the state of the application."""

    config: Config
    """Configuration for the application."""

    datarecords: DatarecordsService
    """Service for datarecords database."""

    emishows: EmishowsService
    """Service for emishows API."""

    emistream: EmistreamService
    """Service for emistream API."""

    store: Store
    """Store for scheduling state."""

    scheduler: SchedulerService
    """Service to manage the lifecycle of scheduled tasks."""

    cleaner: CleanerService
    """Service to remove finished tasks from scheduler's state."""

    synchronizer: SynchronizerService
    """Service to synchronize scheduled tasks with expected ones."""
