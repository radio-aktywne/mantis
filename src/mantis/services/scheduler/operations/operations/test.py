from pyscheduler.models import types as t
from pyscheduler.protocols import operation as o


class TestOperation(o.Operation):
    """Operation for testing purposes that returns its parameters and dependencies."""

    async def run(
        self, parameters: dict[str, t.JSON], dependencies: dict[str, t.JSON]
    ) -> t.JSON:
        return {
            "parameters": parameters,
            "dependencies": dependencies,
        }
