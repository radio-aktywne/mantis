from datetime import timedelta

from pyscheduler.models import transfer as t
from pyscheduler.models import types
from pyscheduler.protocols import cleaning as c

from emischeduler.models.base import SerializableModel
from emischeduler.time import naiveutcnow


class Parameters(SerializableModel):
    """Parameters for the timedelta cleaning strategy."""

    delta: timedelta


class TimedeltaCleaningStrategy(c.CleaningStrategy):
    """Cleaning strategy that cleans tasks after a certain amount of time."""

    def _parse_parameters(self, parameters: dict[str, types.JSON]) -> Parameters:
        return Parameters.model_validate(parameters)

    async def evaluate(
        self, task: t.FinishedTask, parameters: dict[str, types.JSON]
    ) -> bool:
        params = self._parse_parameters(parameters)

        match task:
            case t.CancelledTask(cancelled=cancelled):
                finished = cancelled
            case t.FailedTask(failed=failed):
                finished = failed
            case t.CompletedTask(completed=completed):
                finished = completed
            case _:
                return False

        now = naiveutcnow()
        return (now - finished) > params.delta
