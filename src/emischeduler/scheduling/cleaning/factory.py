from pyscheduler.protocols import cleaning as c

from emischeduler.scheduling.cleaning.strategies.all import AllCleaningStrategy
from emischeduler.scheduling.cleaning.strategies.day import TimedeltaCleaningStrategy


class CleaningStrategyFactory(c.CleaningStrategyFactory):
    async def create(self, type: str) -> c.CleaningStrategy | None:
        match type:
            case "all":
                return AllCleaningStrategy()
            case "day":
                return TimedeltaCleaningStrategy()
            case _:
                return None
