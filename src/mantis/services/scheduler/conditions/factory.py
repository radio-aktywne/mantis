from typing import override

from pyscheduler.protocols import condition as c

from mantis.services.scheduler.conditions.conditions.at import AtCondition
from mantis.services.scheduler.conditions.conditions.now import NowCondition


class ConditionFactory(c.ConditionFactory):
    """Factory for creating conditions."""

    @override
    async def create(self, condition_type: str) -> c.Condition | None:
        match condition_type:
            case "now":
                return NowCondition()
            case "at":
                return AtCondition()
            case _:
                return None
