from mantis.services.apis.beaver import errors as be, models as bm
from mantis.services.apis.beaver.service import BeaverService
from mantis.services.scheduler.operations.operations.stream import (
    errors as e,
    models as m,
)


class Finder:
    """Utility to find instances."""

    def __init__(self, beaver: BeaverService) -> None:
        self._beaver = beaver

    async def find(self, request: m.FindRequest) -> m.FindResponse:
        """Find an instance."""
        instances_get_request = bm.InstancesGetRequest(
            event_id=request.event, start=request.start, include={"event": True}
        )

        try:
            instances_get_response = await self._beaver.instances.get(
                instances_get_request
            )
        except be.NotFoundError as ex:
            raise e.InstanceNotFoundError(request.event, request.start) from ex

        instance = instances_get_response.instance

        if not isinstance(instance, bm.InstanceWithEvent):
            raise e.OperationError

        return m.FindResponse(instance=instance)
