from typing import override

from pyscheduler.models import transfer as t
from pyscheduler.models import types
from pyscheduler.protocols import cleaning as c


class AllCleaningStrategy(c.CleaningStrategy):
    """Cleaning strategy that cleans all tasks."""

    @override
    async def evaluate(
        self, task: t.FinishedTask, parameters: dict[str, types.JSON]
    ) -> bool:
        return True
