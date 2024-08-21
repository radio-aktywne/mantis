from pyscheduler.models import types as t
from pyscheduler.protocols import condition as c


class NowCondition(c.Condition):
    """Condition that does not wait."""

    async def wait(self, parameters: dict[str, t.JSON]) -> None:
        return
