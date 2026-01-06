from typing import override

from pyscheduler.protocols import cleaning as c

from mantis.services.scheduler.cleaning.strategies.all import AllCleaningStrategy
from mantis.services.scheduler.cleaning.strategies.timedelta import (
    TimedeltaCleaningStrategy,
)


class CleaningStrategyFactory(c.CleaningStrategyFactory):
    """Factory for creating cleaning strategies."""

    @override
    async def create(self, strategy_type: str) -> c.CleaningStrategy | None:
        match strategy_type:
            case "all":
                return AllCleaningStrategy()
            case "timedelta":
                return TimedeltaCleaningStrategy()
            case _:
                return None
