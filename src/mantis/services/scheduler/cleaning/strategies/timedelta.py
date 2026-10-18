from datetime import timedelta
from typing import override

from pyscheduler.models import transfer as t, types
from pyscheduler.protocols import cleaning as c

from mantis.models.base import SerializableModel
from mantis.utils.time import awareutcnow


class Parameters(SerializableModel):
    """Parameters for the timedelta cleaning strategy."""

    delta: timedelta
    """Time delta after which the task should be cleaned."""


class TimedeltaCleaningStrategy(c.CleaningStrategy):
    """Cleaning strategy that cleans tasks after a certain amount of time."""

    @override
    async def evaluate(
        self, task: t.FinishedTask, parameters: dict[str, types.JSON]
    ) -> bool:
        params = Parameters.model_validate(parameters)

        match task:
            case t.CancelledTask(cancelled=cancelled):
                finished = cancelled
            case t.FailedTask(failed=failed):
                finished = failed
            case t.CompletedTask(completed=completed):
                finished = completed
            case _:
                return False

        now = awareutcnow()
        return (now - finished) > params.delta
