import asyncio
from typing import override

from pyscheduler.models import types as t
from pyscheduler.protocols import condition as c

from mantis.models.base import SerializableModel
from mantis.utils.time import NaiveDatetime, naiveutcnow


class Parameters(SerializableModel):
    """Parameters for the at condition."""

    datetime: NaiveDatetime
    """Datetime in UTC to wait for."""


class AtCondition(c.Condition):
    """Condition that waits until a specific datetime."""

    def _parse_parameters(self, parameters: dict[str, t.JSON]) -> Parameters:
        return Parameters.model_validate(parameters)

    @override
    async def wait(self, parameters: dict[str, t.JSON]) -> None:
        params = self._parse_parameters(parameters)

        now = naiveutcnow()
        delta = (params.datetime - now).total_seconds()
        delta = max(delta, 0)

        await asyncio.sleep(delta)
