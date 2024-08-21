from pyscheduler.protocols import cleaning as c

from emischeduler.services.scheduler.cleaning.strategies.all import AllCleaningStrategy
from emischeduler.services.scheduler.cleaning.strategies.timedelta import (
    TimedeltaCleaningStrategy,
)


class CleaningStrategyFactory(c.CleaningStrategyFactory):
    async def create(self, type: str) -> c.CleaningStrategy | None:
        match type:
            case "all":
                return AllCleaningStrategy()
            case "timedelta":
                return TimedeltaCleaningStrategy()
            case _:
                return None
