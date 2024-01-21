import asyncio

from pydantic import NaiveDatetime
from pyscheduler.models import types as t
from pyscheduler.protocols import condition as c

from emischeduler.models.base import SerializableModel
from emischeduler.time import naiveutcnow


class Parameters(SerializableModel):
    """Parameters for the at condition."""

    datetime: NaiveDatetime


class AtCondition(c.Condition):
    """Condition that waits until a specific datetime."""

    def _parse_parameters(self, parameters: dict[str, t.JSON]) -> Parameters:
        return Parameters.model_validate(parameters)

    async def wait(self, parameters: dict[str, t.JSON]) -> None:
        params = self._parse_parameters(parameters)

        now = naiveutcnow()
        delta = (params.datetime - now).total_seconds()
        delta = max(delta, 0)

        await asyncio.sleep(delta)
