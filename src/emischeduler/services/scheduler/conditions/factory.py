from pyscheduler.protocols import condition as c

from emischeduler.services.scheduler.conditions.conditions.at import AtCondition
from emischeduler.services.scheduler.conditions.conditions.now import NowCondition


class ConditionFactory(c.ConditionFactory):
    async def create(self, type: str) -> c.Condition | None:
        match type:
            case "now":
                return NowCondition()
            case "at":
                return AtCondition()
            case _:
                return None
