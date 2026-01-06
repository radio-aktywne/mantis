from litestar.datastructures import State as LitestarState

from mantis.config.models import Config
from mantis.services.cleaner.service import CleanerService
from mantis.services.scheduler.service import SchedulerService
from mantis.services.scheduler.store import Store
from mantis.services.synchronizer.service import SynchronizerService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    cleaner: CleanerService
    """Service to remove finished tasks from scheduler's state."""

    config: Config
    """Configuration for the service."""

    scheduler: SchedulerService
    """Service to manage the lifecycle of scheduled tasks."""

    store: Store
    """Store for scheduling state."""

    synchronizer: SynchronizerService
    """Service to synchronize scheduled tasks with expected ones."""
